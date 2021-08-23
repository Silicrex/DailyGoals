import datetime
import os  # For os.system('cls')
import documentation
import item_management
import dict_management
import file_management
import settings_management
import history_interface
import date_logic
import console_display
import exceptions


# Command functions should take arguments (database, context, *extra_input)
# Dictionary commands ------------------------------------------------------------------------------------------

def daily_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def optional_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def todo_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def cycle_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def longterm_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def counter_command(database, context, *extra_input):
    mode_route(database, context, *extra_input)


def note_command(database, context, *extra_input):
    if not len(extra_input) > 1:
        print('Invalid number of parameters, expected at least 2', end='\n\n')
        return
    mode = context['mode']
    valid_modes = documentation.get_modes('note')
    if mode in valid_modes:
        mode_function = getattr(item_management, mode + '_note_mode')  # ie 'add' goes to add_note_mode()
    else:
        console_display.print_display(database)
        print('Invalid mode', end='\n\n')
        return
    dictionary = database['note']
    if not mode_function(database, dictionary, *extra_input):
        return
    # Save and print display
    file_management.update(database)
    console_display.print_display(database)
    print_mode_success(mode)


def mode_route(database, context, *extra_input):
    if not extra_input:  # Needs to at least have a mode specified
        print('Mode must be given', end='\n\n')
        return
    command = context['command']  # To know which dict we're working with
    mode = extra_input[0]
    context['mode'] = mode
    valid_modes = documentation.get_modes(command)  # Returns set of valid modes for given dict command
    if mode in valid_modes:  # If valid mode, retrieve corresponding function
        mode_function = getattr(item_management, mode + '_mode')  # ie 'add' goes to add_mode()
    else:
        console_display.print_display(database)
        print('Invalid mode', end='\n\n')
        return
    dictionary = database[command]  # ie 'daily' gets 'daily' dict
    if not mode_function(database, context, dictionary, *extra_input[1:]):  # Expand input past mode as args (if any)
        return
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.print_display(database)
    print_mode_success(mode)  # To leave success print after everything else


def complete_command(database, context, *extra_input):
    # ex input: complete
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(database, 'complete')


def reset_command(database, context, *extra_input):
    # ex input: reset
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(database, 'reset')


def delete_command(database, context, *extra_input):
    # ex input: delete daily
    # ex input: delete all
    if len(extra_input) != 1:  # Only ever one valid arg
        print('Missing argument!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    delete_mode_input = extra_input[0]
    if delete_mode_input not in documentation.get_dictionary_names() and delete_mode_input != 'all':
        print("Invalid delete mode. Expected a dictionary name (ie daily) or 'all'", end='\n\n')
        return
    if not dict_management.delete_dictionary(database, delete_mode_input):
        return
    file_management.update(database)
    console_display.print_display(database)
    print('Successfully deleted the specified', end='\n\n')


# Display ------------------------------------------------------------------------------------------

def print_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_display(database)


def dailies_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'daily')
    console_display.print_dictionary(database, 'optional')


def optionals_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'optional')


def todos_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'todo')


def cycles_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'active_cycle')
    console_display.print_dictionary(database, 'inactive_cycle')


def longterms_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'longterm')


def counters_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'counter')


def stats_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_stats(database)


def history_command(database, context, *extra_input):
    if len(extra_input) != 1:
        print('Missing argument!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    dict_name_input = extra_input[0]
    if dict_name_input not in documentation.get_goal_dictionary_names():
        print('Invalid mode, takes goals-based dictionary as input (ie daily)', end='\n\n')
        return
    history_interface.launch_history_interface(database, dict_name_input)


def help_command(_, context, *extra_input):  # Doesn't need database
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    os.system('cls')
    documentation.print_help()


# Settings ------------------------------------------------------------------------------------------

def toggle_command(database, context, *extra_input):
    # ex input: toggle
    # ex input: toggle welcome
    # ex input: toggle welcome off
    # ex input: toggle defaults
    settings = database['settings']
    arg_length = len(extra_input)
    if arg_length > 2:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    if arg_length == 0:  # Just 'toggle'
        documentation.print_toggle_help()
        return

    toggle_name = extra_input[0]
    if arg_length == 1:  # Either toggling a specific setting or setting to defaults
        if toggle_name in settings:
            settings_management.toggle(database, toggle_name)
        elif toggle_name == 'defaults':
            database['settings'] = file_management.get_template_dict()['settings']
            print('Default settings restored', end='\n\n')
        else:
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return

    elif arg_length == 2:  # Specified setting and manual value
        if toggle_name not in settings:
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return
        manual_value = extra_input[1]
        if manual_value not in {'on', 'off'}:
            print("Invalid manual value. Expected 'on' or 'off'", end='\n\n')
            return
        settings_management.toggle(database, toggle_name, manual_value)
    file_management.update(database)


def setdate_command(database, context, *extra_input):
    # ex input: setdate 5 26
    # ex input: setdate 8
    arg_length = len(extra_input)
    if arg_length not in {1, 2}:
        print('Invalid number of arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    input_month = extra_input[0]
    if arg_length == 1:  # Default day to 1
        input_day = '1'  # Converted to int later
    else:
        input_day = extra_input[1]

    if not input_month.isnumeric():
        print('Invalid month. Use numbers in the form MM DD, ie 5 27', end='\n\n')
        return
    if not input_day.isnumeric():
        print('Invalid day. Use numbers in the form MM DD, ie 5 27', end='\n\n')
        return

    input_month = int(input_month)
    input_day = int(input_day)

    calendar_date = database['settings']['calendar_date']
    if input_month == calendar_date['month'] and input_day == calendar_date['day']:
        print('That date is already set', end='\n\n')
        return
    if input_month > 12 or input_month < 1:
        print('Invalid input. Expected 1-12 range for month', end='\n\n')
        return
    if input_day > 31 or input_day < 1:
        print('Invalid input. Expected 1-31 range for day', end='\n\n')
        return
    if not date_logic.valid_date(input_month, input_day):
        print('Invalid day for that month', end='\n\n')
        return

    if not settings_management.force_date_change_prompt(database):  # If they confirm; streak reset, cycles deleted
        console_display.print_display(database)
        return

    database['settings']['calendar_date']['month'] = input_month
    database['settings']['calendar_date']['day'] = input_day

    file_management.update(database)
    console_display.print_display(database)
    print('Date successfully changed', end='\n\n')


def setday_command(database, context, *extra_input):
    # ex input: setday monday
    if len(extra_input) != 1:
        print('Invalid number of arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    input_week_day = extra_input[0]
    if input_week_day not in date_logic.get_week_days():
        print('Invalid day. Enter week day name (ie saturday)', end='\n\n')
        return
    if not settings_management.force_date_change_prompt(database):  # If they confirm; streak reset, cycles deleted
        # Else just return to menu
        console_display.print_display(database)
        return

    week_day_number = date_logic.convert_day(input_week_day)  # Convert to #, ie Sunday = 1
    database['settings']['calendar_date']['week_day'] = week_day_number

    file_management.update(database)
    console_display.print_display(database)
    print('Week day successfully changed', end='\n\n')


def settings_command(database, context, *extra_input):
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    console_display.print_settings(database)


# System/file ------------------------------------------------------------------------------------------


def endday_command(database, context, *extra_input):
    # ex input: endday
    # deserve streak point? (check for completion across dailies)
    # increment total dailies completed
    # reset all
    # delete completed todo's
    # adjust cycle offset
    # add to history
    # adjust date/weekday
    # Dicts: daily, optional, todo, cycle, longterm, counter, note, history
    # Streak point: daily, cycle
    # Total dailies completed: daily, optional, todo, cycle
    def add_to_history(dict_name, obj_value):
        obj_numerator = obj_value['numerator']
        obj_denominator = obj_value['denominator']

        history_dict = database['history'][dict_name]
        task_string = f" ({obj_value['task_string']})" if obj_value['task_string'] else ''
        denominator_string = '{:,}'.format(obj_denominator)
        history_key = f"{obj_value['display_name']}{task_string} (/{denominator_string})"
        history_key_lower = history_key.lower()

        if dict_name == 'longterm':  # Longterm is a one-and-done structure
            if history_key_lower in history_dict:
                return
            else:  # First time, so create entry
                first_completed = datetime.datetime.now().date()
                history_dict.update({history_key_lower: {'display_name': history_key,
                                                         'first_completed': str(first_completed)}})
                return

        if history_key_lower in history_dict:
            history_value = history_dict[history_key_lower]
            percent_completed = round(obj_numerator / obj_denominator, 2)  # Tracks >100% comp
            history_value['total_percent_completed'] += percent_completed
            history_value['times_completed'] += 1
        else:  # First time, so create entry
            percent_completed = round(obj_numerator/obj_denominator, 2)  # Tracks >100% completion
            first_completed = datetime.datetime.now().date()
            history_dict.update({history_key_lower: {'display_name': history_key, 'times_completed': 1,
                                                     'denominator': obj_denominator,
                                                     'total_percent_completed': percent_completed,
                                                     'first_completed': str(first_completed)}})

    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])

    daily_dict = database['daily']
    cycle_dict = database['cycle']
    active_cycle_list = dict_management.get_active_cycle_list(database)
    stats = database['stats']

    streak_deserved = True

    # key represents lowercase objective name
    # value is a dict with {display_name, task_string, denominator, numerator}, unless specified otherwise
    for key, value in daily_dict.items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('daily', value)
        else:
            streak_deserved = False
        value['numerator'] = 0
    for key, value in database['optional'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('optional', value)
        value['numerator'] = 0
    todo_delete_list = []
    for key, value in database['todo'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('todo', value)
            todo_delete_list.append(key)  # Completed to-do's are deleted
        elif value['enforced_daily']:  # If it's an enforced daily to-do, that is not completed, it breaks streak
            streak_deserved = False
    for key in todo_delete_list:
        database['todo'].pop(key)
    for key in active_cycle_list:
        # value has {display_name, task_string, denominator, numerator, cycle_frequency, current_offset}
        value = cycle_dict[key]
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('cycle', value)
        else:
            streak_deserved = False
        value['numerator'] = 0
    for key, value in cycle_dict.items():
        if value['current_offset'] == 0:  # Was an active today
            value['current_offset'] = value['cycle_frequency'] - 1  # Then reset; -1 to account for date switching now
        else:
            value['current_offset'] -= 1
    dict_management.sort_dictionary(database, 'cycle')
    for key, value in database['longterm'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            add_to_history('longterm', value)  # Works differently; does not track stats past 'has been done'

    # Time to handle streak
    if len(daily_dict) + len(active_cycle_list) > 0:  # If there are none, then ignore streak for the day
        if streak_deserved:
            stats['days_completed'] += 1
            stats['streak'] += 1  # Increment current streak
            if stats['streak'] > stats['best_streak']:  # Check if it's new best streak
                stats['best_streak'] = stats['streak']
        else:
            stats['streak'] = 0

    # Time to handle date
    calendar_date = database['settings']['calendar_date']
    # Increment month/day properly
    calendar_date['month'], calendar_date['day'] = date_logic.next_day(calendar_date['month'], calendar_date['day'])
    # Increment week day
    calendar_date['week_day'] = date_logic.next_week_day(calendar_date['week_day'])

    # Save, sort, and print display
    file_management.update(database)
    console_display.print_display(database)
    print_mode_success('endday')  # To leave success print after everything else


def backup_command(database, context, *extra_input):
    # ex input: backup
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    file_management.update(database, file_name='data_manualbackup.json')
    print('Manual backup successfully created and saved to [data_manualbackup.json]', end='\n\n')


def stop_command(_, context, *extra_input):  # Doesn't need database
    # ex input: stop
    if extra_input:
        print('Unnecessary arguments!', end='\n\n')
        raise exceptions.InvalidCommandUsage(context['command'])
    quit('Program terminated')


# Misc utility ------------------------------------------------------------------------------------------

def alias_format(user_input):
    # Command alias
    command_alias_dict = documentation.get_command_alias()
    if user_input[0] in command_alias_dict:
        user_input[0] = command_alias_dict[user_input[0]]
    # Mode alias
    if not len(user_input) > 1:
        return
    mode_alias_dict = documentation.get_mode_alias()
    if user_input[1] in mode_alias_dict:  # Replace alias with corresponding mode
        user_input[1] = mode_alias_dict[user_input[1]]
    # Update shorthand; format of dict +x
    elif user_input[1].startswith('+') and len(user_input[1]) > 1:  # 2nd input starts with + and is more than 1 char
        # ie daily +wanikani; daily +wanikani 5 should be daily update wanikani 5
        # End result: replace + with 'update' and push everything else further. Works with spaced names
        user_input.insert(2, user_input[1][1:])  # Splice after the + symbol, put at index 2
        user_input[1] = 'update'  # Make like daily update <name>, which defaults to +1


def print_mode_success(mode):
    if mode in {'complete', 'reset', 'rename', 'retask', 'denominator', 'set', 'position', 'edit'}:
        mode = 'update'  # All have the same print message
    mode_success_dict = {
        'add': 'Item successfully added',
        'update': 'Item successfully updated',
        'setall': 'Dictionary successfully updated',
        'swap': 'Items successfully updated',
        'remove': 'Item successfully removed',
        'endday': 'Day successfully ended!! See you next time!'
    }
    print(mode_success_dict[mode], end='\n\n')
