import file_management
import console_display
import documentation
import date_logic


def get_display_list(database):
    settings = database['settings']
    toggle_list = {'daily': settings['daily'], 'todo': settings['todo'], 'cycle': settings['cycle'],
                   'longterm': settings['longterm'], 'counter': settings['counter'], 'note': settings['note']}
    return [x for x in toggle_list if toggle_list[x]]
    # Add toggle to list if the toggle is on


def name_to_container(database, name):
    if name == 'active_cycle':
        return get_active_cycle_dict(database)
    elif name == 'inactive_cycle':
        return get_inactive_cycle_dict(database)
    elif name == 'enforced_todo':
        return get_enforced_todo_dict(database)
    elif name == 'unenforced_todo':
        return get_unenforced_todo_dict(database)
    else:
        return database[name]


def key_search(database, dictionary, input_string, *, force_manual_match=False):
    """Take an input string and find a dict key resembling it.
    Key must itself be a dict and have the value 'display_name'

    :param dict database:
    :param dict dictionary: Dictionary to search in
    :param str input_string: Input string to try matching
    :param bool force_manual_match: Override setting and force manual matching instead of auto matching.
    :return str | bool: Returns found key str, else False.
    """
    # Search by in, then startswith, then substring
    if input_string in dictionary:  # If the search term is a key, just return it back
        return input_string
    auto_match = database['settings']['auto_match'] if not force_manual_match else False  # Bool
    keys = list(dictionary.keys())
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


def update_item(database, dict_name, objective_name, update_value):
    dictionary = database[dict_name]
    objective = dictionary[objective_name]
    objective['numerator'] += update_value

    # If counter, check if history values need updating
    if dict_name == 'counter' and objective['history_name']:
        new_value = objective['numerator']
        history_key = objective['history_name'].lower()
        history_value = database['history']['counter'][history_key]
        if new_value > history_value['highest_value']:
            history_value['highest_value'] = new_value
        elif new_value < history_value['lowest_value']:
            history_value['lowest_value'] = new_value

    # Handle link
    linked_to = objective['link']['linked_to']
    if linked_to:
        linked_dict_name = linked_to[0]
        linked_dict = database[linked_dict_name]
        linked_objective_name = linked_to[1]
        assert linked_objective_name in linked_dict  # Shouldn't be possible to return false
        update_item(database, linked_dict_name, linked_objective_name, update_value)


def complete_item(database, dict_name, objective_name):
    dictionary = database[dict_name]
    objective = dictionary[objective_name]
    current_value = objective['numerator']
    difference = objective['denominator'] - current_value  # Used to make handling links easier
    if difference <= 0:  # Should not be decreasing anything
        console_display.refresh_and_print(database, 'Item is already marked as complete!')
        return
    update_item(database, dict_name, objective_name, difference)


def reset_item(database, dict_name, objective_name):
    dictionary = database[dict_name]
    objective = dictionary[objective_name]
    current_value = objective['numerator']
    difference = 0 - current_value  # Used to make handling links easier
    if difference == 0:
        console_display.refresh_and_print(database, 'Item already has no progress!')
        return
    update_item(database, dict_name, objective_name, difference)


def remove_item(database, dict_name, objective_name):
    dictionary = database[dict_name]
    objective = dictionary[objective_name]
    linked_to = objective['link']['linked_to']
    linked_from = objective['link']['linked_from']

    # Handle links
    if linked_to:  # Remove from linked item's linked_from
        remove_from_linked_from(database, dict_name, objective_name)
    if linked_from:  # If any objectives link to this one, remove it from their linked_to
        remove_from_linked_to(database, dict_name, objective_name)

    # Handle containers
    remove_from_container(database, dict_name, objective_name)

    dictionary.pop(objective_name)


def get_daily_count(database):
    enforced_containers = [name_to_container(database, name) for name in documentation.get_enforced_dict_names()]
    lengths = map(lambda x: len(x), enforced_containers)
    return sum(lengths)


def check_streak(database):
    enforced_containers = [name_to_container(database, name) for name in documentation.get_enforced_dict_names()]
    for container in enforced_containers:
        for key, value in container.items():
            if value['numerator'] < value['denominator']:
                return False
    return True


# History ------------------------------------------------------------------------------------------

def add_to_history(database, dict_name, obj_value):
    def apply_tag(history_val):
        history_val['tags'].update({date_string: obj_value['tag']})
        obj_value['tag'] = None

    history_dict = database['history'][dict_name]  # Corresponding history dict
    history_name = obj_value['history_name']
    date = database['settings']['calendar_date'].copy()
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


def create_counter_history(database, history_name):
    database['history']['counter'].update({
        history_name.lower(): {
            'display_name': history_name,
            'highest_value': 0,
            'lowest_value': 0,
            'tags': {}
        }})


# Links ------------------------------------------------------------------------------------------

def test_link_chain(database, origin, new_link):
    """Gets a list of the link sequence produced if given objectives are linked.

    :param database:
    :param list origin: Starting point [dict_name, objective_name]
    :param list new_link: Proposed new link [dict_name, objective_name]
    :return: List of lists [dict_name, obj_name] in order of the link sequence. If link is circular, chain ends with
    origin being reached again
    """
    chain = [origin, new_link]
    to_dict, to_obj = new_link
    while True:
        # linked_to = [type_string, linked_objective_name]
        foreign_linked_to = database[to_dict][to_obj]['link']['linked_to']
        if not foreign_linked_to:  # Dead end, not circular
            return chain
        chain.append(foreign_linked_to)
        if foreign_linked_to == origin:  # Ends up back at the start; is circular
            return chain
        # Check link of the link until you either hit a dead end (non-circular) or end up back at the start (circular)
        to_dict, to_obj = foreign_linked_to


def get_link_chain(database, dict_name, objective_name):
    chain = [[dict_name, objective_name]]  # Start with origin, then append in order
    while True:
        # linked_to = [type_string, linked_objective_name]
        linked_to = database[dict_name][objective_name]['link']['linked_to']
        if not linked_to:  # Reached the end
            return chain
        chain.append(linked_to)  # It is linked, append that link to the chain
        dict_name, objective_name = linked_to  # Move down a link


def format_link_chain(link_chain):
    # ex: (Daily) wanikani -> (Optional) Extra work
    return ' -> '.join([f'({x[0].capitalize()}) {x[1]}' for x in link_chain])


def remove_from_linked_to(database, dict_name, objective_name, *, rename_value=False):
    """For a given objective with a link, remove it from the linked_to section of the objectives which link to it

    :param database:
    :param dict_name: Dict name of the objective being removed
    :param objective_name: Name of the objective being removed
    :param rename_value: (Optional) Instead of deleting, rename objective name to this value in link's data
    :return: None
    """
    linked_from = database[dict_name][objective_name]['link']['linked_from']
    for pair in linked_from:  # pair = [linked_dict_name, linked_objective_name]
        if rename_value:
            pair[1] = rename_value
        else:
            database[pair[0]][pair[1]]['link']['linked_to'] = []


def remove_from_linked_from(database, dict_name, objective_name, *, rename_value=False):
    """For a given objective with a link, remove it from the linked_from section of the objective it links to

    :param database:
    :param dict_name: Dict name of the objective being removed
    :param objective_name: Name of the objective being removed
    :param rename_value: (Optional) Instead of deleting, rename objective name to this value in link's data
    :return:
    """
    linked_to = database[dict_name][objective_name]['link']['linked_to']
    foreign_linked_from = database[linked_to[0]][linked_to[1]]['link']['linked_from']
    for pair in foreign_linked_from:
        if pair == [dict_name, objective_name]:
            if rename_value:
                pair[1] = rename_value
            else:
                foreign_linked_from.remove(pair)
            break


# Containers ------------------------------------------------------------------------------------------

def add_to_container(database, dict_name, objective_key, container_name='_default'):
    database['containers'][dict_name][container_name]['items'].append(objective_key)


def find_current_container(command_containers, objective_key):
    for container_name, container_value in command_containers.items():
        if objective_key in container_value['items']:
            return container_name


def move_to_container(database, dict_name, objective_key, destination_name):
    command_containers = database['containers'][dict_name]
    current_container = find_current_container(command_containers, objective_key)
    if current_container == destination_name:
        console_display.refresh_and_print(database, 'Item is already in that container!')
        return
    command_containers[destination_name]['items'].append(objective_key)
    command_containers[current_container]['items'].remove(objective_key)


def remove_from_container(database, dict_name, objective_key):
    command_containers = database['containers'][dict_name]
    current_container = find_current_container(command_containers, objective_key)
    command_containers[current_container]['items'].remove(objective_key)


# ------------------------------------------------------------------------------------------

def change_all_daily_dicts(database, context, mode):
    enforced_dictionary_names = documentation.get_enforced_dict_names()
    enforced_dict_total_items = 0
    for dict_name in enforced_dictionary_names:
        enforced_dict_total_items += len(name_to_container(database, dict_name))
    if enforced_dict_total_items == 0:
        console_display.refresh_and_print(database, 'There are no active daily objectives')
        return

    # Get confirmation
    if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
        if not console_display.confirm('Set all daily-enforced objectives to complete? (y/n)'):
            return
    elif mode == 'reset':
        if not console_display.confirm('Set all daily-enforced objectives to 0%? (y/n)'):
            return
    
    for dict_name in enforced_dictionary_names:
        context['command'] = dict_name
        dictionary = name_to_container(database, dict_name)
        for key in dictionary:
            if mode == 'complete':
                complete_item(database, dict_name, key)
            else:
                reset_item(database, dict_name, key)
        sort_dictionary(database, dict_name)

    file_management.update(database)
    console_display.print_display(database)
    print('Dictionaries successfully updated', end='\n\n')


def delete_dictionary(database, mode):
    if mode == 'all':
        dict_list = documentation.get_dictionary_list(database)
        total_objectives_to_remove = 0
        for dict_name in dict_list:
            total_objectives_to_remove += len(dict_name)
        if not total_objectives_to_remove:  # If there are none
            print('There are no objectives to delete', end='\n\n')
            return False
        if not console_display.confirm(f"> Are you sure you'd like to delete ALL objectives/notes "
                                       f"({total_objectives_to_remove})? (y/n)"):
            console_display.refresh_and_print(database, 'Cancelled')
            return False
        for dictionary in dict_list:
            dictionary.clear()
        return True

    else:  # Specified dictionary
        dictionary = database[mode]
        total_objectives_to_remove = len(dictionary)
        if not total_objectives_to_remove:  # If there are none
            console_display.refresh_and_print(database, 'That container has no items')
            return False
        if not console_display.confirm(f"> Are you sure you'd like to delete ALL {mode} items"
                                       f" ({total_objectives_to_remove})? (y/n)"):
            console_display.refresh_and_print(database, 'Cancelled')
            return False
        for objective_name in dictionary:
            remove_item(database, mode, objective_name)
        return True


def get_enforced_todo_dict(database):
    todo_dict = database['todo']
    return {k: todo_dict[k] for k in todo_dict if todo_dict[k]['enforced_todo']}


def get_unenforced_todo_dict(database):
    todo_dict = database['todo']
    return {k: todo_dict[k] for k in todo_dict if not todo_dict[k]['enforced_todo']}


def get_active_cycle_dict(database):
    cycle_dict = database['cycle']
    return {k: cycle_dict[k] for k in cycle_dict if cycle_dict[k]['remaining_cooldown'] == 0}


def get_inactive_cycle_dict(database):
    cycle_dict = database['cycle']
    return {k: cycle_dict[k] for k in cycle_dict if cycle_dict[k]['remaining_cooldown'] != 0}


def sort_dictionary(database, dict_name):
    def completion_then_alpha_sort(obj):
        # obj[1] refers to dictionary value in tuple (obj_name, dict value)
        # False sorts before True in ascending. a sorts before z. Sorts incomplete to top, then alphabetically.
        # (completion bool, name)
        return obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

    def cycle_sort(obj):
        # (current offset, completion bool, name)
        # 0 sorts before 1, False before True, a before z. Sorts by offset, then completion bool, then name
        return obj[1]['remaining_cooldown'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

    def todo_sort(obj):
        # Puts enforced daily to-do objectives on top (False sorts before True, so invert with not)
        # enforced_todo -> completed or not -> name
        return not obj[1]['enforced_todo'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

    def alpha_sort(obj):
        return obj[0]  # Just by the name

    if dict_name == 'active_cycle':  # Since active_cycle is a subset, not a full dict, sort the real full one
        dictionary = database['cycle']
        dict_name = 'cycle'
    elif dict_name == 'enforced_todo':
        dictionary = database['todo']
        dict_name = 'todo'
    else:
        dictionary = database[dict_name]

    temp_list = list(dictionary.items())  # ie: [(name, {dict_elements}])

    if dict_name == 'cycle':
        temp_list = sorted(temp_list, key=cycle_sort)
    elif dict_name == 'counter':
        temp_list = sorted(temp_list, key=alpha_sort)
    elif dict_name == 'todo':
        temp_list = sorted(temp_list, key=todo_sort)
    else:
        temp_list = sorted(temp_list, key=completion_then_alpha_sort)

    database[dict_name] = dict(temp_list)  # Assignment via index to preserve object


def roll_over_index(n, length):
    if n < length - 1:  # Is n less than the last index?
        return n + 1
    else:
        return 0
