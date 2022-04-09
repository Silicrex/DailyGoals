import os
import date_logic
import dict_management
import documentation

version_number = 0.8


def print_display(database):
    os.system('cls')
    settings = database['settings']
    stats = database['stats']

    # Print top header/welcome message
    print(f"[Daily] ('help' for commands) (v{version_number})")
    if settings['welcome']:
        print(database['welcome_message'])
    print()  # Extra newline

    # Print date: - 01/01/2022 Sunday -
    calendar_date = database['settings']['calendar_date']  # Date dictionary
    date1 = calendar_date['month']
    date2 = calendar_date['day']
    year = calendar_date['year']
    week_day = date_logic.convert_day_number(calendar_date['week_day'])
    if settings['date_switch']:
        date1, date2 = date2, date1
    print(f"- {date1:01}/{date2:01}/{year} {week_day} -", end='\n\n')

    # Streak/total header
    print(f"Streak: {stats['streak']}")
    if settings['display_total']:
        print('Total dailies completed:', stats['total_completed'])
    print('\n')  # Extra two newlines

    # Print dicts
    display_list = dict_management.get_display_list(database)
    if 'inactive_cycle' in display_list:  # If active cycles are toggled off, don't show inactives
        if not settings['cycle']:
            display_list.remove('inactive_cycle')
    if not display_list:  # If display_list is empty
        overall_item_length = 0
        for container in documentation.get_dictionary_names():
            overall_item_length += len(dict_management.name_to_container(database, container))
        if overall_item_length == 0:
            print("No items exist! Create some with '<container> add' (ex: daily add)!", end='\n\n')
        else:
            print("No items are visible! You can change toggle settings with 'toggle'", end='\n\n')
        return

    for dict_name in display_list:
        print_dictionary(database, dict_name)


def refresh_and_print(database, message):  # Refresh display then print message
    print_display(database)
    print(message, end='\n\n')


def print_dictionary(database, dict_name):
    if dict_name == 'daily':
        daily_dict = database['daily']
        if daily_dict:  # Skip if empty
            print_daily_objectives(daily_dict)
            print()  # Extra newline
        else:  # Neither daily nor optionals have any
            print('There are no daily objectives')
    elif dict_name == 'optional':
        optional_dict = database['optional']
        if optional_dict:
            print_optional_objectives(optional_dict)
            print()  # Extra newline
        else:
            print('There are no optional objectives')
    elif dict_name == 'todo':
        todo_dict = database['todo']
        if todo_dict:  # Skip if empty
            print_todo_objectives(database, todo_dict)
            print()  # Extra newline
    elif dict_name == 'active_cycle':
        active_cycle_list = dict_management.get_active_cycle_list(database)
        if active_cycle_list:  # Skip if empty
            print_active_cycle_objectives(database, active_cycle_list)
            print()  # Extra newline
    elif dict_name == 'inactive_cycle':
        inactive_cycle_list = dict_management.get_inactive_cycle_list(database)
        if inactive_cycle_list:  # Skip if empty
            print_inactive_cycle_objectives(database, inactive_cycle_list)
            print()  # Extra newline
    elif dict_name == 'longterm':
        longterm_dict = database['longterm']
        if longterm_dict:  # Skip if empty
            print_longterm_objectives(longterm_dict)
            print()  # Extra newline
    elif dict_name == 'counter':
        counter_dict = database['counter']
        if counter_dict:
            print_counter_dict(counter_dict)
            print()  # Extra newline


def print_base_dictionary(dictionary):
    for key, value in dictionary.items():
        # {display_name, task_string, denominator, numerator}
        display_name = value['display_name']
        task_string = value['task_string']
        formatted_task_string = ''
        if task_string:  # If it's not blank
            formatted_task_string = f' ({task_string})'
        denominator = value['denominator']
        numerator = value['numerator']
        if numerator >= denominator:  # Complete
            print(f'[x] {display_name}{formatted_task_string}: ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%}) (DONE!!)'.format(numerator / denominator))
        else:  # Incomplete
            print(f'[ ] {display_name}{formatted_task_string}: ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%})'.format(numerator / denominator))


def print_daily_objectives(daily_dict):
    print('>>> Daily objectives:', end='\n\n')
    print_base_dictionary(daily_dict)


def print_optional_objectives(optional_dict):
    print('(Optional)', end='\n\n')
    print_base_dictionary(optional_dict)


def print_todo_objectives(database, todo_dict):
    def print_obj(obj_value):
        display_name = obj_value['display_name']
        task_string = obj_value['task_string']
        formatted_task_string = ''
        if task_string:  # If it's not blank
            formatted_task_string = f' ({task_string})'
        denominator = obj_value['denominator']
        numerator = obj_value['numerator']
        if numerator >= denominator:  # Complete
            print(f'[x] {display_name}{formatted_task_string}: ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%}) (DONE!!)'.format(numerator / denominator))
        else:  # Incomplete
            print(f'[ ] {display_name}{formatted_task_string}: ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%})'.format(numerator / denominator))

    print('>>> To-dos:')
    enforced_daily_list = dict_management.get_enforced_dailies_list(database)
    if enforced_daily_list:
        print("* '>' signifies enforced to-do; required for streak today", end='\n\n')
        for key in enforced_daily_list:
            print('> ', end='')
            print_obj(todo_dict[key])
    else:
        print()  # Newline to make up for lack of enforced newline print
    for key in dict_management.get_unenforced_cycle_list(database):
        # {display_name, task_string, denominator, numerator, enforced_daily}
        value = todo_dict[key]
        print_obj(value)


def print_active_cycle_objectives(database, active_cycle_list):
    print('>>> Active cycles', end='\n\n')
    cycle_objectives = database['cycle']
    for key in active_cycle_list:
        # {display_name, task_string, denominator, progress numerator, cycle_length, current_offset}
        value = cycle_objectives[key]
        display_name = value['display_name']
        task_string = value['task_string']
        formatted_task_string = ''
        if task_string:  # If it's not blank
            formatted_task_string = f' ({task_string})'
        denominator = value['denominator']
        numerator = value['numerator']
        cycle_frequency = value['cycle_frequency']
        percent = numerator/denominator
        if numerator >= denominator:  # Complete
            print(f'[x] {display_name}{formatted_task_string} (every {cycle_frequency}d): ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%}) (DONE!!)'.format(percent))
        else:  # Incomplete
            print(f'[ ] {display_name}{formatted_task_string} (every {cycle_frequency}d): ', end='')
            print('{:,}/{:,} '.format(numerator, denominator), end='')
            print('({:.2%})'.format(percent))


def print_inactive_cycle_objectives(database, inactive_cycle_list):
    print('(Inactive cycles)', end='\n\n')
    cycle_objectives = database['cycle']
    # {display_name, task_string, denominator, progress numerator, cycle_length, current_offset}
    for key in inactive_cycle_list:
        value = cycle_objectives[key]
        display_name = value['display_name']
        task_string = value['task_string']
        cycle_frequency = value['cycle_frequency']
        current_offset = value['current_offset']
        denominator = value['denominator']
        print(f'{display_name} ({task_string}) (x/{denominator}): Every {cycle_frequency}d, next in {current_offset}d')


def print_longterm_objectives(longterm_dict):
    print('>>> Long-term goals:', end='\n\n')
    print_base_dictionary(longterm_dict)


def print_counter_dict(counter_dict):
    print('>>> Counters', end='\n\n')
    for key, value in counter_dict.items():
        # {display_name, task_string, numerator}
        display_name = value['display_name']
        task_string = value['task_string']
        numerator = value['numerator']
        print(f'{display_name} ({task_string}): {numerator}')


def print_stats(database):
    os.system('cls')
    print(f"Total completed daily goals: {database['stats']['total_completed']}\n"
          f"Days completed: {database['stats']['days_completed']}\n"
          f"Current streak: {database['stats']['streak']}\n"
          f"Best streak: {database['stats']['best_streak']}", end='\n\n')


def print_settings(database):
    os.system('cls')
    settings = database['settings']
    print(f">>> Main display dictionary toggles\n\n"
          f"Daily: {settings['daily']}\n"
          f"Todo: {settings['todo']}\n"
          f"Active cycle: {settings['cycle']}\n"
          f"-> Full cycle: {settings['full_cycle']}\n"
          f"Longterm: {settings['longterm']}\n"
          f"Counter: {settings['counter']}\n"
          f"Note: {settings['note']}\n\n\n"
          f">>> Main display header\n\n"
          f"Print DD/MM: {settings['date_switch']}\n"
          f"Print welcome: {settings['welcome']}\n"
          f"Show total completed dailies: {settings['display_total']}\n\n\n"
          f">>> Dictionary functionality\n\n"
          f"Objective search auto-match (skip confirmation): {settings['auto_match']}", end='\n\n')


def confirm(text):  # Take print statement, get yes or no
    while True:
        print(text, end='\n\n')  # Asks the question
        user_response = input().lower()
        print()  # Newline to separate input from print
        if user_response in {'yes', 'y'}:
            return True
        elif user_response in {'no', 'n'}:
            return False
