import os
import date_logic
import dict_management
import documentation
from database import DB

version_number = 'PRE-RELEASE'


def print_display():
    os.system('cls')
    settings = DB['settings']
    stats = DB['stats']

    # Print top header/welcome message
    print(f"[Daily] ('help' for commands) (v{version_number})")
    if settings['welcome']:
        print(DB['welcome_message'])
    print()  # Extra newline

    # Print date: - 01/01/2022 Sunday -
    calendar_date = DB['settings']['calendar_date']  # Date dictionary
    print(f"- {date_logic.string_date(calendar_date)} -", end='\n\n')

    # Streak/total header
    print(f"Streak: {stats['streak']}")
    if settings['display_total']:
        print('Total dailies completed:', stats['total_completed'])
    print('\n')  # Extra two newlines

    # Print dicts
    display_list = dict_management.get_display_list()
    if not display_list:  # If display_list is empty
        overall_item_length = 0
        for dictionary in documentation.get_dictionary_names():
            overall_item_length += len(DB[dictionary])
        if overall_item_length == 0:
            print("No items exist! Create some with '<type> add' (ex: daily add)!", end='\n\n')
        else:
            print("No items are visible! You can change toggle settings with 'toggle'", end='\n\n')
        return

    for dict_name in display_list:
        print_dictionary(dict_name)


def refresh_display(message=''):  # Refresh display then print message
    print_display()
    if message:
        print(message, end='\n\n')


# Sorting -------------------------------------------------------------------

def completion_then_alpha_sort(item):
    # item[1] refers to dictionary value in tuple (item_key, dict value)
    # False sorts before True in ascending. a sorts before z. Sorts incomplete to top, then alphabetically.
    # (completion bool, name)
    return item[1]['numerator'] >= item[1]['denominator'], item[0]


def cycle_sort(item):
    # (current offset, completion bool, name)
    # 0 sorts before 1, False before True, a before z. Sorts by offset, then completion bool, then name
    return item[1]['remaining_cooldown'], item[1]['numerator'] >= item[1]['denominator'], item[0]


def todo_sort(item):
    # Puts enforced daily to-do items on top (False sorts before True, so invert with not)
    # enforced_todo -> completed or not -> name
    return not item[1]['enforced_todo'], item[1]['numerator'] >= item[1]['denominator'], item[0]


def alpha_sort(item):
    return item[0]  # Just by the name


# Item printing --------------------------------------------------------

def print_dictionary(dict_name):
    globals()['print_' + dict_name]()


def print_groups(dictionary, groups, display_order, print_items, sort_key, *, extra_string_func=None,
                 prefix_func=None, suffix_func=None):
    """Given a dictionary of items, print them out with detailed information.

    :param dict dictionary: The dictionary of items
    :param dict groups: The Groups dict for the corresponding dict type
    :param list display_order: A list of the order to display Groups in, not including the default
    :param function print_items: Function that prints a dict of items, called within a group.
    Signature: (DB, items_dict, extra_string_exec, item_prefix, item_suffix)
    :param function sort_key: Sorting function that takes an item_value
    :param function prefix_func: Function that takes an item_value and returns a string to prefix the print
    :param function suffix_func: Function that takes an item_value and returns a string to suffix the print
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
        print_items(sorted_items, extra_string_func, prefix_func, suffix_func)
        print()


def print_items_generic(items_dict, extra_string_func=None, prefix_func=None, suffix_func=None):
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
        if value['history_name'] and DB['settings']['show_history_link']:
            history_link = f" [-> {value['history_name']}]"
        body = (f'{display_name}{extra_string}: '
                f'{numerator:,}/{denominator:,} ({numerator / denominator:.2%})')
        box = '[x] ' if numerator >= denominator else '[ ] '
        print(f' {prefix}{box}{body}{suffix}{history_link}{linked}{tagged}')


def print_items_counters(items_dict, extra_string_func=None, prefix_func=None, suffix_func=None):
    for key, value in items_dict.items():
        display_name = value['display_name']
        extra_string = '' if not extra_string_func else extra_string_func(value)
        prefix = '' if not prefix_func else prefix_func(value)
        suffix = '' if not suffix_func else suffix_func(value)
        numerator = value['numerator']
        history_link = ''
        if value['history_name'] and DB['settings']['show_history_link']:
            history_link = f" [-> {value['history_name']}]"
        print(f'{prefix}{display_name}{history_link}{extra_string}: {numerator}{suffix}')


def print_daily():
    dictionary = DB['daily']
    groups = DB['groups']['daily']
    groups_display = DB['groups_display']['daily']
    if dictionary or DB['optional']:
        print('>>> Dailies:', end='\n\n')
        if dictionary:
            print_groups(dictionary, groups, groups_display, print_items_generic, completion_then_alpha_sort)
            print()  # Extra newline
        print_optional()


def print_optional():
    dictionary = DB['optional']
    groups = DB['groups']['optional']
    groups_display = DB['groups_display']['optional']
    if dictionary:
        print('(Optional)', end='\n\n')
        print_groups(dictionary, groups, groups_display, print_items_generic, completion_then_alpha_sort)
        print()  # Extra newline


def print_todo():
    dictionary = DB['todo']
    groups = DB['groups']['todo']
    groups_display = DB['groups_display']['todo']
    if dictionary:
        print('>>> To-dos:')
        enforced_todo_dict = dict_management.get_enforced_todo()
        if enforced_todo_dict:
            print("* '>' signifies enforced to-do; required for streak today")
        print()
        print_groups(dictionary, groups, groups_display, print_items_generic, todo_sort,
                     prefix_func=lambda x: '> ' if x['enforced_todo'] else '')
        print()  # Extra newline


def print_cycle():
    dictionary = DB['cycle']
    if dictionary:
        print('>>> Cycles', end='\n\n')
        print_active_cycle()
        print_inactive_cycle()


def print_active_cycle():
    active_cycle_dict = dict_management.get_active_cycle()
    inactive_cycle_dict = dict_management.get_inactive_cycle()
    groups = DB['groups']['cycle']
    groups_display = DB['groups_display']['cycle']
    if active_cycle_dict:
        print_groups(active_cycle_dict, groups, groups_display, print_items_generic, cycle_sort,
                     extra_string_func=lambda val: f' ({get_cycle_sequence_string(val)})')
        if not inactive_cycle_dict:  # Inactive print will cover if exists
            print()  # Extra newline


def print_inactive_cycle(preview_len=None):
    inactive_cycle_dict = dict_management.get_inactive_cycle()
    if preview_len is None:
        preview_len = DB['settings']['cycle_preview']
    if inactive_cycle_dict:
        print('(Inactive cycles)', end='\n\n')
        for key, value in inactive_cycle_dict.items():
            display_name = value['display_name']
            remaining_cooldown = value['remaining_cooldown']
            denominator = value['denominator']
            if value['display_mode'] == 'number':
                print(f" {display_name} (x/{denominator}): "
                      f"Every {value['cooldown_sequence'][0]}d, next in {remaining_cooldown}d")
            else:  # == 'week_day'
                print(f' {display_name} (x/{denominator}): '
                      f'{get_cycle_sequence_string(value).capitalize()}, next in {remaining_cooldown}d')
        print(end='\n\n')  # Extra newline


def print_longterm():
    dictionary = DB['longterm']
    groups = DB['groups']['longterm']
    groups_display = DB['groups_display']['longterm']
    if dictionary:
        print('>>> Long-term goals:', end='\n\n')
        print_groups(dictionary, groups, groups_display, print_items_generic, alpha_sort)
        print()  # Extra newline


def print_counter():
    dictionary = DB['counter']
    groups = DB['groups']['counter']
    groups_display = DB['groups_display']['counter']
    if dictionary:
        print('>>> Counters', end='\n\n')
        print_groups(dictionary, groups, groups_display, print_items_counters, alpha_sort)
        print()  # Extra newline


def print_note():
    pass


def get_cycle_sequence_string(item_value):
    display_mode = item_value['display_mode']
    if display_mode == 'number':
        return f"every {item_value['cooldown_sequence'][0]}d"
    elif display_mode == 'week_day':
        week_cooldown = item_value['week_cooldown']
        if week_cooldown == 0:
            cooldown_string = 'every'
        elif week_cooldown == 1:
            cooldown_string = 'every other'
        else:
            cooldown_string = f'every {week_cooldown + 1}'  # 2 cooldown = item occurs every 3 weeks
        return f"{cooldown_string} [{'/'.join(item_value['week_days'])}]"
    elif display_mode == 'custom':
        return item_value['frequency_description']
    else:
        quit('Invalid cycle display mode..')


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
