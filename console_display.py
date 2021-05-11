import os
import date_logic
import core_dict_logic
import file_management

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

    display_list = core_dict_logic.get_display_list(database)
    for dict_name in display_list:
        print_dictionary(database, dict_name)
        print()  # Extra newline


def print_dictionary(database, dict_name):
    if dict_name == 'daily':
        daily_dict = database['daily_objectives']
        if daily_dict: # Skip if empty
            print('>>> Daily objectives:', end='\n\n')
            print_base_dictionary(daily_dict)
            print()  # Extra newline
            print('(Optional)', end='\n\n')
            print_base_dictionary(database['optional_objectives'])
    elif dict_name == 'todo':
        todo_dict = database['todo_objectives']
        if todo_dict:  # Skip if empty
            print('>>> To-dos:', end='\n\n')
            print_base_dictionary(todo_dict)
    elif dict_name == 'cycle':
        active_cycle_list = core_dict_logic.get_active_cycle_list(database)
        if active_cycle_list:  # Skip if empty
            print('>>> Active cycles', end='\n\n')
            print_active_cycle_objectives(database, active_cycle_list)
        if database['settings']['full_cycle_toggle']:
            print()  # Extra newline
            print('(Inactive cycles)')
            print_inactive_cycle_objectives(database)
    elif dict_name == 'longterm':
        print('>>> Long-term goals:', end='\n\n')
        print_base_dictionary(database['longterm_objectives'])
    elif dict_name == 'counter':
        print('>>> Counters:', end='\n\n')
        print_counters(database)
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


def print_active_cycle_objectives(database, active_cycle_list):
    active_cycles = {}
    for objective in active_cycle_list:
        active_cycles.update({objective: database['cycle_objectives'][objective]})
    for key, value in active_cycles.items():
        # [task_string, progress_denominator, progress numerator, cycle length, current offset]
        task = value[0]
        denominator = value[1]
        numerator = value[2]
        length = value[3]
        percent = numerator/denominator
        if numerator >= denominator:  # Complete
            print(f'[x] {key} ({task}) (every {length}d): {numerator}/{denominator} (DONE!!)', end='')
            print('({:.2%})'.format(percent))
        else:  # Incomplete
            print(f'[ ] {key} ({task}) (every {length}d): {numerator}/{denominator} ', end='')
            print('({:.2%})'.format(percent))


def print_inactive_cycle_objectives(database):
    # [task_string, progress_denominator, progress numerator, cycle length, current offset]
    for key, value in database['cycle_objectives'].items():
        if value[4] == 0:  # Skip actives
            continue
        print(f'{key} ({value[0]}): Every {value[3]}d, next in {value[4]}d')


def print_counters(database):
    for key, value in database['counter_dict'].items():
        # value = [task_string, number]
        print(f'{key} ({value[0]}): {value[1]}')


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
