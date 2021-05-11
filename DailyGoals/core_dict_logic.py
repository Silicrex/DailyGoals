def get_display_list(database):
    settings = database['settings']
    toggle_list = {'daily': settings['daily_toggle'], 'todo': settings['todo_toggle'],
                   'cycle': settings['cycle_toggle'], 'longterm': settings['longterm_toggle'],
                   'counter': settings['counter_toggle']}
    return [x for x in toggle_list if toggle_list[x]]


def name_to_dict(database, dict_name):
    if dict_name == 'daily':
        return database['daily_objectives']
    elif dict_name == 'todo':
        return database['todo_objectives']
    elif dict_name == 'cycle':
        return database['cycle_objectives']
    elif dict_name == 'longterm':
        return database['longterm_objectives']
    elif dict_name == 'counter':
        return database['counter_dict']


def add_item_base(dictionary, objective_name, add_items):
    if objective_name in dictionary:
        print('Objective exists already')
        return False

    if not (task_string := get_task()):  # Enter blank string = cancel
        return False

    # Get the progress denominator
    print('Enter a progress goal value (ie 2 becomes 0/2) (blank defaults to 1)')
    progress_denominator = input()
    if progress_denominator:  # If it's not blank
        progress_denominator = eval(progress_denominator)
        if progress_denominator <= 0:
            print('Progress quantity must be greater than 0\n'
                  'Returning to menu')
            return False
    else:
        progress_denominator = 1

    add_items.append(task_string)
    add_items.append(progress_denominator)
    return True


def add_item(database, dictionary, objective_name, command):
    add_items = []  # Will be filled unless add_item_base returns False, [task_string, progress_denominator]
    if not add_item_base(dictionary, objective_name, add_items):
        return False
    task_string, progress_denominator = add_items

    dictionary.update({objective_name: [task_string, progress_denominator, 0]})  # 0 is the numerator
    sort_dictionary(database, command)
    print(f"Added '{objective_name}'")
    return True


def update_item(dictionary, objective_name, add_value):
    add_value = eval(add_value)
    dictionary[objective_name][2] += add_value  # Add to numerator
    return True


def complete_item(dictionary, objective_name):
    if dictionary[objective_name][2] < dictionary[objective_name][1]:  # If numerator < denominator
        dictionary[objective_name][2] = dictionary[objective_name][1]  # Make it x/x
        return True
    else:
        print('That objective is already marked as at least 100% complete')
        return False


def reset_item(dictionary, objective_name):
    # value = [task_string, progress_denominator, progress numerator]
    if dictionary[objective_name][2] != 0:
        dictionary[objective_name][2] = 0
        return True
    else:
        print('That objective is already marked as 0% complete')
        return False


def remove_item(dictionary, objective_name):
    dictionary.pop(objective_name)
    print(f'Removed {objective_name}')
    return True


def rename_item(database, dictionary, objective_name, new_name, command):
    if new_name in dictionary:
        print('That name is already in use')
        return False
    dictionary[new_name] = dictionary[objective_name]
    dictionary.pop(objective_name)
    sort_dictionary(database, command)
    return True


def retask_item(dictionary, objective_name):
    if not (task_string := get_task()):  # Enter blank string = cancel
        return False
    dictionary[objective_name][0] = task_string
    print('Successfully changed the task text')
    return True


def change_denominator(dictionary, objective_name, new_denominator):
    if new_denominator <= 0:
        print('Denominator must be greater than 0. Returning to menu')
        return False

    dictionary[objective_name][1] = new_denominator
    return True


def dict_setall(dictionary, setall_value):
    if setall_value not in {'complete', 'reset'}:
        print('Invalid 1st parameter. Expected "complete" or "reset"')
        return False
    # daily/longterm/to-do value = [task_string, progress_denominator, progress numerator]
    # cycle value = [task_string, denominator, numerator, cycle length, current offset]
    if setall_value == 'complete':
        for key, value in dictionary.items():
            value[2] = value[1]  # Set the numerator to the denominator
        print('Set all given objectives to 100%')
    elif setall_value == 'reset':
        for key, value in dictionary.items():
            value[2] = 0
        print('Set all given objectives to 0%')
    return True


def get_task():
    while True:
        print('Please enter a brief description/couple keywords. Leave blank and enter to cancel')
        task_string = input()
        if not task_string.isascii():
            print('Please only use ASCII characters')
            continue
        break
    return task_string


def change_all_dailies(database, mode):
    while True:
        print('Set all to-do, active cycle, and daily objectives to ', end='')
        if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
            print('complete', end='')
        elif mode == 'reset':
            print('0%', end='')
        print('? (y/n)')
        user_input = input().lower()
        if user_input == 'y':
            break
        elif user_input == 'n':
            return False
    # daily/to-do value = [task_string, progress_denominator, progress numerator]
    # cycle value = [task_string, denominator, numerator, cycle length, current offset]

    daily_dictionaries = (database['daily_objectives'], database['todo_objectives'],
                          database['active_cycle_objectives'])
    if mode == 'complete':
        for dictionary in daily_dictionaries:
            for key, value in dictionary.items():
                value[2] = value[1]
    elif mode == 'reset':
        for dictionary in daily_dictionaries:
            for key, value in dictionary.items():
                value[2] = 0
    return True


def clear_dictionary(database, mode):
    daily_objectives = database['daily_objectives']
    optional_objectives = database['optional_objectives']
    todo_objectives = database['todo_objectives']
    inactive_cycle_objectives = database['inactive_cycle_objectives']
    active_cycle_objectives = database['active_cycle_objectives']
    longterm_objectives = database['longterm_objectives']
    counter_dict = database['counter_dict']

    if mode == 'all':
        total_objectives = len(daily_objectives) + len(optional_objectives) + len(todo_objectives)\
                           + len(inactive_cycle_objectives) + len(active_cycle_objectives)\
                           + len(longterm_objectives) + len(counter_dict)

        if not total_objectives:  # If there are none
            print('There are no objectives to delete')
            return False

        while True:
            print(f"Are you sure you'd like to remove ALL objectives"
                  f"from EACH category ({total_objectives})? (y/n)")
            user_input = input().lower()
            if user_input in {'y', 'n'}:
                break
        if user_input == 'n':
            return False  # Return to menu

        daily_objectives.clear()
        optional_objectives.clear()
        todo_objectives.clear()
        inactive_cycle_objectives.clear()
        active_cycle_objectives.clear()
        longterm_objectives.clear()
        counter_dict.clear()
        print('Removed all objectives')

    else:
        if mode == 'daily':
            total_objectives = len(daily_objectives)
        elif mode == 'optional':
            total_objectives = len(optional_objectives)
        elif mode == 'todo':
            total_objectives = len(todo_objectives)
        elif mode == 'cycle':
            total_objectives = len(inactive_cycle_objectives) + len(active_cycle_objectives)
        elif mode == 'longterm':
            total_objectives = len(longterm_objectives)
        else:  # mode == 'counter'
            total_objectives = len(counter_dict)

        if not total_objectives:  # If there are none
            print('There are no objectives to delete')
            return False

        while True:
            print(f"Are you sure you'd like to remove all {mode} objectives ({total_objectives})? (y/n)")
            user_input = input().lower()
            if user_input in {'y', 'n'}:
                break
        if user_input == 'n':
            return False  # Return to menu

    if mode == 'daily':
        daily_objectives.clear()
    elif mode == 'optional':
        optional_objectives.clear()
    elif mode == 'todo':
        todo_objectives.clear()
    elif mode == 'cycle':
        inactive_cycle_objectives.clear()
        active_cycle_objectives.clear()
    elif mode == 'longterm':
        longterm_objectives.clear()
    else:  # mode == 'counter'
        counter_dict.clear()
    print(f'Removed all {mode} objectives')


def get_active_cycle_dict(database):
    # cycle value = [task_string, denominator, numerator, cycle length, current offset]
    active_cycle_objectives = []
    for key, value in database['cycle_objectives'].items():
        if value[4] == 0:
            active_cycle_objectives.append(key)
        else:  # Sorted for 0's to be on top
            break
    return active_cycle_objectives


def get_inactive_cycle_dict(database):
    # cycle value = [task_string, denominator, numerator, cycle length, current offset]
    cycle_dict_copy = database['cycle_objectives'].copy()
    for key, value in cycle_dict_copy.copy():
        if value[4] == 0:
            inactive_cycle_objectives.append(key)
        else:  # Sorted for 0's to be on top
            break
    return inactive_cycle_objectives


def sort_dictionary(database, command):
    if command == 'daily':
        dictionary_name = 'daily_objectives'
    elif command == 'optional':
        dictionary_name = 'optional_objectives'
    elif command == 'todo':
        dictionary_name = 'todo_objectives'
    elif command == 'cycle':
        sort_cycle_dictionary(database)
        return
    elif command == 'longterm':
        dictionary_name = 'longterm_objectives'
    else:  # command == 'counter'
        dictionary_name = 'counter_dict'

    temp_list = sorted(list(database[dictionary_name].items()))
    database[dictionary_name] = dict(temp_list)


def sort_cycle_dictionary(database):
    temp_list = list(database['cycle_objectives'].items())
    temp_list = sorted(temp_list, key=lambda obj: (obj[1][1], obj[0]))
    database['cycle_objectives'] = dict(temp_list)
