import os
import date_logic
import dict_management
import documentation

version_number = ['PRE-RELEASE']


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
    month = calendar_date['month']
    day = calendar_date['day']
    year = calendar_date['year']
    str_date = f'{year}-{month:02d}-{day:02d}'
    week_day = date_logic.convert_day_number(calendar_date['week_day'])
    print(f"- {week_day}, {date_logic.string_date(database, str_date)} -", end='\n\n')

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
        for dictionary in documentation.get_dictionary_names():
            overall_item_length += len(database[dictionary])
        if overall_item_length == 0:
            print("No items exist! Create some with '<type> add' (ex: daily add)!", end='\n\n')
        else:
            print("No items are visible! You can change toggle settings with 'toggle'", end='\n\n')
        return

    for dict_name in display_list:
        print_dictionary(database, dict_name)


def refresh_and_print(database, message):  # Refresh display then print message
    print_display(database)
    print(message, end='\n\n')


def print_dictionary(database, dict_name):
    globals()['print_' + dict_name + '_objectives'](database)


def print_base_dictionary(dictionary, containers, *, item_prefix='', item_suffix='', task_string_exec=None):
    """Given a dictionary of objectives, print them out with detailed information.

    :param dict dictionary: The dictionary of objectives
    :param dict containers: The dictionary of containers for the above dict type
    :param str item_prefix: String printed before each item
    :param str item_suffix: String printed after each time
    :param function task_string_exec: Function that takes a dict and returns a string.
    Passed the value of each item and returns a string to append to the task string
    :return:
    """
    def print_items(items_dict):
        for key, value in items_dict.items():
            display_name = value['display_name']
            task_string = value['task_string']
            formatted_task_string = ''
            if task_string:  # If it's not blank
                formatted_task_string = f' ({task_string})'
            if task_string_exec:
                formatted_task_string += task_string_exec(value)
            denominator = value['denominator']
            numerator = value['numerator']
            box = '[ ] '
            text = (f'{display_name}{formatted_task_string}: '
                    f'{numerator:,}/{denominator:,} ({numerator / denominator:.2%})')
            if numerator >= denominator:  # Complete
                box = '[x] '
                text += ' DONE!!'
            print(item_prefix + box + text + item_suffix)

    for container_name, container_value in containers.items():
        container_items = {k: dictionary[k] for k in container_value['items'] if k in dictionary}
        if container_name != '_default':
            print(f"[{container_value['display_name']}] ({len(container_value['items'])} items)", end='')
            if container_value['expanded']:
                print()
            else:
                print(' (Minimized)')
                continue
        print_items(container_items)
        print()


def print_daily_objectives(database):
    dictionary = database['daily']
    if dictionary:
        print('>>> Daily objectives:', end='\n\n')
        print_base_dictionary(dictionary, database['containers']['daily'])
        print()  # Extra newline


def print_optional_objectives(database):
    dictionary = database['optional']
    if dictionary:
        print('(Optional)', end='\n\n')
        print_base_dictionary(dictionary, database['containers']['optional'])
        print()  # Extra newline


def print_todo_objectives(database):
    dictionary = database['todo']
    if dictionary:
        print('>>> To-dos:')
        enforced_todo_dict = dict_management.get_enforced_todo_dict(database)
        if enforced_todo_dict:
            print("* '>' signifies enforced to-do; required for streak today", end='\n\n')
            print_base_dictionary(enforced_todo_dict, database['containers']['todo'], item_prefix='> ')
        else:
            print()  # Newline to make up for lack of enforced newline print
        unenforced_todo_dict = dict_management.get_unenforced_todo_dict(database)
        print_base_dictionary(unenforced_todo_dict, database['containers']['todo'])
        print()  # Extra newline


def print_active_cycle_objectives(database):
    dictionary = dict_management.get_active_cycle_dict(database)
    if dictionary:
        print('>>> Active cycles', end='\n\n')
        print_base_dictionary(dictionary, database['containers']['cycle'],
                              task_string_exec=lambda value: f" (every {value['cycle_frequency']}d)")
        print()  # Extra newline


def print_inactive_cycle_objectives(database):
    dictionary = dict_management.get_inactive_cycle_dict(database)
    if dictionary:
        print('(Inactive cycles)', end='\n\n')
        # {display_name, task_string, denominator, progress numerator, cycle_length, current_offset}
        for key, value in dictionary.items():
            display_name = value['display_name']
            task_string = value['task_string']
            cycle_frequency = value['cycle_frequency']
            current_offset = value['current_offset']
            denominator = value['denominator']
            print(f'{display_name} ({task_string}) (x/{denominator}): '
                  f'Every {cycle_frequency}d, next in {current_offset}d')
        print()  # Extra newline


def print_longterm_objectives(database):
    dictionary = database['longterm']
    if dictionary:
        print('>>> Long-term goals:', end='\n\n')
        print_base_dictionary(dictionary, database['containers']['longterm'])
        print()  # Extra newline


def print_counter_objectives(database):
    dictionary = database['counter']
    if dictionary:
        print('>>> Counters', end='\n\n')
        for key, value in dictionary.items():
            # {display_name, task_string, numerator}
            display_name = value['display_name']
            task_string = value['task_string']
            numerator = value['numerator']
            print(f'{display_name} ({task_string}): {numerator}')
        print()  # Extra newline


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
