import date_logic
import core_dict_logic


def add_cycle_item(line_data, objective_name):
    dictionary = line_data['cycle_objectives']

    add_items = []  # Will be filled unless add_item_base returns False, [task_string, progress_denominator]
    if not core_dict_logic.add_item_base(dictionary, objective_name, add_items):
        return False
    task_string, progress_denominator = add_items

    print('Enter a frequency (every x days) or a week day name')
    user_input = input().lower()
    # Going by day name automatically fills day frequency and offset
    if user_input in {'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'}:
        week_day = line_data['week_day']  # Current day
        cycle_frequency = 7  # If a day is specified, it's weekly
        current_offset = date_logic.convert_day(user_input) - week_day  # Diff from today and given day
    elif user_input.isnumeric():  # A number was given, not specific day
        cycle_frequency = eval(user_input)
        print('Enter offset until next occurrence (ie 0 if today, 1 if tomorrow)')
        current_offset = eval(input().lower())
    else:
        print('Invalid input. Expected day name or day offset number.\n'
              'Returning to menu.')
        return False

    # 0 is the numerator
    dictionary.update({objective_name: [task_string, progress_denominator, 0, cycle_frequency, current_offset]})
    core_dict_logic.sort_dictionary(line_data, 'cycle')
    print(f"Added '{objective_name}'")
    return True


def cycle_dict_setall(dictionary, setall_value):
    pass
