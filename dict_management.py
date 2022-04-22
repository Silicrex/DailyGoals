import file_management
import console_display
import documentation


def get_display_list(database):
    settings = database['settings']
    toggle_list = {'daily': settings['daily'], 'optional': settings['optional'],
                   'todo': settings['todo'], 'active_cycle': settings['cycle'],
                   'inactive_cycle': settings['full_cycle'], 'longterm': settings['longterm'],
                   'counter': settings['counter'], 'note': settings['note']}
    return [x for x in toggle_list if toggle_list[x] and name_to_container(database, x)]
    # Add toggle to list if the toggle is on and if the corresponding container isn't empty


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


def complete_item(database, context, objective_name):
    command = context['command']
    dictionary = context['dictionary']
    objective = dictionary[objective_name]
    if objective['numerator'] < objective['denominator']:
        current_value = objective['numerator']
        objective['numerator'] = objective['denominator']

        # Handle link
        if command == 'daily' and 'link' in objective:
            difference = objective['denominator'] - current_value
            linked_objective_name = dictionary[objective_name]['link']
            database['todo'][linked_objective_name]['numerator'] += difference


def reset_item(database, context, objective_name):
    command = context['command']
    dictionary = context['dictionary']
    objective = dictionary[objective_name]
    if objective['numerator'] != 0:
        current_value = objective['numerator']
        objective['numerator'] = 0

        # Handle link
        if command == 'daily' and 'link' in objective:
            difference = 0 - current_value
            linked_objective_name = dictionary[objective_name]['link']
            database['todo'][linked_objective_name]['numerator'] += difference


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
        context['dictionary'] = dictionary = name_to_container(database, dict_name)
        for key in dictionary:
            if mode == 'complete':
                complete_item(database, context, key)
            else:
                reset_item(database, context, key)
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
        if not console_display.confirm(f"Are you sure you'd like to delete ALL objectives "
                                       f"({total_objectives_to_remove})? (y/n)"):
            console_display.print_display(database)
            print('Cancelled', end='\n\n')
            return False
        for dictionary in dict_list:
            dictionary.clear()
        return True

    else:  # Specified dictionary
        dictionary = database[mode]
        total_objectives_to_remove = len(dictionary)
        if not total_objectives_to_remove:  # If there are none
            print('That container has no items', end='\n\n')
            return False
        if not console_display.confirm(f"Are you sure you'd like to delete ALL {mode} items"
                                       f" ({total_objectives_to_remove})? (y/n)"):
            console_display.print_display(database)
            print('Cancelled', end='\n\n')
            return False
        dictionary.clear()
        return True


def get_enforced_todo_dict(database):
    todo_dict = database['todo']
    return [x for x in todo_dict if todo_dict[x]['enforced_todo']]


def get_unenforced_todo_dict(database):
    todo_dict = database['todo']
    return [x for x in todo_dict if not todo_dict[x]['enforced_todo']]


def get_active_cycle_dict(database):
    cycle_dict = database['cycle']
    return [cycle_dict[x] for x in cycle_dict if cycle_dict[x]['current_offset'] == 0]


def get_inactive_cycle_dict(database):
    cycle_dict = database['cycle']
    return [cycle_dict[x] for x in cycle_dict if cycle_dict[x]['current_offset'] != 0]


def sort_dictionary(database, dict_name):
    def completion_then_alpha_sort(obj):
        # obj[1] refers to dictionary value in tuple (obj_name, dict value)
        # False sorts before True in ascending. a sorts before z. Sorts incomplete to top, then alphabetically.
        # (completion bool, name)
        return obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

    def cycle_sort(obj):
        # (current offset, completion bool, name)
        # 0 sorts before 1, False before True, a before z. Sorts by offset, then completion bool, then name
        return obj[1]['current_offset'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

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

    database[dict_name] = dict(temp_list)  # Assignment via method to preserve object
