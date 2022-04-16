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
        return get_active_cycle_list(database)
    elif name == 'inactive_cycle':
        return get_inactive_cycle_list(database)
    elif name == 'enforced_todo':
        return get_enforced_dailies_list(database)
    elif name == 'unenforced_todo':
        return get_unenforced_cycle_list(database)
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


def wrong_parameter_count(parameter_length, *expected):
    # Convert to list of len # instead of parameter #'s. List for pop() and list comprehension convenience
    expected = list(expected)
    if parameter_length not in expected:  # -1 so it's by parameter count instead of by length
        print(f'Invalid amount of parameters (expected {expected.pop(0)}', end='')  # Pop to check for more
        if expected:  # If there are more term numbers left after popping the first one
            for value in expected:
                print(' or', value, end='')  # Print 'or x' for them all
        print(')', end='\n\n')  # Print the close-parenthesis and extra newline
        return True  # Return True, as in to say there were a wrong # of terms
    return False  # Else return False, as in not wrong #


def change_all_daily_dicts(database, mode):
    daily_container_names = documentation.get_daily_container_names()
    daily_dict_item_length = 0
    for dict_name in daily_container_names:
        daily_dict_item_length += len(name_to_container(database, dict_name))
    if daily_dict_item_length == 0:
        print('There are no active daily objectives', end='\n\n')
        return

    # Get confirmation
    if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
        if not console_display.confirm('Set all daily-enforced objectives to complete? (y/n)'):
            return
    elif mode == 'reset':
        if not console_display.confirm('Set all daily-enforced objectives to 0%? (y/n)'):
            return

    if mode == 'complete':
        for dict_name in daily_container_names[:-2]:  # Exclude last two, enforced_todo and active_cycles (lists)
            dictionary = name_to_container(database, dict_name)
            for key, value in dictionary.items():
                # Set the numerator to the denominator (100%). value is the key's dictionary value
                value['numerator'] = value['denominator']
            sort_dictionary(database, dict_name)
        enforced_todos =  name_to_container(database, 'enforced_todo')
        todo_dict = database['todo']
        active_cycles = name_to_container(database, 'active_cycle')
        cycle_dict = database['cycle']
        for key in enforced_todos:
            value = todo_dict[key]
            value['numerator'] = value['denominator']
        sort_dictionary(database, 'todo')
        for key in active_cycles:
            value = cycle_dict[key]
            value['numerator'] = value['denominator']
        sort_dictionary(database, 'cycle')

    elif mode == 'reset':
        for dict_name in daily_container_names[:-2]: # Exclude last two, enforced_todo and active_cycles (lists)
            dictionary = name_to_container(database, dict_name)
            for key, value in dictionary.items():
                value['numerator'] = 0
            sort_dictionary(database, dict_name)
        enforced_todos = name_to_container(database, 'enforced_todo')
        todo_dict = database['todo']
        active_cycles = name_to_container(database, 'active_cycle')
        cycle_dict = database['cycle']
        for key in enforced_todos:
            value = todo_dict[key]
            value['numerator'] = 0
        sort_dictionary(database, 'todo')
        for key in active_cycles:
            value = cycle_dict[key]
            value['numerator'] = 0
        sort_dictionary(database, 'cycle')

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
        dictionary = name_to_container(database, mode)
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


def get_enforced_dailies_list(database):
    enforced_dailies_list = []
    for key, value in database['todo'].items():
        if value['enforced_daily']:
            enforced_dailies_list.append(key)
        else:  # Sorted for all enforced to-do's to be first, so once you encounter one that's not, that's the end
            break
    return enforced_dailies_list


def get_unenforced_cycle_list(database):
    todo_keys = list(database['todo'].keys())
    enforced_list = get_enforced_dailies_list(database)
    for key in enforced_list:  # Remove enforced keys to get unenforced keys
        todo_keys.remove(key)
    return todo_keys


def get_active_cycle_list(database):
    active_cycle_list = []
    for key, value in database['cycle'].items():
        if value['current_offset'] == 0:
            active_cycle_list.append(key)
        else:  # Sorted for 0's to be on top, so once you exit the 0 range, it's all 1+
            break
    return active_cycle_list


def get_inactive_cycle_list(database):
    cycle_objective_keys = list(database['cycle'].keys())
    active_cycle_list = get_active_cycle_list(database)
    for key in active_cycle_list:
        cycle_objective_keys.remove(key)
    return cycle_objective_keys  # Remove active keys to get inactive keys


def sort_dictionary(database, command):
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
        # enforced_daily -> completed or not -> name
        return not obj[1]['enforced_daily'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]

    def alpha_sort(obj):
        return obj[0]  # Just by the name

    dictionary = name_to_container(database, command)
    temp_list = list(dictionary.items())  # ie: [(name, {dict_elements}])

    if command == 'cycle':
        temp_list = sorted(temp_list, key=cycle_sort)
    elif command == 'counter':
        temp_list = sorted(temp_list, key=alpha_sort)
    elif command == 'todo':
        temp_list = sorted(temp_list, key=todo_sort)
    else:
        temp_list = sorted(temp_list, key=completion_then_alpha_sort)

    database[command] = dict(temp_list)  # Assignment via method to preserve object
