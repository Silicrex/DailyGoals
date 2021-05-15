def get_dictionary_list(database):
    dictionary_list = [database['daily_objectives'], database['optional_objectives'], database['todo_objectives'],
                       database['inactive_cycle_objectives'], database['active_cycle_objectives'],
                       database['longterm_objectives'], database['counter_dict']]
    return dictionary_list


def get_display_list(database):
    settings = database['settings']
    toggle_list = {'daily': settings['daily_toggle'], 'todo': settings['todo_toggle'],
                   'cycle': settings['cycle_toggle'], 'longterm': settings['longterm_toggle'],
                   'counter': settings['counter_toggle']}
    return [x for x in toggle_list if toggle_list[x]]


def name_to_dict(database, dict_name):
    if dict_name == 'daily':
        return database['daily_objectives']
    elif dict_name == 'optional':
        return database['optional_objectives']
    elif dict_name == 'todo':
        return database['todo_objectives']
    elif dict_name == 'cycle':
        return database['cycle_objectives']
    elif dict_name == 'longterm':
        return database['longterm_objectives']
    elif dict_name == 'counter':
        return database['counter_dict']


def mode_to_dict_name(mode):
    if mode == 'daily':
        return 'daily_objectives'
    elif mode == 'optional':
        return 'optional_objectives'
    elif mode == 'todo':
        return 'todo_objectives'
    elif mode == 'cycle':
        return 'cycle_objectives'
    elif mode == 'longterm':
        return 'longterm_objectives'
    elif mode == 'counter':
        return 'counter_dict'


def dict_setall(dictionary, setall_value):
    if setall_value not in {'complete', 'reset'}:
        print('Invalid 1st parameter. Expected "complete" or "reset"')
        return False
    if setall_value == 'complete':
        for key, value in dictionary.items():
            # Set the numerator to the denominator (100%). value is the key's dictionary value
            value['progress_numerator'] = value['progress_denominator']
        print('Set all given objectives to 100%')
    elif setall_value == 'reset':
        for key, value in dictionary.items():
            value['progress_numerator'] = 0
        print('Set all given objectives to 0%')
    return True


def change_all_dailies(database, mode):
    while True:
        if mode == 'complete':  # If 'complete', print 'complete', else print '0%' for 'reset'
            print('Set all daily, to-do, and active cycle objectives to complete? (y/n)')
        elif mode == 'reset':
            print('Set all daily, to-do, and active cycle objectives to 0%? (y/n)')
        user_input = input().lower()
        if user_input == 'y':
            break
        elif user_input == 'n':
            return False

    daily_dictionaries = (name_to_dict(database, 'daily'), name_to_dict(database, 'todo'),
                          get_active_cycle_list(database))
    cycle_objectives = database['cycle_objectives']
    if mode == 'complete':
        for dictionary in daily_dictionaries[:-1]:  # Splice because cycles needs to be handled differently
            for key, value in dictionary.items():
                # value is the key's dictionary value
                value['progress_numerator'] = value['progress_denominator']
        for key in daily_dictionaries[-1]:
            value = cycle_objectives[key]
            value['progress_numerator'] = value['progress_denominator']
    elif mode == 'reset':
        for dictionary in daily_dictionaries[:-1]:  # Splice because cycles needs to be handled differently
            for key, value in dictionary.items():
                # value is the key's dictionary value
                value['progress_numerator'] = 0
        for key in daily_dictionaries[-1]:
            value = cycle_objectives[key]
            value['progress_numerator'] = 0
    return True


def delete_dictionary(database, mode):
    def get_confirmation():
        while True:
            print(f"Are you sure you'd like to remove all {mode} objectives ({total_objectives_removed})? (y/n)")
            user_response = input().lower()
            if user_response in {'y', 'n'}:
                break
        if user_response == 'n':
            return False  # Return to menu
        else:
            return True

    if mode == 'all':
        dictionary_list = get_dictionary_list(database)

        total_objectives_removed = 0
        for dictionary in dictionary_list:
            total_objectives_removed += len(dictionary)

        if not total_objectives_removed:  # If there are none
            print('There are no objectives to delete')
            return False

        if not get_confirmation():
            return False

        for dictionary in dictionary_list:
            dictionary.clear()
        print('Removed all objectives')
        return True

    else:  # Specific dictionary
        dictionary = name_to_dict(database, mode)
        total_objectives_removed = len(dictionary)

        if not total_objectives_removed:  # If there are none
            print('There are no objectives to delete')
            return False

        if not get_confirmation():
            return False

        dictionary.clear()
        print(f'Removed all {mode} objectives')


def get_active_cycle_list(database):
    active_cycle_list = []
    for key, value in database['cycle_objectives'].items():
        if value['current_offset'] == 0:
            active_cycle_list.append(key)
        else:  # Sorted for 0's to be on top, so once you exit the 0 range, it's all 1+
            break
    return active_cycle_list


def get_inactive_cycle_list(database):
    cycle_objective_keys = database['cycle_objectives'].keys()
    active_cycle_list = get_active_cycle_list(database)
    for key in active_cycle_list:
        cycle_objective_keys.remove(key)
    return cycle_objective_keys  # Remove active keys to get inactive keys


def sort_dictionary(database, mode):
    def normal_sort(obj):
        # (completion bool, name)
        # False sorts before True in ascending. a sorts before z. Sorts incomplete to top, then alphabetically.
        return obj[1]['progress_numerator'] >= obj[1]['progress denominator'], obj[0]

    if mode == 'cycle':
        sort_cycle_dictionary(database)  # Handled differently
        return

    dictionary = name_to_dict(database, mode)
    temp_list = list(dictionary.items())  # ie: [(name, {dict_elements}])
    temp_list = sorted(temp_list, key=normal_sort)
    database[mode_to_dict_name(mode)] = dict(temp_list)  # Assignment via method to preserve object


def sort_cycle_dictionary(database):
    def cycle_sort(obj):
        # (current offset, completion bool, name)
        # 0 sorts before 1, False before True, a before z. Sorts by offset, then completion bool, then name
        return obj[1]['current_offset'], obj[1]['progress_numerator'] >= obj[1]['progress denominator'], obj[0]

    temp_list = list(database['cycle_objectives'].items())  # ie: [(name, {dict_elements}])
    temp_list = sorted(temp_list, key=cycle_sort)
    database['cycle_objectives'] = dict(temp_list)
