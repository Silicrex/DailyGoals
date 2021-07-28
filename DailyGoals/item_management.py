import dict_management
import date_logic


# Base core dict functions need to take (items), which is a dict of {database, dictionary, command, mode, parameters}
# Return False = abort, return True = sort and save

# Adding items ------------------------------------------------------------------------------------------
def add_mode(database, dictionary, input_info):
    # ex input: daily add
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 0):
        return False

    command = input_info['command']  # Command to identify if different add type

    if command in {'counter', 'cycle'}:
        special_add_function = globals()['add_' + command + '_mode']  # ie add_cycle_mode, gets corresponding func
        if not special_add_function(database, dictionary):
            return False
        return True

    objective_name = get_objective_name()
    objective_name_lower = objective_name.lower()
    if objective_name_lower in dictionary:
        print('Objective by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    denominator = get_denominator()
    dictionary.update({objective_name_lower: {'display_name': objective_name, 'task_string': task_string,
                                              'denominator': denominator, 'numerator': 0}})
    return True


def add_cycle_mode(database, dictionary):
    objective_name = get_objective_name()
    objective_name_lower = objective_name.lower()
    if objective_name_lower in dictionary:
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

    dictionary.update({objective_name_lower: {'display_name': objective_name, 'task_string': task_string,
                                              'denominator': denominator, 'numerator': 0,
                                              'cycle_frequency': cycle_frequency, 'current_offset': current_offset}})
    return True


def add_counter_mode(_, dictionary):  # Takes (database, dictionary), doesn't need database
    objective_name = get_objective_name()
    objective_name_lower = objective_name.lower()
    if objective_name_lower in dictionary:
        print('Counter by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    dictionary.update({objective_name_lower: {'display_name': objective_name, 'task_string': task_string,
                                              'numerator': 0}})
    return True


def add_note_mode(database, user_input):
    # ex input: note add
    # ex input: note add 0
    input_length = len(user_input)
    if dict_management.wrong_parameter_count(input_length, 2, 3):
        return False
    dictionary = database['note']
    note_count = len(dictionary)
    if input_length == 3:
        note_index = user_input[2]
        if not note_index.isnumeric():
            print('Invalid parameter. Index must be a positive integer', end='\n\n')
            return False
        note_index = eval(note_index)
        if note_index > note_count:  # If specified index is higher than list length, bump down to end index
            print('Index adjusted as given value was higher than list length')
            note_index = note_count
    else:
        note_index = note_count  # If no index specified, default to end of list
    while True:
        print(f'Enter note for index [{note_index}]:', end='\n\n')
        note_input = input()  # Lower for string comparisons
        if not note_input:  # It's possible to enter nothing
            continue
        if not note_input.isascii():
            print('Please only use ASCII characters')
            continue
        break
    dictionary.insert(note_index, note_input)
    return True


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
        print('Enter a progress denominator (ie 2 becomes 0/2) (blank defaults to 1)', end='\n\n')
        denominator = input()
        print()  # Extra newline

        if denominator == '':  # Default to 1
            return 1
        if not (denominator := format_integer(denominator)):
            continue
        if denominator < 0:  # Case of 0 is already handled in format_integer()
            print('Denominator must be greater than 0')
            continue
        return denominator


# Updating/editing items ------------------------------------------------------------------------------------------
def update_mode(database, dictionary, input_info, objective_name, update_value='1'):
    # ex input: daily update wanikani 50
    # ex input: daily update wanikani
    parameter_length = input_info['parameter_length']
    if dict_management.wrong_parameter_count(parameter_length, 1, 2):
        return False

    command = input_info['command']  # Cycle handled differently
    objective_name = objective_name.lower()

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    if not (update_value := format_integer(update_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        return False

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    dictionary[objective_name]['numerator'] += update_value
    return True


def set_mode(database, dictionary, input_info, objective_name, set_value):
    # ex input: daily set wanikani 50
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 2):
        return False

    command = input_info['command']  # Cycle handled differently
    objective_name = objective_name.lower()

    if not (set_value := format_integer(set_value)):  # Enforces non-zero integer. Accepts extension ie 1k
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


def complete_mode(database, dictionary, input_info, objective_name):
    # ex input: daily complete wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    command = input_info['command']
    objective_name = objective_name.lower()

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


def reset_mode(database, dictionary, input_info, objective_name):
    # ex input: daily reset wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    command = input_info['command']
    objective_name = objective_name.lower()

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


def setall_mode(database, dictionary, input_info, setall_value):
    # ex input: daily setall complete
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    command = input_info['command']

    if command in {'counter', 'cycle'}:
        special_setall_function = globals()['setall_' + command + '_mode']  # ie setall_cycle_mode, gets func
        if not special_setall_function(database, dictionary, setall_value):
            return False
        return True

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


def setall_cycle_mode(database, dictionary, setall_value):
    active_cycle_list = dict_management.get_active_cycle_list(database)

    if setall_value not in {'complete', 'reset'}:
        print('Invalid parameter. Expected "complete" or "reset"', end='\n\n')
        return False

    if not active_cycle_list:
        print('There are no active cycle objectives', end='\n\n')
        return False

    if setall_value == 'complete':
        for objective in active_cycle_list:
            # Set the numerator to the denominator (100%). value is the key's dictionary value
            value = dictionary[objective]
            value['numerator'] = value['denominator']
    elif setall_value == 'reset':
        for objective in active_cycle_list:
            value = dictionary[objective]
            value['numerator'] = 0
    return True


def setall_counter_mode(_, dictionary, setall_value):  # _: doesn't need database
    try:
        setall_value = eval(setall_value)
    except (SyntaxError, NameError):
        print('Setall value must be a number', end='\n\n')
        return False
    if not isinstance(setall_value, int):
        print('Setall value must be an integer', end='\n\n')
        return False

    if not dictionary:
        print('There are no counters', end='\n\n')
        return False

    while True:
        print(f'Change ALL counters to a value of {setall_value}? (y/n)', end='\n\n')
        user_response = input().lower()
        if user_response == 'y':
            break
        elif user_response == 'n':
            return False

    for counter in dictionary:
        dictionary[counter]['numerator'] = setall_value
    return True


def rename_mode(database, dictionary, input_info, objective_name):
    # ex input: daily rename wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    objective_name = objective_name.lower()

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


def retask_mode(database, dictionary, input_info, objective_name):
    # ex input: daily retask wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    objective_name=objective_name.lower()

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    new_task_string = get_task_string()
    dictionary[objective_name]['task_string'] = new_task_string
    return True


def denominator_mode(database, dictionary, input_info, objective_name):
    # ex input: daily denominator wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    objective_name = objective_name.lower()

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    if not (new_denominator := get_nonzero_integer('Enter a progress denominator (ie 2 becomes 0/2) '
                                                   '(blank defaults to 1)')):
        return False
    dictionary[objective_name]['denominator'] = new_denominator
    return True


# Removing items ------------------------------------------------------------------------------------------
def remove_mode(database, dictionary, input_info, objective_name):
    # ex input: daily remove wanikani
    if dict_management.wrong_parameter_count(input_info['parameter_length'], 1):
        return False

    objective_name = objective_name.lower()

    if objective_name not in dictionary:  # If not found, look for as a substring
        if not (objective_name := dict_management.objective_search(database, dictionary, objective_name)):
            return False
    dictionary.pop(objective_name)
    return True


# Misc utility ------------------------------------------------------------------------------------------
def get_nonzero_integer(msg=None):
    while True:
        if msg:
            print(msg)
            print('Enter blank to cancel', end='\n\n')
        value = input().lower()
        print()  # Extra newline

        if not value:  # Cancel
            print('Returning to menu')
            return False
        if not format_integer(value):
            continue
        return value


def format_integer(value: str):
    multiplier = 1
    if value[-1] in {'k', 'm', 'b', 't'}:  # Extension
        extension = value[-1]
        value = value[:-1]
        if extension == 'k':
            multiplier = 1e3
        elif extension == 'm':
            multiplier = 1e6
        elif extension == 'b':
            multiplier = 1e9
        elif extension == 't':
            multiplier = 1e12
    try:
        number = eval(value)
    except (SyntaxError, NameError):
        print('Value must be a number')
        return False
    if not number:  # If it's 0
        print('Value cannot be 0')
        return False
    if isinstance(number, float):
        print('Value must be an integer')
        return False
    return int(number * multiplier)
