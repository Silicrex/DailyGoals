import os  # For os.system('cls')
import documentation
import modes
import dict_management
import settings_management
import date_logic
import console_display
import errors
from console_display import refresh_display
from database import DB, save, get_template_dict


# Command functions should take arguments (context, args)
# mode_route() is a generalized function for routing commands to mode functions for dicts with generic structures
# Dictionary commands ------------------------------------------------------------------------------------------
import welcome_messages


def daily_command(context, args):
    modes.mode_route(context, args)


def optional_command(context, args):
    modes.mode_route(context, args)


def todo_command(context, args):
    modes.mode_route(context, args)


def cycle_command(context, args):
    modes.mode_route(context, args)


def longterm_command(context, args):
    modes.mode_route(context, args)


def counter_command(context, args):
    modes.mode_route(context, args)


# --- Disabled for now
# def note_command(context, args):
#     if not len(args) > 1:
#         console_display.refresh_and_print('Invalid number of parameters, expected at least 2')
#         raise errors.InvalidCommandUsage('note')
#     mode = args[0]
#     context['mode'] = mode
#     valid_modes = documentation.get_modes('note')
#     if mode in valid_modes:
#         mode_function = getattr(modes, mode + '_note_mode')  # ie 'add' goes to add_note_mode()
#     else:
#         console_display.refresh_and_print('Invalid mode')
#         raise errors.InvalidCommandUsage('note')
#     context['dictionary'] = DB['note']
#     mode_function(context, args)


def complete_command(context, args):
    # ex input: complete
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(context, 'complete')


def reset_command(context, args):
    # ex input: reset
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    dict_management.change_all_daily_dicts(context, 'reset')


def delete_command(context, args):
    # ex input: delete daily
    # ex input: delete all
    if len(args) != 1:  # Only ever one valid arg
        print('Missing argument!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    delete_mode_input = args[0]
    if delete_mode_input not in documentation.get_dictionary_names() and delete_mode_input != 'all':
        print("Invalid delete mode. Expected a dictionary name (ie daily) or 'all'", end='\n\n')
        return
    if not dict_management.delete_dictionary(delete_mode_input):
        return
    save()
    console_display.print_display()
    print('Successfully deleted the specified', end='\n\n')


# Display ------------------------------------------------------------------------------------------

def print_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_display()


def dailies_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('daily')
    console_display.print_dictionary('optional')


def optionals_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('optional')


def todos_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('todo')


def cycles_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('active_cycle')
    console_display.print_dictionary('inactive_cycle')


def longterms_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('longterm')


def counters_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_dictionary('counter')


def stats_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    console_display.print_stats()


def help_command(_, context, args):  # Doesn't need database
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    os.system('cls')
    documentation.print_help()


# Settings ------------------------------------------------------------------------------------------

def toggle_command(context, args):
    # ex input: toggle
    # ex input: toggle welcome
    # ex input: toggle welcome off
    # ex input: toggle defaults
    arg_length = len(args)
    if arg_length > 2:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    if arg_length == 0:  # Just 'toggle'
        documentation.print_toggle_help()
        return

    toggle_name = args[0]
    if arg_length == 1:  # Either toggling a specific setting or setting to defaults
        if toggle_name not in documentation.get_toggles():
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return
        if toggle_name == 'defaults':
            DB['settings'] = get_template_dict()['settings']
            print('Default settings restored', end='\n\n')
        else:
            settings_management.toggle(toggle_name)

    elif arg_length == 2:  # Specified setting and manual value
        if toggle_name not in documentation.get_toggles():
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return
        manual_value = args[1]
        if manual_value not in {'on', 'off'}:
            print("Invalid manual value. Expected 'on' or 'off'", end='\n\n')
            return
        settings_management.toggle(toggle_name, manual_value)
    save()


def setdate_command(context, args):
    # ex input: setdate 5 26 2021
    if len(args) != 3:
        refresh_display('Invalid number of arguments, expected M D YYYY')
        raise errors.InvalidCommandUsage(context['command'])
    input_month = args[0]
    input_day = args[1]
    input_year = args[2]

    if not (input_month.isnumeric() and input_day.isnumeric() and input_year.isnumeric()):
        refresh_display('Invalid arg. Use numbers in the form M D YYYY, ie 3 17 2022')
        return

    month = int(input_month)
    day = int(input_day)
    year = int(input_year)

    # calendar_date = DB['settings']['calendar_date']
    # if input_month == calendar_date['month'] and input_day == calendar_date['day']:
    #     print('That date is already set', end='\n\n')
    #     return
    if not (1 <= month <= 12):
        refresh_display('Invalid month. Expected 1-12 range')
        return
    if not (1 <= day <= 31):
        refresh_display('Invalid day. Expected 1-31 range')
        return
    if not date_logic.valid_date(month, day, year):
        refresh_display('Invalid day for that month/year')
        return

    if DB['stats']['streak'] != 0 or len(DB['cycle']) != 0:
        if not console_display.confirm('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)'):
            refresh_display('Cancelled')
            return
    DB['stats']['streak'] = 0
    DB['cycle'].clear()

    DB['settings']['calendar_date']['month'] = month
    DB['settings']['calendar_date']['day'] = day
    DB['settings']['calendar_date']['year'] = year

    save()
    refresh_display('Date successfully changed')


def setday_command(context, args):
    # ex input: setday monday
    if len(args) != 1:
        print('Invalid number of arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    input_week_day = args[0]
    if not (week_day_number := date_logic.convert_day(input_week_day)):
        refresh_display('Invalid day. Enter week day name or keyword (ie Saturday)')
        return
    if DB['stats']['streak'] != 0 or len(DB['cycle']) != 0:
        if not console_display.confirm('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)'):
            refresh_display('Cancelled')
            return
    DB['stats']['streak'] = 0
    DB['cycle'].clear()
    DB['settings']['calendar_date']['week_day'] = week_day_number

    save()
    refresh_display('Week day successfully changed')


def settings_command(context, args):
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    console_display.print_settings()


# System/file ------------------------------------------------------------------------------------------

def endday_command(context, args):
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

    if args:
        refresh_display('Unnecessary args!')
        raise errors.InvalidCommandUsage(context['command'])

    daily_dict = DB['daily']
    cycle_dict = DB['cycle']
    active_cycle_dict = dict_management.get_active_cycle()
    stats = DB['stats']

    # Handle streak
    if dict_management.get_daily_count() > 0:  # There must be at least one daily item
        streak_deserved = dict_management.check_streak()
        if not streak_deserved and DB['settings']['end_day_warning']:
            if not console_display.confirm('Not all dailies have been completed. Proceed? (y/n)'):
                refresh_display('Cancelled')
                return
        if streak_deserved:
            stats['days_completed'] += 1
            stats['streak'] += 1  # Increment current streak
            if stats['streak'] > stats['best_streak']:  # Check if it's new best streak
                stats['best_streak'] = stats['streak']
        else:
            stats['streak'] = 0

    # Handle daily dict
    for key, obj_value in daily_dict.items():
        objective_completed = obj_value['numerator'] >= obj_value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            obj_value['streak'] += 1
        else:
            obj_value['streak'] = 0
        dict_management.add_to_history('daily', obj_value)
        obj_value['numerator'] = 0

    # Handle optional dict
    for key, obj_value in DB['optional'].items():
        objective_completed = obj_value['numerator'] >= obj_value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            obj_value['streak'] += 1
        else:
            obj_value['streak'] = 0
        dict_management.add_to_history('optional', obj_value)
        obj_value['numerator'] = 0

    # Handle to-do dict
    todo_delete_list = []
    for key, obj_value in DB['todo'].items():
        objective_completed = obj_value['numerator'] >= obj_value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            todo_delete_list.append(key)  # Completed to-do's are deleted
        dict_management.add_to_history('todo', obj_value)
    for key in todo_delete_list:
        dict_management.remove_item('todo', key)

    # Handle cycle dict
    for key, obj_value in active_cycle_dict.items():
        objective_completed = obj_value['numerator'] >= obj_value['denominator']
        if objective_completed:
            stats['total_completed'] += 1
            obj_value['streak'] += 1
        else:
            obj_value['streak'] = 0
        dict_management.add_to_history('cycle', obj_value)
        obj_value['numerator'] = 0
    for key, obj_value in cycle_dict.items():
        if obj_value['remaining_cooldown'] == 0:  # Was an active today
            next_cooldown_index = obj_value['cooldown_iterator']
            cooldown_sequence = obj_value['cooldown_sequence']
            obj_value['remaining_cooldown'] = cooldown_sequence[next_cooldown_index] - 1  # -1 to factor day change
            obj_value['cooldown_iterator'] = dict_management.roll_over_index(next_cooldown_index,
                                                                             len(cooldown_sequence))
        else:
            obj_value['remaining_cooldown'] -= 1

    # Handle longterm dict
    for key, obj_value in DB['longterm'].items():
        dict_management.add_to_history('longterm', obj_value)

    # Handle counter dict
    for key, obj_value in DB['counter'].items():
        dict_management.add_to_history('counter', obj_value)

    # Increment month/day/year & week day
    date_logic.increment_date()

    # Update welcome message
    DB['welcome_message'] = welcome_messages.get_welcome(current_welcome=DB['welcome_message'])

    # Save, sort, and print display
    save()
    refresh_display('See you tomorrow! :D')


def backup_command(context, args):
    # ex input: backup
    if args:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'])
    save(file_name='data_manualbackup.json')
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
        # ie `daily +itemname 5` is the same as `daily update itemname 5`
        # End result: replace + with 'update' and push everything else further. Works with spaced names
        user_input.insert(2, user_input[1][1:])  # Slice name connected to the + symbol, put at index 2
        # daily +itemname 5 -> daily +itemname itemname 5
        user_input[1] = 'update'  # Format like full command
        # daily +itemname itemname 5 -> daily update itemname 5
