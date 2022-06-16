import datetime
import os  # For os.system('cls')
import documentation
import modes
import dict_management
import file_management
import settings_management
import history_interface
import date_logic
import console_display
import errors


# Command functions should take arguments (database, context, args)
# mode_route() is a generalized function for routing commands to mode functions for dicts with generic structures
# Dictionary commands ------------------------------------------------------------------------------------------
import welcome_messages


def daily_command(database, context, args):
    modes.mode_route(database, context, args)


def optional_command(database, context, args):
    modes.mode_route(database, context, args)


def todo_command(database, context, args):
    modes.mode_route(database, context, args)


def cycle_command(database, context, args):
    modes.mode_route(database, context, args)


def longterm_command(database, context, args):
    modes.mode_route(database, context, args)


def counter_command(database, context, args):
    modes.mode_route(database, context, args)


def note_command(database, context, args):
    if not len(args) > 1:
        console_display.refresh_and_print(database, 'Invalid number of parameters, expected at least 2')
        raise errors.InvalidCommandUsage('note')
    mode = args[0]
    context['mode'] = mode
    valid_modes = documentation.get_modes('note')
    if mode in valid_modes:
        mode_function = getattr(modes, mode + '_note_mode')  # ie 'add' goes to add_note_mode()
    else:
        console_display.refresh_and_print(database, 'Invalid mode')
        raise errors.InvalidCommandUsage('note')
    context['dictionary'] = database['note']
    mode_function(database, context, args)


def complete_command(database, context, args):
    # ex input: complete
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(database, context, 'complete')


def reset_command(database, context, args):
    # ex input: reset
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(database, context, 'reset')


def delete_command(database, context, args):
    # ex input: delete daily
    # ex input: delete all
    if len(args) != 1:  # Only ever one valid arg
        print('Missing argument!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    delete_mode_input = args[0]
    if delete_mode_input not in documentation.get_dictionary_names() and delete_mode_input != 'all':
        print("Invalid delete mode. Expected a dictionary name (ie daily) or 'all'", end='\n\n')
        return
    if not dict_management.delete_dictionary(database, delete_mode_input):
        return
    file_management.update(database)
    console_display.print_display(database)
    print('Successfully deleted the specified', end='\n\n')


# Display ------------------------------------------------------------------------------------------

def print_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_display(database)


def dailies_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'daily')
    console_display.print_dictionary(database, 'optional')


def optionals_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'optional')


def todos_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'todo')


def cycles_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'active_cycle')
    console_display.print_dictionary(database, 'inactive_cycle')


def longterms_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'longterm')


def counters_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary(database, 'counter')


def stats_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_stats(database)


def history_command(database, context, args):
    if len(args) != 1:
        print('Missing required argument!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    dict_name_input = args[0]
    if dict_name_input not in documentation.get_goal_dictionary_names():
        console_display.print_display(database)
        print('Invalid mode, takes goals-based dictionary as input (ie daily)', end='\n\n')
        return
    history_interface.launch_history_interface(database, dict_name_input)


def help_command(_, context, args):  # Doesn't need database
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    documentation.print_help()


# Settings ------------------------------------------------------------------------------------------

def toggle_command(database, context, args):
    # ex input: toggle
    # ex input: toggle welcome
    # ex input: toggle welcome off
    # ex input: toggle defaults
    settings = database['settings']
    arg_length = len(args)
    if arg_length > 2:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    if arg_length == 0:  # Just 'toggle'
        documentation.print_toggle_help()
        return

    toggle_name = args[0]
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
        manual_value = args[1]
        if manual_value not in {'on', 'off'}:
            print("Invalid manual value. Expected 'on' or 'off'", end='\n\n')
            return
        settings_management.toggle(database, toggle_name, manual_value)
    file_management.update(database)


def setdate_command(database, context, args):
    # ex input: setdate 5 26 2021
    if len(args) != 3:
        console_display.refresh_and_print(database, 'Invalid number of arguments, expected M D YYYY')
        raise errors.InvalidCommandUsage(context['command'])
    input_month = args[0]
    input_day = args[1]
    input_year = args[2]

    if not (input_month.isnumeric() and input_day.isnumeric() and input_year.isnumeric()):
        console_display.refresh_and_print(database, 'Invalid arg. Use numbers in the form M D YYYY, ie 3 17 2022')
        return

    month = int(input_month)
    day = int(input_day)
    year = int(input_year)

    # calendar_date = database['settings']['calendar_date']
    # if input_month == calendar_date['month'] and input_day == calendar_date['day']:
    #     print('That date is already set', end='\n\n')
    #     return
    if not (1 <= month <= 12):
        console_display.refresh_and_print(database, 'Invalid month. Expected 1-12 range')
        return
    if not (1 <= day <= 31):
        console_display.refresh_and_print(database, 'Invalid day. Expected 1-31 range')
        return
    if not date_logic.valid_date(month, day, year):
        console_display.refresh_and_print(database, 'Invalid day for that month/year')
        return

    if database['stats']['streak'] != 0 or len(database['cycle']) != 0:
        if not console_display.confirm('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)'):
            console_display.refresh_and_print(database, 'Cancelled')
            return
    database['stats']['streak'] = 0
    database['cycle'].clear()

    database['settings']['calendar_date']['month'] = month
    database['settings']['calendar_date']['day'] = day
    database['settings']['calendar_date']['year'] = year

    file_management.update(database)
    console_display.refresh_and_print(database, 'Date successfully changed')


def setday_command(database, context, args):
    # ex input: setday monday
    if len(args) != 1:
        print('Invalid number of arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    input_week_day = args[0]
    if not (week_day_number := date_logic.convert_day(input_week_day)):
        console_display.refresh_and_print(database, 'Invalid day. Enter week day name or keyword (ie Saturday)')
        return
    if database['stats']['streak'] != 0 or len(database['cycle']) != 0:
        if not console_display.confirm('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)'):
            console_display.refresh_and_print(database, 'Cancelled')
            return
    database['stats']['streak'] = 0
    database['cycle'].clear()
    database['settings']['calendar_date']['week_day'] = week_day_number

    file_management.update(database)
    console_display.refresh_and_print(database, 'Week day successfully changed')


def settings_command(database, context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    console_display.print_settings(database)


# System/file ------------------------------------------------------------------------------------------

def endday_command(database, context, args):
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
        numerator = obj_value['numerator']
        denominator = obj_value['denominator']

        command_history_dict = database['history'][dict_name]  # Corresponding history dict
        task_string = f" ({obj_value['task_string']})" if obj_value['task_string'] else ''
        denominator_string = f'{denominator:,}'
        history_name = f"{obj_value['display_name']}{task_string} (/{denominator_string})"
        history_key = history_name.lower()
        percent_completed = round(numerator / denominator, 2)  # Tracks >100% completion
        date_string = (f"{calendar_date['year']}-{calendar_date['month']:02d}-{calendar_date['day']:02d}, " 
                       f"{date_logic.convert_day_number(calendar_date['week_day'])}")  # YYYY-MM-DD, Day

        if history_key not in command_history_dict:  # Create entry
            command_history_dict.update({
                history_key: {
                    'display_name': history_name,
                    'denominator': denominator,
                    'times_completed': 0,
                    'total_percent_completed': 0,
                    'first_completed': date_string,
                    'tags': []
                }})

        # Longterm is a one-and-done structure
        if dict_name == 'longterm' and command_history_dict[history_key]['times_completed'] > 0:
            obj_value['tag'] = None
            return

        if obj_value['tag']:
            command_history_dict[history_key]['tags'].append((date_string, obj_value['tag']))
            obj_value['tag'] = None

        command_history_dict[history_key]['times_completed'] += 1
        command_history_dict[history_key]['total_percent_completed'] += percent_completed

    if args:
        console_display.refresh_and_print(database, 'Unnecessary args!')
        raise errors.InvalidCommandUsage(context['command'])

    calendar_date = database['settings']['calendar_date']
    daily_dict = database['daily']
    cycle_dict = database['cycle']
    active_cycle_dict = dict_management.get_active_cycle_dict(database)
    enforced_todo = dict_management.get_enforced_todo_dict(database)
    stats = database['stats']

    streak_deserved = True

    # Handle daily dict
    for key, value in daily_dict.items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('daily', value)
        else:
            streak_deserved = False
        value['numerator'] = 0

    # Handle optional dict
    for key, value in database['optional'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('optional', value)
        value['numerator'] = 0

    # Handle to-do dict
    todo_delete_list = []
    for key, value in database['todo'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('todo', value)
            todo_delete_list.append(key)  # Completed to-do's are deleted
        elif value['enforced_todo']:  # If it's an enforced daily to-do, that is not completed, it breaks streak
            streak_deserved = False
    for key in todo_delete_list:
        dict_management.remove_item(database, 'todo', key)

    # Handle cycle dict
    for key, value in active_cycle_dict.items():
        # value has {display_name, task_string, denominator, numerator, cycle_frequency, current_offset}
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            add_to_history('cycle', value)
        else:
            streak_deserved = False
        value['numerator'] = 0
    for key, value in cycle_dict.items():
        if value['remaining_cooldown'] == 0:  # Was an active today
            next_cooldown_index = value['cooldown_iterator']
            cooldown_sequence = value['cooldown_sequence']
            value['remaining_cooldown'] = cooldown_sequence[next_cooldown_index] - 1  # -1 to factor day change
            value['cooldown_iterator'] = dict_management.roll_over_index(next_cooldown_index, len(cooldown_sequence))
        else:
            value['remaining_cooldown'] -= 1
    dict_management.sort_dictionary(database, 'cycle')

    # Handle longterm dict
    for key, value in database['longterm'].items():
        objective_completed = value['numerator'] >= value['denominator']
        if objective_completed:
            add_to_history('longterm', value)  # Works differently; does not track stats past 'has been done'

    # Time to handle streak. First, make sure there are enforced dailies
    if len(daily_dict) + len(enforced_todo) + len(active_cycle_dict) > 0:
        if streak_deserved:
            stats['days_completed'] += 1
            stats['streak'] += 1  # Increment current streak
            if stats['streak'] > stats['best_streak']:  # Check if it's new best streak
                stats['best_streak'] = stats['streak']
        else:
            stats['streak'] = 0

    # Increment month/day/year properly
    date_logic.increment_date(database)
    # Increment week day
    calendar_date['week_day'] = date_logic.next_week_day(calendar_date['week_day'])

    # Update welcome message
    database['welcome_message'] = welcome_messages.get_welcome(current_welcome=database['welcome_message'])

    # Save, sort, and print display
    file_management.update(database)
    console_display.refresh_and_print(database, 'See you tomorrow! :D')


def backup_command(database, context, args):
    # ex input: backup
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    file_management.update(database, file_name='data_manualbackup.json')
    print('Manual backup successfully created and saved to [data_manualbackup.json]', end='\n\n')


def stop_command(_, context, args):  # Doesn't need database
    # ex input: stop
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    quit('Program terminated')


# Misc utility ------------------------------------------------------------------------------------------

def alias_format(user_input):
    # Command alias
    command_alias_dict = documentation.get_command_alias()
    command = user_input[0]
    if command in command_alias_dict:
        user_input[0] = command_alias_dict[command]  # Put full command back into input list
    # Mode alias
    if not len(user_input) > 1:
        return
    mode_alias_dict = documentation.get_mode_alias()
    mode = user_input[1]
    if mode in mode_alias_dict:
        user_input[1] = mode_alias_dict[mode]  # Put full mode back into input list
    # Update shorthand
    elif mode.startswith('+') and len(user_input[1]) > 1:  # 2nd input starts with + and is more than just +
        # ie `daily +wanikani` and `daily +wanikani 5` are the same as `daily update wanikani 5`
        # End result: replace + with 'update' and push everything else further. Works with spaced names
        user_input.insert(2, user_input[1][1:])  # Slice name connected to the + symbol, put at index 2
        # daily +wanikani 5 -> daily +wanikani wanikani 5
        user_input[1] = 'update'  # Format like full command
        # daily +wanikani wanikani 5 -> daily update wanikani 5
