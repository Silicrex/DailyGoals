import dict_management
import date_logic
import exceptions


# Base core dict functions need to take (database, context, dictionary, *extra_input)
# Return False = abort, return True = sort and save

# Adding items ------------------------------------------------------------------------------------------
def add_mode(database, context, dictionary, *extra_input):
    # ex input: daily add
    command = context['command']  # Command to identify if different add type

    if command in {'counter', 'cycle', 'todo'}:
        special_add_function = globals()['add_' + command + '_mode']  # ie add_cycle_mode, gets corresponding func
        if not special_add_function(database, dictionary, *extra_input):
            return False
        return True

    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

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


def add_cycle_mode(database, dictionary, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage('cycle', 'add')

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


def add_counter_mode(_, dictionary, *extra_input):  # Doesn't need database
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage('counter', 'add')

    objective_name = get_objective_name()
    objective_name_lower = objective_name.lower()
    if objective_name_lower in dictionary:
        print('Counter by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    dictionary.update({objective_name_lower: {'display_name': objective_name, 'task_string': task_string,
                                              'numerator': 0}})
    return True


def add_todo_mode(_, dictionary, *extra_input):  # Doesn't need database
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage('todo', 'add')

    objective_name = get_objective_name()
    objective_name_lower = objective_name.lower()
    if objective_name_lower in dictionary:
        print('Objective by that name already exists. Returning to menu', end='\n\n')
        return False
    task_string = get_task_string()
    denominator = get_denominator()
    while True:
        print('Should this todo objective count towards daily requirement? (y/n)', end='\n\n')
        user_response = input().lower()
        print()  # Newline
        if user_response in {'yes', 'y'}:
            enforced_daily = True
            break
        elif user_response in {'no', 'n'}:
            enforced_daily = False
            break
    dictionary.update({objective_name_lower: {'display_name': objective_name, 'task_string': task_string,
                                              'denominator': denominator, 'numerator': 0,
                                              'enforced_daily': enforced_daily}})
    return True


def add_note_mode(_, dictionary, *extra_input):  # Doesn't need database
    # ex input: note add
    # ex input: note add 0
    if len(extra_input) > 1:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage('note', 'add')

    note_count = len(dictionary)
    if extra_input:
        note_index = extra_input[0]
        try:
            note_index = eval(note_index)
        except (NameError, SyntaxError):
            print('Invalid index', end='\n\n')
            raise exceptions.InvalidCommandUsage('note', 'add')
        if not isinstance(note_index, int):
            print('Invalid index', end='\n\n')
            raise exceptions.InvalidCommandUsage('note', 'add')

        if note_index > note_count - 1:  # If specified index is higher than list length, bump down to end index
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
        print('Enter a name for the objective (must be unique; no leading/trailing spaces)', end='\n\n')
        objective_name = input().strip()  # Get input and remove leading/trailing spaces
        print()  # Extra newline
        if not objective_name:
            print('Objective name cannot be blank')
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
            #  print('Denominator defaulted to 1')  # Doesn't show anyways
            return 1
        if not (denominator := format_integer(denominator)):
            continue
        if denominator < 0:  # Case of 0 is already handled in format_integer(), but not negatives
            print('Denominator must be greater than 0')
            continue
        return denominator


# Updating/editing items ------------------------------------------------------------------------------------------
def update_mode(database, context, dictionary, *extra_input):
    # ex input: daily update wanikani 50
    # ex input: daily update clean dishes

    # Spaces in names complicates. Prioritize searching for objective name over valid update value.
    # Can have a case where obj name is something like "Do number 9". Command could potentially be
    # "daily update do number 9" to increment it by one, or "daily update do number 9 1" for specified.

    command = context['command']  # Cycle handled differently

    if not extra_input:
        print('Must provide an objective to update', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    full_string = ' '.join(extra_input).lower()  # Lowercase string of entire rest of input
    # Search for full string as an objective name; assuming no update value specified
    if (objective_name := dict_management.objective_search(database, dictionary, full_string)) in dictionary:
        update_value = '1'  # str because format_integer takes a string
    else:  # Objective wasn't found. Assume update value was specified
        sub_string = ' '.join(extra_input[:-1]).lower()  # Last element should be update value
        if not (objective_name := dict_management.objective_search(database, dictionary, sub_string)):
            print('Objective name not found', end='\n\n')
            raise exceptions.InvalidCommandUsage(command, context['mode'])
        update_value = extra_input[-1]

    # Validate/format update value from str to int
    if not (update_value := format_integer(update_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        raise exceptions.InvalidCommandUsage(command, context['mode'])  # Invalid update value

    if command == 'cycle':  # Can't update inactive item
        if objective_name not in dict_management.get_active_cycle_list(database):
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    dictionary[objective_name]['numerator'] += update_value
    return True


def set_mode(database, context, dictionary, *extra_input):
    # ex input: daily set wanikani 50

    command = context['command']  # Cycle handled differently

    if not extra_input:
        print('Must provide an objective to update and set value', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input[:-1]).lower()  # Last element should be set value
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    if not (set_value := format_integer(extra_input[-1])):  # Enforces non-zero integer. Accepts extension ie 1k
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    dictionary[objective_name]['numerator'] = set_value
    return True


def complete_mode(database, context, dictionary, *extra_input):
    # ex input: daily complete wanikani

    command = context['command']

    if not extra_input:
        print('Must provide an objective to set as complete', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    value = dictionary[objective_name]
    # If numerator < denominator
    if value['numerator'] < value['denominator']:
        # Then make it 100%
        value['numerator'] = value['denominator']
    else:
        print('That objective is already marked as at least 100% complete', end='\n\n')
        return False
    return True


def reset_mode(database, context, dictionary, *extra_input):
    # ex input: daily reset wanikani

    command = context['command']

    if not extra_input:
        print('Must provide an objective to reset', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_list(database):  # Can't update inactive item
            print('Cannot update progress for inactive cycle objectives', end='\n\n')
            return False

    value = dictionary[objective_name]
    if value['numerator'] != 0:
        value['numerator'] = 0
    else:
        print('That item already has no progress', end='\n\n')
        return False
    return True


def setall_mode(database, context, dictionary, *extra_input):
    # ex input: daily setall complete

    command = context['command']

    if not extra_input or len(extra_input) > 1:
        print('Must provide a setall type', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    setall_value = extra_input[0]

    if command in {'counter', 'cycle'}:
        special_setall_function = globals()['setall_' + command + '_mode']  # ie setall_cycle_mode, gets func
        if not special_setall_function(database, dictionary, setall_value):
            return False
        return True

    if setall_value not in {'complete', 'reset'}:
        print('Invalid parameter setall value', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

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
        print('Invalid parameter setall value', end='\n\n')
        raise exceptions.InvalidCommandUsage('cycle', 'setall')

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
    if not (setall_value := format_integer(setall_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        raise exceptions.InvalidCommandUsage('counter', 'setall')

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


def rename_mode(database, context, dictionary, *extra_input):
    # ex input: daily rename wanikani

    command = context['command']

    if not extra_input:
        print('Must provide an objective to rename', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    new_name = get_objective_name()
    if new_name in dictionary:
        print('That name is already in use', end='\n\n')
        return False
    dictionary[new_name] = dictionary[objective_name]
    dictionary.pop(objective_name)
    return True


def retask_mode(database, context, dictionary, *extra_input):
    # ex input: daily retask wanikani
    command = context['command']

    if not extra_input:
        print('Must provide an objective to retask', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    new_task_string = get_task_string()
    dictionary[objective_name]['task_string'] = new_task_string
    return True


def denominator_mode(database, context, dictionary, *extra_input):
    # ex input: daily denominator wanikani
    command = context['command']

    if not extra_input:
        print('Must provide an objective to change the denominator of', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    if not (new_denominator := get_denominator()):
        return False
    dictionary[objective_name]['denominator'] = new_denominator
    return True


# Removing items ------------------------------------------------------------------------------------------
def remove_mode(database, context, dictionary, *extra_input):
    # ex input: daily remove wanikani
    command = context['command']

    if not extra_input:
        print('Must provide an objective to remove', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(extra_input).lower()
    if not (objective_name := dict_management.objective_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise exceptions.InvalidCommandUsage(command, context['mode'])

    dictionary.pop(objective_name)
    return True


# Misc utility ------------------------------------------------------------------------------------------
def format_integer(value: str):
    multiplier = 1  # Default value
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
    try:  # Try an eval
        value = eval(value)
    except (SyntaxError, NameError):
        print('Value must be a number', end='\n\n')
        return False

    try:  # The input base value can be a float, as long as the end result is an integer
        # We need output to be an integer. But, something like "1.5b" will result in a float, since there is
        # multiplication by a float involved. Don't want any implicit conversions, so compare int result to float
        # result, and see if they're numerically equal.
        if not (number := int(value * multiplier)) == value * multiplier:
            print('Value must be an integer', end='\n\n')
            return False
    except TypeError:  # Valid eval happened, but not a valid number
        print('Value must be an integer*', end='\n\n')
        return False

    if number == 0:
        print('Value cannot be 0', end='\n\n')
        return False
    return number
