import file_management
import item_management
import console_display
import documentation


def get_display_list(database):
    settings = database['settings']
    toggle_list = {'daily': settings['daily'], 'optional': settings['optional'],
                   'todo': settings['todo'], 'active_cycle': settings['cycle'],
                   'inactive_cycle': settings['full_cycle'], 'longterm': settings['longterm'],
                   'counter': settings['counter'], 'note': settings['note']}
    return [x for x in toggle_list if toggle_list[x] and database[x]]
    # Add toggle to list if the toggle is on and if the corresponding container isn't empty


def name_to_container(database, name):
    if name == 'active_cycle':
        return get_active_cycle_list(database)
    elif name == 'inactive_cycle':
        return get_inactive_cycle_list(database)
    else:
        return database[name]


def objective_search(database, dictionary, input_objective_string):  # Search by startswith then substring
    auto_match = database['settings']['auto_match']
    objective_keys = list(dictionary.keys())
    objective_keys.sort()  # Alphabetize list of keys
    objectives_seen = set()  # Track objectives already seen/suggested
    for objective in objective_keys:  # Search for via startswith()
        if objective.startswith(input_objective_string):

            if auto_match:  # If auto_match, don't ask, just return that
                return objective

            objectives_seen.add(objective)
            print(f"Could not find '{input_objective_string}', but found '{objective}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)')
                user_response = input().lower()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return objective
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    for objective in objective_keys:  # Search for via find()
        if objective not in objectives_seen and objective.find(input_objective_string) != -1:

            if auto_match:  # If auto_match, don't ask, just return that
                return objective

            print(f"Could not find '{input_objective_string}', but found '{objective}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)')
                user_response = input().lower()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return objective
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    print('Could not find objective. Returning to menu')
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
    daily_dictionary_names = documentation.get_daily_dictionary_names()
    daily_dict_item_length = 0
    for dict_name in daily_dictionary_names:
        daily_dict_item_length += len(name_to_container(database, dict_name))
    if daily_dict_item_length == 0:
        print('There are no active daily objectives', end='\n\n')
        return

    # Get confirmation
    while True:
        if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
            print('Set all daily, optional, and active cycle objectives to complete? (y/n)', end='\n\n')
        elif mode == 'reset':
            print('Set all daily, optional, and active cycle objectives to 0%? (y/n)', end='\n\n')
        user_input = input().lower()
        if user_input == 'y':
            break
        elif user_input == 'n':
            return

    if mode == 'complete':
        for dict_name in daily_dictionary_names:
            # Function expects a dictionary with {database, command, dictionary, parameters} (command = dict name)
            items = {
                'database': database,
                'dictionary': name_to_container(database, dict_name),
                'command': dict_name,
                'parameters': ['complete']
            }
            item_management.setall_mode(items)
    elif mode == 'reset':
        for dict_name in daily_dictionary_names:
            # Function expects a dictionary with {command, dictionary, parameters} (command = dict name)
            items = {
                'database': database,
                'dictionary': name_to_container(database, dict_name),
                'command': dict_name,
                'parameters': ['reset']
            }
            item_management.setall_mode(items)

    for dict_name in daily_dictionary_names:
        sort_dictionary(database, dict_name)
    file_management.update(database)
    console_display.print_display(database)
    print('Dictionary successfully updated', end='\n\n')


def delete_dictionary(database, mode):
    def get_confirmation():
        while True:
            if mode == 'all':
                print(f"Are you sure you'd like to delete ALL objectives"
                      f" ({total_objectives_to_remove})? (y/n)", end='\n\n')
            else:
                print(f"Are you sure you'd like to delete ALL {mode} items"
                      f" ({total_objectives_to_remove})? (y/n)", end='\n\n')
            user_response = input().lower()
            if user_response == 'y':
                return True
            elif user_response == 'n':
                return False

    if mode == 'all':
        dict_list = documentation.get_dictionary_list(database)

        total_objectives_to_remove = 0
        for dict_name in dict_list:
            total_objectives_to_remove += len(dict_name)
        if not total_objectives_to_remove:  # If there are none
            print('There are no objectives to delete', end='\n\n')
            return False
        if not get_confirmation():
            console_display.print_display(database)
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
        if not get_confirmation():
            console_display.print_display(database)
            return False
        dictionary.clear()
        return True


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

    def alpha_sort(obj):
        return obj[0]  # Just by the name

    dictionary = name_to_container(database, command)
    temp_list = list(dictionary.items())  # ie: [(name, {dict_elements}])

    if command == 'cycle':
        temp_list = sorted(temp_list, key=cycle_sort)
    elif command == 'counter':
        temp_list = sorted(temp_list, key=alpha_sort)
    else:
        temp_list = sorted(temp_list, key=completion_then_alpha_sort)

    database[command] = dict(temp_list)  # Assignment via method to preserve object
