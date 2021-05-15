import os
import date_logic
import dict_management

version_number = 0.8


def print_display(database):
    os.system('cls')
    settings = database['settings']
    stats = database['stats']

    # Print top header/welcome message
    print(f"[Daily] ('help' for commands) (v{version_number})")
    if settings['welcome_toggle']:
        print(database['welcome_message'])
    print()  # Extra newline

    # Print date: - 01/01 Sunday -
    calendar_date = database['calendar_date']  # Date dictionary
    month_text = date_logic.format_month_text(calendar_date['month'])
    day_text = date_logic.format_day_text(calendar_date['day'])
    week_day_text = date_logic.convert_day_number(calendar_date['week_day'])
    if not settings['date_switch']:
        print(f"- {month_text}/{day_text} {week_day_text} -")
    else:
        print(f"- {day_text}/{month_text} {week_day_text} -")
    print()  # Extra newline

    # Streak/total header: Streak: 0
    print(f"Streak: {stats['streak']}")
    if settings['total_toggle']:
        print('Total dailies completed:', stats['total_completed'])
    print(end='\n\n')  # Extra newlines

    display_list = dict_management.get_display_list(database)
    for dict_name in display_list:
        print_dictionary(database, dict_name)


def print_dictionary(database, dict_name):
    if dict_name == 'daily':
        daily_dict = database['daily_objectives']
        optional_dict = database['optional_objectives']
        if daily_dict: # Skip if empty
            print_daily_objectives(daily_dict)
        if optional_dict:
            print_optional_objectives(optional_dict)
            print()  # Extra newline
        elif daily_dict:
            print()  # Print extra newline here if dailies but no optionals
    elif dict_name == 'todo':
        todo_dict = database['todo_objectives']
        if todo_dict:  # Skip if empty
            print_todo_objectives(todo_dict)
            print()  # Extra newline
    elif dict_name == 'cycle':
        active_cycle_list = dict_management.get_active_cycle_list(database)
        inactive_cycle_list = dict_management.get_inactive_cycle_list(database)
        if active_cycle_list:  # Skip if empty
            print_active_cycle_objectives(database, active_cycle_list)
        if database['settings']['full_cycle_toggle'] and inactive_cycle_list:  # Skip if toggle off or dict empty
            print_inactive_cycle_objectives(database, inactive_cycle_list)
            print()  # Extra newline
        elif active_cycle_list:
            print()  # Extra newline if actives but no inactives
    elif dict_name == 'longterm':
        longterm_dict = database['longterm_objectives']
        if longterm_dict:  # Skip if empty
            print_longterm_objectives(longterm_dict)
            print()  # Extra newline
    elif dict_name == 'counter':
        counter_dict = database['counter_dict']
        if counter_dict:
            print_counter_dict(counter_dict)
            print()  # Extra newline
    return


def print_base_dictionary(dictionary):
    for key, value in dictionary.items():
        # Expects [task_string, progress_denominator, progress numerator]
        task_string = value[0]
        denominator = value[1]
        numerator = value[2]
        if numerator >= denominator:  # Complete
            print(f'[x] {key} ({task_string}): {numerator}/{denominator} ', end='')
            print('({:.2%}) (DONE!!)'.format(numerator / denominator))
        else:  # Incomplete
            print(f'[ ] {key} ({task_string}): {numerator}/{denominator} ', end='')
            print('({:.2%})'.format(numerator / denominator))


def print_daily_objectives(daily_dict):
    print('>>> Daily objectives:', end='\n\n')
    print_base_dictionary(daily_dict)


def print_optional_objectives(optional_dict):
    print('(Optional)', end='\n\n')
    print_base_dictionary(optional_dict)


def print_todo_objectives(todo_dict):
    print('>>> To-dos:', end='\n\n')
    print_base_dictionary(todo_dict)


def print_active_cycle_objectives(database, active_cycle_list):
    print('>>> Active cycles', end='\n\n')
    cycle_objectives = database['cycle_objectives']
    for key in active_cycle_list:
        # {task_string, progress_denominator, progress numerator, cycle_length, current_offset}
        value = cycle_objectives[key]
        task_string = value['task_string']
        denominator = value['progress_denominator']
        numerator = value['progress_denominator']
        cycle_frequency = value['cycle_frequency']
        percent = numerator/denominator
        if numerator >= denominator:  # Complete
            print(f'[x] {key} ({task_string}) (every {cycle_frequency}d): {numerator}/{denominator} (DONE!!)', end='')
            print('({:.2%})'.format(percent))
        else:  # Incomplete
            print(f'[ ] {key} ({task_string}) (every {cycle_frequency}d): {numerator}/{denominator} ', end='')
            print('({:.2%})'.format(percent))


def print_inactive_cycle_objectives(database, inactive_cycle_list):
    print('(Inactive cycles)')
    cycle_objectives = database['cycle_objectives']
    # {task_string, progress_denominator, progress numerator, cycle_length, current_offset}
    for key in inactive_cycle_list:
        value = cycle_objectives[key]
        task_string = value['task_string']
        cycle_frequency = value['cycle_frequency']
        current_offset = value['current_offset']
        print(f'{key} ({task_string}): Every {cycle_frequency}d, next in {current_offset}d')


def print_longterm_objectives(longterm_dict):
    print('>>> Long-term goals:', end='\n\n')
    print_base_dictionary(longterm_dict)


def print_counter_dict(counter_dict):
    print('>>> Counters', end='\n\n')
    for key, value in counter_dict.items():
        # {task_string, counter}
        task_string = counter_dict['task_string']
        counter = counter_dict['counter']
        print(f'{key} ({task_string}): {counter}')


def print_stats(database):
    print(f"Total completed daily goals: {database['total_completed']}\n"
          f"Days completed: {database['days_completed']}\n"
          f"Current streak: {database['streak']}\n"
          f"Best streak: {database['best_streak']}")


def print_settings(database):
    print(f"Print DD/MM: {database['date_switch']}\n"
          f"Print welcome: {database['welcome_toggle']}\n"
          f"Show total completed dailies on startup: {database['total_toggle']}\n"
          f"Always show dailies: {database['daily_toggle']}\n"
          f"Always show todos: {database['todo_toggle']}\n"
          f"Always show active cycles: {database['cycle_toggle']}\n"
          f"Always show all cycles: {database['full_cycle_toggle']}\n"
          f"Always show longterms: {database['longterm_toggle']}\n"
          f"Always show counters: {database['counter_toggle']}\n"
          f"Auto-match closest objective when given not found: {database['auto_match_toggle']}")



    print('Print MM/DD:', not database['date_switch'])
    print('Welcome message:', database['welcome_toggle'])
    print('Always show total:', database['total_toggle'])
    print('Always show long-terms:', database['longterm_toggle'])
