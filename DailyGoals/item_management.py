import dict_management
import date_logic


# Adding items ------------------------------------------------------------------------------------------
def add_item_base(database, dictionary, mode):  # Make sure not a dupe, get name/task string
    while True:  # Get objective name
        print('Enter a name for the objective (must be unique)')
        objective_name = input()
        if not objective_name.isascii():
            print('Please only use ASCII characters')
            continue
        break

    while True:  # Get task string
        print('Enter a brief task description/couple keywords (display: goal_name (task string))')
        task_string = input()
        if not task_string.isascii():
            print('Please only use ASCII characters')
            continue
        break

    # Route to correct function for dictionary format. Return False if failure. mode is passed for dict sorting
    if mode == 'cycle':
        if not add_cycle_item(database, dictionary, objective_name, task_string, mode):
            return False
    elif mode == 'counter':
        if not add_counter_item(database, dictionary, objective_name, task_string, mode):
            return False
    else:
        if not add_normal_item(database, dictionary, objective_name, task_string, mode):
            return False
    return True


def add_normal_item(database, dictionary, objective_name, task_string, mode):
    if not (progress_denominator := get_progress_denominator()):
        return False  # Abort if failed
    dictionary.update({objective_name: {'task_string': task_string, 'progress_denominator': progress_denominator,
                                        'progress_numerator': 0}})
    dict_management.sort_dictionary(database, mode)
    return True


def add_cycle_item(database, dictionary, objective_name, task_string, mode):
    if not (progress_denominator := get_progress_denominator()):
        return False  # Abort if failed

    print('Enter a frequency (every x days) or a week day name')
    user_input = input().lower()
    # Going by day name automatically fills day frequency and offset
    if user_input in {'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'}:
        week_day_number = database['week_day']  # Current day
        input_week_day_number = date_logic.convert_day(user_input)
        cycle_frequency = 7  # If a day is specified, it's weekly
        current_offset = input_week_day_number - week_day_number  # Diff between given day and today
    elif user_input.isnumeric():  # A number was given, not specific day
        cycle_frequency = eval(user_input)
        print('Enter offset until next occurrence (ie 0 if today, 1 if tomorrow)')
        current_offset = eval(input())
    else:
        print('Invalid input. Expected day name or day offset number.\n'
              'Returning to menu.')
        return False

    dictionary.update({objective_name: {'task_string': task_string, 'progress_denominator': progress_denominator,
                                        'progress_numerator': 0, 'cycle_frequency': cycle_frequency,
                                        'current_offset': current_offset}})
    dict_management.sort_dictionary(database, 'cycle')
    print(f"Added '{objective_name}'")
    return True


def add_counter_item(database, dictionary, objective_name, task_string, mode):
    dictionary.update({objective_name: {'task_string': task_string, 'counter': 0}})
    dict_management.sort_dictionary(database, mode)
    return True


def get_progress_denominator():
    print('Enter a progress denominator (ie 2 becomes 0/2) (blank defaults to 1)')
    progress_denominator = input()

    if progress_denominator:  # If it's not blank
        if not progress_denominator.isnumeric():
            print('Progress denominator must be a number\n'
                  'Returning to menu')
            return False
        progress_denominator = eval(progress_denominator)
        if progress_denominator <= 0:
            print('Progress quantity must be greater than 0\n'
                  'Returning to menu')
            return False
    else:  # Blank input defaults to 1
        progress_denominator = 1
    return progress_denominator


# Updating/editing items ------------------------------------------------------------------------------------------
def update_item(dictionary, objective_name, add_value):
    add_value = eval(add_value)
    dictionary[objective_name]['progress_numerator'] += add_value
    return True


def update_counter_item(counter_dict, objective_name, add_value):
    add_value = eval(add_value)
    counter_dict[objective_name]['counter'] += add_value  # Add to numerator
    return True


def complete_item(dictionary, objective_name):
    # If numerator < denominator
    if dictionary[objective_name]['progress_numerator'] < dictionary[objective_name]['progress_denominator']:
        # Make it 100%
        dictionary[objective_name]['progress_numerator'] = dictionary[objective_name]['progress_denominator']
        return True
    else:
        print('That objective is already marked as at least 100% complete')
        return False


def reset_item(dictionary, objective_name):
    # value = [task_string, progress_denominator, progress numerator]
    if dictionary[objective_name]['numerator'] != 0:
        dictionary[objective_name]['numerator'] = 0
        return True
    else:
        print('That objective is already marked as 0% complete')
        return False


def reset_counter_item(counter_dict, objective_name):
    if counter_dict[objective_name]['counter'] != 0:
        counter_dict[objective_name]['counter'] = 0
    else:
        print('That counter is already at 0')
        return False
    return True


def rename_item(database, dictionary, objective_name, new_name, mode):
    if new_name in dictionary:
        print('That name is already in use')
        return False
    dictionary[new_name] = dictionary[objective_name]
    dictionary.pop(objective_name)
    dict_management.sort_dictionary(database, mode)
    return True


def retask_item(dictionary, objective_name):
    while True:  # Get task string
        print('Enter a brief task description/couple keywords (display: goal_name (task string))')
        task_string = input()
        if not task_string.isascii():
            print('Please only use ASCII characters')
            continue
        break
    dictionary[objective_name]['task_string'] = task_string
    print('Successfully changed the task text')
    return True


def change_denominator(dictionary, objective_name, new_denominator):
    if new_denominator <= 0:
        print('Denominator must be greater than 0. Returning to menu')
        return False

    dictionary[objective_name]['progress_denominator'] = new_denominator
    return True


# Removing items ------------------------------------------------------------------------------------------
def remove_item(dictionary, objective_name):
    dictionary.pop(objective_name)
    print(f'Removed {objective_name}')
    return True
