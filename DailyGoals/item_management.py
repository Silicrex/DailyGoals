import dict_management
import date_logic


# Base core dict functions need to take (items), which is a dict of {database, dictionary, command, mode, parameters}
# Return False = abort, return True = sort and save

# Adding items ------------------------------------------------------------------------------------------
def add_mode(items):
    # ex input: daily add
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 0):
        return False

    command = items['command']  # Command to identify if different add type
    dictionary = items['dictionary']

    if command in {'counter', 'cycle'}:
        special_add_function = globals()['add_' + command + '_mode']  # ie add_cycle_mode, gets corresponding func
        if not special_add_function(items['database'], dictionary):
            return False
        return True

    objective_name = get_objective_name()
    if objective_name in dictionary:
        print('Objective by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    denominator = get_denominator()
    dictionary.update({objective_name: {'task_string': task_string, 'denominator': denominator, 'numerator': 0}})
    return True


def add_cycle_mode(database, dictionary):
    objective_name = get_objective_name()
    if objective_name in dictionary:
        print('Objective by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    denominator = get_denominator()

    print('Enter a frequency (every x days) or a week day name', end='\n\n')
    input_frequency = input().lower()
    print()  # Newline
    # Going by day name automatically fills day frequency and offset
    if input_frequency in {'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'}:  # Week day
        current_week_day = database['week_day']  # Current day
        input_week_day = date_logic.convert_day(input_frequency)
        cycle_frequency = 7  # If a day is specified, it's weekly
        current_offset = input_week_day - current_week_day  # Diff between given day and today

    elif input_frequency.isnumeric():  # A number was given, not specific day
        cycle_frequency = eval(input_frequency)
        if cycle_frequency == 0:
            print('Item frequency cannot be 0. Returning to menu', end='\n\n')
            return False

        print('Enter offset until next occurrence (ie 0 if today, 1 if tomorrow)', end='\n\n')
        current_offset = eval(input())

    else:  # Neither a weekday nor number were given
        print('Invalid input. Expected day name or day offset integer. Returning to menu.', end='\n\n')
        return False

    dictionary.update({objective_name: {'task_string': task_string, 'denominator': denominator,
                                        'numerator': 0, 'cycle_frequency': cycle_frequency,
                                        'current_offset': current_offset}})
    return True


def add_counter_mode(_, dictionary):  # Takes (database, dictionary), doesn't need database
    objective_name = get_objective_name()
    if objective_name in dictionary:
        print('Counter by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    dictionary.update({objective_name: {'task_string': task_string, 'numerator': 0}})
    return True


def add_note_mode(database, user_input):
    pass


def get_objective_name():
    while True:
        print('Enter a name for the objective (must be unique, no spaces)')
        print()  # Extra newline
        objective_name = input().strip()  # Get input and remove leading/trailing spaces
        print()  # Extra newline
        if not objective_name:
            print('Objective name cannot be blank')
            continue
        if len(objective_name.split()) > 1:  # If there are spaces
            print('Please do not use spaces')
            continue
        if not objective_name.isascii():
            print('Please only use ASCII characters')
            continue
        return objective_name


def get_task_string():
    while True:
        print('Enter a brief task description/couple keywords '
              '(looks like: goal_name (task string), can be blank)', end='\n\n')
        task_string = input()

        if not task_string:  # If it's empty, that's fine, but print something to signify
            print('Task string skipped')

        print()  # Extra newline
        if not task_string.isascii():
            print('Please only use ASCII characters')
            continue
        return task_string


def get_denominator():
    while True:
        print('Enter a progress denominator (ie 2 becomes 0/2) (blank defaults to 1)')
        print()  # Extra newline
        denominator = input()
        print()  # Extra newline
        if not denominator:
            print('Progress denominator cannot be blank')
            continue
        if not denominator.isnumeric():
            print('Progress denominator must be a positive integer')
            continue
        denominator = eval(denominator)
        if denominator <= 0:
            print('Progress quantity must be greater than 0')
            continue
        return denominator


# Updating/editing items ------------------------------------------------------------------------------------------
def update_mode(items):
    # ex input: daily update wanikani 50
    # ex input: daily update wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1, 2):
        return False

    command = items['command']  # Cycle handled differently
    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']
    objective_name = parameters[0]

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    if parameter_length == 1:  # Default to 1 if no specific value given
        update_value = 1
    else:  # parameter_length == 2
        update_value = parameters[1]
        try:
            update_value = eval(update_value)
        except (SyntaxError, NameError):
            print('Update value must be a number', end='\n\n')
            return False
        if not isinstance(update_value, int):
            print('Update value must be an integer', end='\n\n')
            return False

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    dictionary[objective_name]['numerator'] += update_value
    return True


def set_mode(items):
    # ex input: daily set wanikani 50
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 2):
        return False

    command = items['command']  # Cycle handled differently
    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']
    objective_name = parameters[0]
    set_value = parameters[1]

    try:
        set_value = eval(set_value)
    except (SyntaxError, NameError):
        print('Set value must be a number', end='\n\n')
        return False
    if not isinstance(set_value, int):
        print('Set value must be an integer', end='\n\n')
        return False

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False

    dictionary[objective_name]['numerator'] = set_value
    return True


def complete_mode(items):
    # ex input: daily complete wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    command = items['command']
    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']
    objective_name = parameters[0]

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False
        
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    value = dictionary[objective_name]
    # If numerator < denominator
    if value['numerator'] < value['denominator']:
        # Then make it 100%
        value['numerator'] = value['denominator']
    else:
        print('That objective is already marked as at least 100% complete')
        return False
    return True


def reset_mode(items):
    # ex input: daily reset wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    command = items['command']
    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']
    objective_name = parameters[0]

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False
        
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    value = dictionary[objective_name]
    if value['numerator'] != 0:
        value['numerator'] = 0
    else:
        print('That item already has no progress')
        return False
    return True


def setall_mode(items):
    # ex input: daily setall complete
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    command = items['command']

    if command in {'counter', 'cycle'}:
        special_add_function = globals()['setall_' + command + '_mode']  # ie setall_cycle_mode, gets corresponding func
        if not special_add_function(items):
            return False
        return True

    dictionary = items['dictionary']
    parameters = items['parameters']
    setall_value = parameters[0]

    if setall_value not in {'complete', 'reset'}:
        print('Invalid parameter. Expected "complete" or "reset"', end='\n\n')
        return False

    if not dictionary:
        print('That dictionary is empty', end='\n\n')
        return False
    
    if setall_value == 'complete':
        for key, value in dictionary.items():
            # Set the numerator to the denominator (100%). value is the key's dictionary value
            value['numerator'] = value['denominator']
    elif setall_value == 'reset':
        for key, value in dictionary.items():
            value['numerator'] = 0
    return True


def setall_cycle_mode(items):
    database = items['database']
    cycle_dict = items['dictionary']
    active_cycle_list = dict_management.get_active_cycle_list(database)
    parameters = items['parameters']
    setall_value = parameters[0]

    if setall_value not in {'complete', 'reset'}:
        print('Invalid parameter. Expected "complete" or "reset"', end='\n\n')
        return False

    if not active_cycle_list:
        print('There are no active cycle objectives', end='\n\n')
        return False

    if setall_value == 'complete':
        for objective in active_cycle_list:
            # Set the numerator to the denominator (100%). value is the key's dictionary value
            value = cycle_dict[objective]
            value['numerator'] = value['denominator']
    elif setall_value == 'reset':
        for objective in active_cycle_list:
            value = cycle_dict[objective]
            value['numerator'] = 0
    return True


def setall_counter_mode(items):
    counter_dict = items['dictionary']
    parameters = items['parameters']
    setall_value = parameters[0]

    try:
        setall_value = eval(setall_value)
    except (SyntaxError, NameError):
        print('Setall value must be a number', end='\n\n')
        return False
    if not isinstance(setall_value, int):
        print('Setall value must be an integer', end='\n\n')
        return False

    if not counter_dict:
        print('There are no counters', end='\n\n')
        return False

    while True:
        print(f'Change ALL counters to a value of {setall_value}? (y/n)', end='\n\n')
        user_response = input().lower()
        if user_response == 'y':
            break
        elif user_response == 'n':
            return False

    for counter in counter_dict:
        counter_dict[counter]['numerator'] = setall_value
    return True


def rename_mode(items):
    # ex input: daily rename wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']

    objective_name = parameters[0]
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    new_name = get_objective_name()
    if new_name in dictionary:
        print('That name is already in use', end='\n\n')
        return False
    dictionary[new_name] = dictionary[objective_name]
    dictionary.pop(objective_name)
    return True


def retask_mode(items):
    # ex input: daily retask wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']

    objective_name = parameters[0]
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    new_task_string = get_task_string()
    dictionary[objective_name]['task_string'] = new_task_string
    return True


def denominator_mode(items):
    # ex input: daily denominator wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']

    objective_name = parameters[0]
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    new_denominator = get_denominator()
    dictionary[objective_name]['denominator'] = new_denominator
    return True


# Removing items ------------------------------------------------------------------------------------------
def remove_mode(items):
    # ex input: daily remove wanikani
    parameter_length = len(items['parameters'])
    if dict_management.wrong_parameter_count(parameter_length, 1):
        return False

    database = items['database']
    dictionary = items['dictionary']
    parameters = items['parameters']

    objective_name = parameters[0]
    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    dictionary.pop(objective_name)
    return True
