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
    print(f"- {date_logic.string_date(calendar_date)} -", end='\n\n')

    # Streak/total header
    print(f"Streak: {stats['streak']}")
    if settings['display_total']:
        print('Total dailies completed:', stats['total_completed'])
    print('\n')  # Extra two newlines

    # Print dicts
    display_list = dict_management.get_display_list(database)
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


def print_base_dictionary(database, dictionary, containers, *, item_prefix='', item_suffix='', extra_string_exec=None):
    """Given a dictionary of objectives, print them out with detailed information.

    :param dict database: The database
    :param dict dictionary: The dictionary of objectives
    :param dict containers: The dictionary of containers for the above dict type
    :param str item_prefix: String printed before each item
    :param str item_suffix: String printed after each time
    :param function extra_string_exec: Function that takes a dict and returns a string.
    Extra text to be inserted after the item name is generated according to this based on the item's value
    :return:
    """
    def print_items(items_dict):
        for key, value in items_dict.items():
            display_name = value['display_name']
            extra_string = ''
            if extra_string_exec:
                extra_string = extra_string_exec(value)
            denominator = value['denominator']
            numerator = value['numerator']
            box = '[ ] '
            history_link = ''
            if value['history_name'] and database['settings']['show_history_link']:
                history_link = f' [-> {value["history_name"]}]'
            body = (f'{display_name}{history_link}{extra_string}: '
                    f'{numerator:,}/{denominator:,} ({numerator / denominator:.2%})')
            if numerator >= denominator:  # Complete
                box = '[x] '
                body += ' DONE!!'
            print(f' {item_prefix}{box}{body}{item_suffix}')

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
    daily_dict = database['daily']
    optional_dict = database['optional']
    if daily_dict or optional_dict:
        print('>>> Dailies:', end='\n\n')
        if daily_dict:
            print_base_dictionary(database, daily_dict, database['containers']['daily'])
            print()  # Extra newline
        print_optional_objectives(database)


def print_optional_objectives(database):
    dictionary = database['optional']
    if dictionary:
        print('(Optional)', end='\n\n')
        print_base_dictionary(database, dictionary, database['containers']['optional'])
        print()  # Extra newline


def print_todo_objectives(database):
    dictionary = database['todo']
    if dictionary:
        print('>>> To-dos:')
        enforced_todo_dict = dict_management.get_enforced_todo_dict(database)
        if enforced_todo_dict:
            print("* '>' signifies enforced to-do; required for streak today", end='\n\n')
            print_base_dictionary(database, enforced_todo_dict, database['containers']['todo'], item_prefix='> ')
        else:
            print()  # Newline to make up for lack of enforced newline print
        unenforced_todo_dict = dict_management.get_unenforced_todo_dict(database)
        print_base_dictionary(database, unenforced_todo_dict, database['containers']['todo'])
        print()  # Extra newline


def print_cycle_objectives(database):
    dictionary = database['cycle']
    if dictionary:
        print('>>> Cycles', end='\n\n')
        print_active_cycle_objectives(database)
        print_inactive_cycle_objectives(database)


def get_cycle_sequence_string(obj_value):
    display_mode = obj_value['display_mode']
    if display_mode == 'number':
        return f'every {obj_value["cooldown_sequence"][0]}d'
    elif display_mode == 'week_day':
        week_cooldown = obj_value['week_cooldown']
        if week_cooldown == 0:
            cooldown_string = 'every'
        elif week_cooldown == 1:
            cooldown_string = 'every other'
        else:
            cooldown_string = f'every {week_cooldown + 1}'  # 2 cooldown = objective occurs every 3 weeks
        return f'{cooldown_string} [{"/".join(obj_value["week_days"])}]'
    elif display_mode == 'custom':
        return obj_value['frequency_description']
    else:
        quit('Invalid cycle display mode..')


def print_active_cycle_objectives(database):
    dictionary = dict_management.get_active_cycle_dict(database)
    if dictionary:
        print_base_dictionary(database, dictionary, database['containers']['cycle'],
                              extra_string_exec=lambda val: f' ({get_cycle_sequence_string(val)})')
        print()  # Extra newline


def print_inactive_cycle_objectives(database):
    dictionary = dict_management.get_inactive_cycle_dict(database)
    if dictionary:
        print('(Inactive cycles)', end='\n\n')
        for key, value in dictionary.items():
            display_name = value['display_name']
            remaining_cooldown = value['remaining_cooldown']
            denominator = value['denominator']
            if value['display_mode'] == 'number':
                print(f'{display_name} (x/{denominator}): '
                      f'Every {value["cooldown_sequence"][0]}d, next in {remaining_cooldown}d')
            else:  # == 'week_day'
                print(f'{display_name} (x/{denominator}): '
                      f'{get_cycle_sequence_string(value).capitalize()}, next in {remaining_cooldown}d')
        print()  # Extra newline


def print_longterm_objectives(database):
    dictionary = database['longterm']
    if dictionary:
        print('>>> Long-term goals:', end='\n\n')
        print_base_dictionary(database, dictionary, database['containers']['longterm'])
        print()  # Extra newline


def print_counter_objectives(database):
    dictionary = database['counter']
    if dictionary:
        print('>>> Counters', end='\n\n')
        for key, value in dictionary.items():
            display_name = value['display_name']
            numerator = value['numerator']
            history_link = ''
            if value['history_name'] and database['settings']['show_history_link']:
                history_link = f' [-> {value["history_name"]}]'
            print(f'{display_name}{history_link}: {numerator}')
        print()  # Extra newline


def print_note_objectives(database):
    pass


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


def pluralize(text, count):
    if count == 1:
        return text
    else:
        return text + 's'
