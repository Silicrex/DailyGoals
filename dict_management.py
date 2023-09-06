import documentation
import date_logic
from console_display import refresh_display, confirm
from database import DB, save


def get_display_list():
    settings = DB['settings']
    toggle_list = {'daily': settings['daily'], 'todo': settings['todo'], 'cycle': settings['cycle'],
                   'longterm': settings['longterm'], 'counter': settings['counter'], 'note': settings['note']}
    return [x for x in toggle_list if toggle_list[x]]
    # Add toggle to list if the toggle is on


def get_container(name):
    if name == 'active_cycle':
        return get_active_cycle()
    elif name == 'inactive_cycle':
        return get_inactive_cycle()
    elif name == 'enforced_todo':
        return get_enforced_todo()
    elif name == 'unenforced_todo':
        return get_unenforced_todo()
    else:
        return DB[name]


def key_search(dictionary, input_string, *, force_manual_match=False, ignore_list=None):
    """Take an input string and find a dict key resembling it.
    Key must itself be a key to another dict which has the element 'display_name'

    :param dict dictionary: Dictionary to search in
    :param str input_string: Input string to try matching
    :param bool force_manual_match: Override setting and force manual matching instead of auto matching.
    :param ignore_list: None or a container of str to ignore in the search
    :return str | bool: Returns found key str, else False.
    """
    # Search by in, then startswith, then substring
    if input_string in dictionary:  # If the search term is a key, just return it back
        return input_string
    auto_match = DB['settings']['auto_match'] if not force_manual_match else False
    keys = list(dictionary.keys())
    if ignore_list:
        for ignore_key in [x for x in ignore_list if x in keys]:
            keys.remove(ignore_key)
    keys.sort()  # Alphabetize list of keys
    keys_seen = set()  # Track keys already suggested
    for key in keys:  # Search for via startswith()
        if key.startswith(input_string):
            if auto_match:  # If auto_match, don't ask, just return that
                return key

            keys_seen.add(key)
            display_name = dictionary[key]['display_name']
            print(f"Could not find '{input_string}', but found '{display_name}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)', end='\n\n')
                user_response = input().lower()
                print()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return key
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    for key in keys:  # Search for via find()
        if key not in keys_seen and key.find(input_string) != -1:
            if auto_match:  # If auto_match, don't ask, just return that
                return key

            display_name = dictionary[key]['display_name']
            print(f"Could not find '{input_string}', but found '{display_name}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)')
                user_response = input().lower()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return key
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    return False


def update_item(dict_name, item_name, update_value, *, chaining=True, depth=1):
    """
    :param dict_name:
    :param item_name:
    :param update_value:
    :param chaining: Used to indicate if a link should trigger a subsequent link
    :param depth: Used to track the update depth for linked updates
    :return: None
    """
    dictionary = DB[dict_name]
    item = dictionary[item_name]
    item['numerator'] += update_value

    # If counter, check if history values need updating
    if dict_name == 'counter' and item['history_name']:
        new_value = item['numerator']
        history_key = item['history_name'].lower()
        history_value = DB['history']['counter'][history_key]
        if new_value > history_value['highest_value']:
            history_value['highest_value'] = new_value
        elif new_value < history_value['lowest_value']:
            history_value['lowest_value'] = new_value

    # Handle link
    link = item['link']
    linked_to = link['linked_to']
    if linked_to and chaining:
        linked_dict_name = linked_to[0]
        linked_dict = DB[linked_dict_name]
        linked_item_name = linked_to[1]
        assert linked_item_name in linked_dict  # Shouldn't be possible to return False
        depth = update_item(linked_dict_name, linked_item_name, update_value,
                            chaining=link['chaining'], depth=depth+1)
    return depth


def complete_item(dict_name, objective_name):
    dictionary = DB[dict_name]
    objective = dictionary[objective_name]
    current_value = objective['numerator']
    difference = objective['denominator'] - current_value  # Used to make handling links easier
    if difference <= 0:  # Should not be decreasing anything
        refresh_display('Item is already marked as complete!')
        return
    update_item(dict_name, objective_name, difference)


def reset_item(dict_name, objective_name):
    dictionary = DB[dict_name]
    objective = dictionary[objective_name]
    current_value = objective['numerator']
    difference = 0 - current_value  # Used to make handling links easier
    if difference == 0:
        refresh_display('Item already has no progress!')
        return
    update_item(dict_name, objective_name, difference)


def remove_item(dict_name, objective_name):
    dictionary = DB[dict_name]
    objective = dictionary[objective_name]
    linked_to = objective['link']['linked_to']
    linked_from = objective['link']['linked_from']

    # Handle links
    if linked_to:  # Remove from linked item's linked_from
        remove_from_linked_from(dict_name, objective_name)
    if linked_from:  # If any objectives link to this one, remove it from their linked_to
        remove_from_linked_to(dict_name, objective_name)

    # Handle groups
    remove_from_groups(dict_name, objective_name)

    dictionary.pop(objective_name)


def get_daily_count():
    enforced_containers = [get_container(name) for name in documentation.get_enforced_dict_names()]
    lengths = map(lambda x: len(x), enforced_containers)
    return sum(lengths)


def check_streak():
    enforced_containers = [get_container(name) for name in documentation.get_enforced_dict_names()]
    for container in enforced_containers:
        for key, value in container.items():
            if value['numerator'] < value['denominator']:
                return False
    return True


# History ------------------------------------------------------------------------------------------

def add_to_history(dict_name, obj_value):
    def apply_tag(history_val):
        history_val['tags'].update({date_string: obj_value['tag']})
        obj_value['tag'] = None

    history_dict = DB['history'][dict_name]  # Corresponding history dict
    history_name = obj_value['history_name']
    date = DB['settings']['calendar_date'].copy()
    date_string = date_logic.string_date(date)
    if not history_name:  # No history tracking for this item
        return
    if dict_name == 'counter':  # Everything else for Counter History is handled elsewhere
        if obj_value['tag']:
            apply_tag(history_dict[history_name.lower()])
        return

    history_key = history_name.lower()

    if history_key not in history_dict:  # Create entry
        if dict_name == 'longterm':
            history_dict.update({
                history_key: {
                    'display_name': history_name,
                    'first_completed': None,
                    'tags': {}
                }})
        else:
            history_dict.update({
                history_key: {
                    'display_name': history_name,
                    'numerator': 0,
                    'times_completed': 0,
                    'first_completed': None,
                    'tags': {}
                }})

    history_value = history_dict[history_key]
    completed = obj_value['numerator'] >= obj_value['denominator']
    if completed and not history_value['first_completed']:
        history_value['first_completed'] = date
    if obj_value['tag']:
        apply_tag(history_value)

    if dict_name == 'longterm':
        return
    elif dict_name == 'todo':
        if completed:
            history_value['numerator'] += obj_value['numerator']
            history_value['times_completed'] += 1
    else:
        history_value['numerator'] += obj_value['numerator']
        if completed:
            history_value['times_completed'] += 1


def create_counter_history(history_name):
    DB['history']['counter'].update({
        history_name.lower(): {
            'display_name': history_name,
            'highest_value': 0,
            'lowest_value': 0,
            'tags': {}
        }})


# Links ------------------------------------------------------------------------------------------

def get_link_chain(origin, next_link):
    """Gets a list of the link sequence produced if given items are linked.

    :param list origin: Starting point [dict_name, item_name, chaining]
    :param list next_link: Proposed new link [dict_name, item_name, chaining]
    :return: List of lists [dict_name, item_name, chaining] in order of the link sequence.
    If link is circular, chain ends with origin being reached again
    """
    chain = [origin]  # Initialize chain list
    prev = origin  # Need to track previous item as chaining is based on its setting
    while True:  # Check link of the link until you either hit a dead end or end up back at the start
        chain.append(next_link)
        chaining = prev[2]
        if not chaining:  # Chaining was disabled, so next_link's link doesn't matter
            break
        elif next_link == origin:  # Ends up back at the start and chaining is on; is circular
            break
        to_dict = next_link[0]
        to_item = next_link[1]
        linked_to = DB[to_dict][to_item]['link']['linked_to']
        if not linked_to:  # There is no further link
            break
        next_chaining = DB[linked_to[0]][linked_to[1]]['link']['chaining']
        prev = next_link
        next_link = [linked_to[0], linked_to[1], next_chaining]  # Switch focus to next link in chain
    return chain


def format_link_chain(link_chain):
    # ex: (Daily) itemname -> (Optional) Extra work
    res = []
    for link in link_chain:
        dict_name, item_name, chaining = link
        if chaining:
            res.append(f'({dict_name.capitalize()}) {item_name}')
        else:
            res.append(f'({dict_name.capitalize()}; no chaining) {item_name}')
    return ' -> '.join(res)


def remove_from_linked_to(dict_name, item_name):
    """For a given item with a link to it, remove it from the linked_to section of the items which link to it

    :param dict_name: Dict name of the item being removed
    :param item_name: Name of the item being removed
    :return: None
    """
    linked_from = DB[dict_name][item_name]['link']['linked_from']
    for pair in linked_from:  # pair = [linked_dict_name, linked_item_name]
        DB[pair[0]][pair[1]]['link']['linked_to'] = []


def rename_linked_to(dict_name, item_name, rename_value):
    """For a given item with a link to it, rename it in the linked_to section of the items which link to it

    :param dict_name: Dict name of the item being renamed
    :param item_name: Name of the item being renamed
    :param rename_value: What it is being renamed to
    :return: None
    """
    linked_from = DB[dict_name][item_name]['link']['linked_from']
    for pair in linked_from:  # pair = [linked_dict_name, linked_item_name]
        DB[pair[0]][pair[1]]['link']['linked_to'][1] = rename_value


def remove_from_linked_from(dict_name, item_name):
    """For a given objective with an outward link, remove it from the linked_from section of the item it links to

    :param dict_name: Dict name of the item being removed
    :param item_name: Name of the item being removed
    :return:
    """
    linked_to = DB[dict_name][item_name]['link']['linked_to']
    foreign_linked_from = DB[linked_to[0]][linked_to[1]]['link']['linked_from']
    foreign_linked_from.remove([dict_name, item_name])


def rename_linked_from(dict_name, item_name, rename_value):
    """For a given objective with an outward link, rename it in the linked_from section of the item it links to

    :param dict_name: Dict name of the item being renamed
    :param item_name: Name of the item being renamed
    :param rename_value: What it is being renamed to
    :return:
    """
    linked_to = DB[dict_name][item_name]['link']['linked_to']
    foreign_linked_from = DB[linked_to[0]][linked_to[1]]['link']['linked_from']
    for pair in foreign_linked_from:
        if pair == [dict_name, item_name]:
            pair[1] = rename_value
            return


# Groups ------------------------------------------------------------------------------------------

def default_group(dict_name, item_key):  # Init into the Groups system
    DB['groups'][dict_name]['_Default']['items'].append(item_key)


def get_group(dict_name, item_key):
    groups = DB['groups'][dict_name]
    for group_name, group_value in groups.items():
        if item_key in group_value['items']:
            return groups[group_name]


def move_to_group(dict_name, item_key, destination_name):
    target = DB['groups'][dict_name][destination_name]
    current = get_group(dict_name, item_key)
    target['items'].append(item_key)
    current['items'].remove(item_key)


def remove_from_groups(dict_name, item_key):
    get_group(dict_name, item_key)['items'].remove(item_key)


# ------------------------------------------------------------------------------------------

def change_all_daily_dicts(context, mode):
    enforced_dictionary_names = documentation.get_enforced_dict_names()
    enforced_dict_total_items = 0
    for dict_name in enforced_dictionary_names:
        enforced_dict_total_items += len(get_container(dict_name))
    if enforced_dict_total_items == 0:
        refresh_display('There are no active daily objectives')
        return

    # Get confirmation
    if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
        if not confirm('Set all daily-enforced objectives to complete? (y/n)'):
            return
    elif mode == 'reset':
        if not confirm('Set all daily-enforced objectives to 0%? (y/n)'):
            return
    
    for dict_name in enforced_dictionary_names:
        context['command'] = dict_name
        dictionary = get_container(dict_name)
        for key in dictionary:
            if mode == 'complete':
                complete_item(dict_name, key)
            else:
                reset_item(dict_name, key)

    save()
    refresh_display('Dictionaries successfully updated')


def delete_dictionary(mode):
    if mode == 'all':
        dict_list = documentation.get_dictionary_list()
        total_objectives_to_remove = 0
        for dict_name in dict_list:
            total_objectives_to_remove += len(dict_name)
        if not total_objectives_to_remove:  # If there are none
            print('There are no objectives to delete', end='\n\n')
            return False
        if not confirm(f"> Are you sure you'd like to delete ALL objectives/notes "
                       f"({total_objectives_to_remove})? (y/n)"):
            refresh_display('Cancelled')
            return False
        for dictionary in dict_list:
            dictionary.clear()
        return True

    else:  # Specified dictionary
        dictionary = DB[mode]
        total_objectives_to_remove = len(dictionary)
        if not total_objectives_to_remove:  # If there are none
            refresh_display('That container has no items')
            return False
        if not confirm(f"> Are you sure you'd like to delete ALL {mode} items ({total_objectives_to_remove})? (y/n)"):
            refresh_display('Cancelled')
            return False
        for objective_name in dictionary:
            remove_item(mode, objective_name)
        return True


def get_enforced_todo():
    todo_dict = DB['todo']
    return {k: todo_dict[k] for k in todo_dict if todo_dict[k]['enforced_todo']}


def get_unenforced_todo():
    todo_dict = DB['todo']
    return {k: todo_dict[k] for k in todo_dict if not todo_dict[k]['enforced_todo']}


def get_active_cycle():
    cycle_dict = DB['cycle']
    return {k: cycle_dict[k] for k in cycle_dict if cycle_dict[k]['remaining_cooldown'] == 0}


def get_inactive_cycle():
    cycle_dict = DB['cycle']
    return {k: cycle_dict[k] for k in cycle_dict if cycle_dict[k]['remaining_cooldown'] != 0}


def sort_dict(dictionary, key):
    temp_list = list(dictionary.items())
    temp_list.sort(key=key)
    return dict(temp_list)


def roll_over_index(n, length):
    if n < length - 1:  # Is n less than the last index?
        return n + 1
    else:
        return 0
