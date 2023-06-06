import os
import date_logic
import dict_management
import documentation

version_number = 'PRE-RELEASE'


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


# Sorting -------------------------------------------------------------------

def completion_then_alpha_sort(obj):
    # obj[1] refers to dictionary value in tuple (obj_name, dict value)
    # False sorts before True in ascending. a sorts before z. Sorts incomplete to top, then alphabetically.
    # (completion bool, name)
    return obj[1]['numerator'] >= obj[1]['denominator'], obj[0]


def cycle_sort(obj):
    # (current offset, completion bool, name)
    # 0 sorts before 1, False before True, a before z. Sorts by offset, then completion bool, then name
    return obj[1]['remaining_cooldown'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]


def todo_sort(obj):
    # Puts enforced daily to-do objectives on top (False sorts before True, so invert with not)
    # enforced_todo -> completed or not -> name
    return not obj[1]['enforced_todo'], obj[1]['numerator'] >= obj[1]['denominator'], obj[0]


def alpha_sort(obj):
    return obj[0]  # Just by the name


# Item printing --------------------------------------------------------

def print_dictionary(database, dict_name):
    globals()['print_' + dict_name](database)


def print_groups(database, dictionary, groups, display_order, print_items, sort_key, *, extra_string_func=None,
                 prefix_func=None, suffix_func=None):
    """Given a dictionary of objectives, print them out with detailed information.

    :param dict database: The database
    :param dict dictionary: The dictionary of objectives
    :param dict groups: The Groups dict for the corresponding dict type
    :param list display_order: A list of the order to display Groups in, not including the default
    :param function print_items: Function that prints a dict of objectives, called within a group.
    Signature: (database, items_dict, extra_string_exec, item_prefix, item_suffix)
    :param function sort_key: Sorting function that takes an obj_value
    :param function prefix_func: Function that takes an obj_value and returns a string to prefix the print
    :param function suffix_func: Function that takes an obj_value and returns a string to suffix the print
    :param function extra_string_func: Function that takes a dict and returns a string.
    Extra text to be inserted after the item name is generated according to this based on the item's value
    :return:
    """
    display_order = ['_Default'] + display_order
    for group_name, group_value in {k: groups[k] for k in display_order}.items():
        group_items = {k: dictionary[k] for k in group_value['items'] if k in dictionary}
        if group_name != '_Default':  # Exclude the default 'groupless' container
            items_len = len(group_value['items'])
            print(f"[{group_value['display_name']}] ({items_len} {pluralize('item', items_len)})", end='')
            if group_value['expanded']:
                print()  # Newline
            else:
                print(' (Minimized)')
                continue
        sorted_items = dict_management.sort_dict(group_items, sort_key)
        print_items(database, sorted_items, extra_string_func, prefix_func, suffix_func)
        print()


def print_items_generic(database, items_dict, extra_string_func, prefix_func, suffix_func):
    for key, value in items_dict.items():
        display_name = value['display_name']
        extra_string = '' if not extra_string_func else extra_string_func(value)
        prefix = '' if not prefix_func else prefix_func(value)
        suffix = '' if not suffix_func else suffix_func(value)
        linked = ' [Linked]' if value['link']['linked_to'] else ''
        tagged = ' [Tagged]' if value['tag'] else ''
        denominator = value['denominator']
        numerator = value['numerator']
        history_link = ''
        if value['history_name'] and database['settings']['show_history_link']:
            history_link = f' [-> {value["history_name"]}]'
        body = (f'{display_name}{extra_string}: '
                f'{numerator:,}/{denominator:,} ({numerator / denominator:.2%})')
        box = '[x] ' if numerator >= denominator else '[ ] '
        print(f' {prefix}{box}{body}{suffix}{history_link}{linked}{tagged}')


def print_items_counters(database, items_dict, extra_string_func, prefix_func, suffix_func):
    for key, value in items_dict.items():
        display_name = value['display_name']
        extra_string = '' if not extra_string_func else extra_string_func(value)
        prefix = '' if not prefix_func else prefix_func(value)
        suffix = '' if not suffix_func else suffix_func(value)
        numerator = value['numerator']
        history_link = ''
        if value['history_name'] and database['settings']['show_history_link']:
            history_link = f' [-> {value["history_name"]}]'
        print(f'{prefix}{display_name}{history_link}{extra_string}: {numerator}{suffix}')


def print_daily(database):
    dictionary = database['daily']
    groups = database['groups']['daily']
    groups_display = database['groups_display']['daily']
    if dictionary or database['optional']:
        print('>>> Dailies:', end='\n\n')
        if dictionary:
            print_groups(database, dictionary, groups, groups_display, print_items_generic, completion_then_alpha_sort)
            print()  # Extra newline
        print_optional(database)


def print_optional(database):
    dictionary = database['optional']
    groups = database['groups']['optional']
    groups_display = database['groups_display']['optional']
    if dictionary:
        print('(Optional)', end='\n\n')
        print_groups(database, dictionary, groups, groups_display, print_items_generic, completion_then_alpha_sort)
        print()  # Extra newline


def print_todo(database):
    dictionary = database['todo']
    groups = database['groups']['todo']
    groups_display = database['groups_display']['todo']
    if dictionary:
        print('>>> To-dos:')
        enforced_todo_dict = dict_management.get_enforced_todo(database)
        if enforced_todo_dict:
            print("* '>' signifies enforced to-do; required for streak today")
        print()
        print_groups(database, dictionary, groups, groups_display, print_items_generic, todo_sort,
                     prefix_func=lambda x: '> ' if x['enforced_todo'] else '')
        print()  # Extra newline


def print_cycle(database):
    dictionary = database['cycle']
    if dictionary:
        print('>>> Cycles', end='\n\n')
        print_active_cycle(database)
        print_inactive_cycle(database)


def print_active_cycle(database):
    active_cycle_dict = dict_management.get_active_cycle(database)
    inactive_cycle_dict = dict_management.get_inactive_cycle(database)
    groups = database['groups']['cycle']
    groups_display = database['groups_display']['cycle']
    if active_cycle_dict:
        print_groups(database, active_cycle_dict, groups, groups_display, print_items_generic, cycle_sort,
                     extra_string_func=lambda val: f' ({get_cycle_sequence_string(val)})')
        if not inactive_cycle_dict:  # Inactive print will cover if exists
            print()  # Extra newline


def print_inactive_cycle(database, preview_len=None):
    inactive_cycle_dict = dict_management.get_inactive_cycle(database)
    if preview_len is None:
        preview_len = database['settings']['cycle_preview']
    if inactive_cycle_dict:
        print('(Inactive cycles)', end='\n\n')
        for key, value in inactive_cycle_dict.items():
            display_name = value['display_name']
            remaining_cooldown = value['remaining_cooldown']
            denominator = value['denominator']
            if value['display_mode'] == 'number':
                print(f' {display_name} (x/{denominator}): '
                      f'Every {value["cooldown_sequence"][0]}d, next in {remaining_cooldown}d')
            else:  # == 'week_day'
                print(f' {display_name} (x/{denominator}): '
                      f'{get_cycle_sequence_string(value).capitalize()}, next in {remaining_cooldown}d')
        print(end='\n\n')  # Extra newline


def print_longterm(database):
    dictionary = database['longterm']
    groups = database['groups']['longterm']
    groups_display = database['groups_display']['longterm']
    if dictionary:
        print('>>> Long-term goals:', end='\n\n')
        print_groups(database, dictionary, groups, groups_display, print_items_generic, alpha_sort)
        print()  # Extra newline


def print_counter(database):
    dictionary = database['counter']
    groups = database['groups']['counter']
    groups_display = database['groups_display']['counter']
    if dictionary:
        print('>>> Counters', end='\n\n')
        print_groups(database, dictionary, groups, groups_display, print_items_counters, alpha_sort)
        print()  # Extra newline


def print_note(database):
    pass


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
