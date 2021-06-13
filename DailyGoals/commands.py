import documentation
import item_management
import dict_management
import file_management
import settings_management
import history_management
import date_logic
import console_display


# Command functions should take arguments (database, user_input)
# Dictionary commands ------------------------------------------------------------------------------------------

def daily_command(database, user_input):
    mode_route(database, user_input)


def optional_command(database, user_input):
    mode_route(database, user_input)


def todo_command(database, user_input):
    mode_route(database, user_input)


def cycle_command(database, user_input):
    mode_route(database, user_input)


def longterm_command(database, user_input):
    mode_route(database, user_input)


def counter_command(database, user_input):
    mode_route(database, user_input)


def note_command(database, user_input):
    if not len(user_input) > 1:
        print('Invalid number of parameters, expected at least 2', end='\n\n')
        return
    mode = user_input[2]
    valid_modes = documentation.get_modes('note')
    if mode in valid_modes:
        mode_function = getattr(item_management, 'note_' + mode + '_mode')  # ie 'add' goes to note_add_mode()
    else:
        print('Invalid mode', end='\n\n')
        return
    if not mode_function(database, user_input):
        return
    # Save and print display
    file_management.update(database)
    console_display.print_display(database)
    print_mode_success(mode)


def mode_route(database, user_input):
    if not len(user_input) > 1:
        print('Invalid number of parameters, expected at least 2', end='\n\n')
        return
    command = user_input[0]  # To know which dict we're working with
    mode = user_input[1]
    valid_modes = documentation.get_modes(command)  # Returns set of valid modes for given dict command
    if mode in valid_modes:
        mode_function = getattr(item_management, mode + '_mode')  # ie 'add' goes to add_mode()
    else:
        print('Invalid mode', end='\n\n')
        return
    dictionary = database['command']
    items = {  # Pack it up so modes can be more flexible about what parameters they actually use
        'database': database,
        'dictionary': dictionary,
        'command': command,
        'mode': mode,
        'parameters': user_input[2:],  # Everything after mode
    }
    if not mode_function(items):
        return
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.print_display(database)
    print_mode_success(mode)


def complete_command(database, user_input):
    # ex input: complete
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    dict_management.change_all_daily_dicts(database, 'complete')


def reset_command(database, user_input):
    # ex input: reset
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    dict_management.change_all_daily_dicts(database, 'reset')


def delete_command(database, user_input):
    # ex input: delete daily
    # ex input: delete all
    if dict_management.wrong_parameter_count(len(user_input), 2):
        return
    delete_mode_input = user_input[1]
    if delete_mode_input not in documentation.get_dictionary_names() and delete_mode_input != 'all':
        print("Invalid delete mode. Expected a dictionary name (ie daily) or 'all'", end='\n\n')
        return
    if not dict_management.delete_dictionary(database, delete_mode_input):
        return
    file_management.update(database)
    console_display.print_display(database)
    print('Successfully deleted the specified', end='\n\n')


# Display ------------------------------------------------------------------------------------------

def print_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_display(database)


def dailies_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'daily')
    console_display.print_dictionary(database, 'optional')


def optionals_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'optional')


def todos_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'todo')


def cycles_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'active_cycle')
    console_display.print_dictionary(database, 'inactive_cycle')


def longterms_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'longterm')


def counters_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_dictionary(database, 'counter')


def stats_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_stats(database)


def history_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 2):
        return
    dict_name_input = user_input[1]
    if dict_name_input not in documentation.get_goal_dictionary_names():
        print('Invalid mode, takes goals-based dictionary as input (ie daily)', end='\n\n')
        return
    history_management.launch_history_interface(database, dict_name_input)


def help_command(_, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    documentation.print_help()


# Settings ------------------------------------------------------------------------------------------

def toggle_command(database, user_input):
    # ex input: toggle
    # ex input: toggle welcome
    # ex input: toggle welcome off
    # ex input: toggle defaults
    settings = database['settings']
    input_length = len(user_input)
    if dict_management.wrong_parameter_count(input_length, 1, 2, 3):
        return
    if input_length == 1:  # Just 'toggle'
        documentation.print_toggle_help()
        return

    toggle_input = user_input[1]
    if input_length == 2:  # Either toggling a specific setting or setting to defaults
        if toggle_input in settings:
            settings_management.toggle(database, toggle_input)
        elif toggle_input == 'defaults':
            database['settings'] = file_management.get_template_dict()['settings']
            print('Default settings restored', end='\n\n')
        else:
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return

    elif input_length == 3:  # Specified setting and manual value
        if toggle_input not in settings:
            print("Invalid setting. See keywords with 'toggle'", end='\n\n')
            return
        manual_value = user_input[2]
        if manual_value not in {'on', 'off'}:
            print("Invalid manual value (3rd input). Expected 'on' or 'off'", end='\n\n')
            return
        settings_management.toggle(database, toggle_input, manual_value)
    file_management.update(database)


def setdate_command(database, user_input):
    # ex input: setdate 5 26
    if dict_management.wrong_parameter_count(len(user_input), 3):
        return
    input_month = user_input[1]
    input_day = user_input[2]

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


def setday_command(database, user_input):
    # ex input: setday monday
    if dict_management.wrong_parameter_count(len(user_input), 2):
        return
    input_week_day = user_input[1]
    if input_week_day not in date_logic.get_week_days():
        print('Invalid day. Enter week day name (ie saturday)', end='\n\n')
        return
    if not settings_management.force_date_change_prompt(database):  # If they confirm; streak reset, cycles deleted
        console_display.print_display(database)
        return

    week_day_number = date_logic.convert_day(input_week_day)  # Convert to #, ie Sunday = 1
    database['settings']['calendar_date']['week_day'] = week_day_number

    file_management.update(database)
    console_display.print_display(database)
    print('Week day successfully changed', end='\n\n')


def settings_command(database, user_input):
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    console_display.print_settings(database)


# System/file ------------------------------------------------------------------------------------------


def endday_command(database, user_input):
    # ex input: endday
    # deserve streak point?
    # reset all
    # delete completed todo's
    # adjust cycle offset
    # add to history
    # adjust date/weekday
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return


def backup_command(database, user_input):
    # ex input: backup
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
    file_management.update(database, file_name='data_manualbackup.json')
    print('Manual backup successfully created and saved to [data_manualbackup.json]', end='\n\n')


def stop_command(_, user_input):
    # ex input: stop
    if dict_management.wrong_parameter_count(len(user_input), 1):
        return
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
    elif user_input[1].startswith('+') and len(user_input[1]) > 1:  # Update shorthand, format of +x
        input_length = len(user_input)
        # ie daily +wanikani, daily +wanikani 5, should be daily update wanikani 5
        if input_length == 2:  # Looking for daily +name
            user_input.append(user_input[1][1:])  # Splice after the + symbol, put at index 2
            user_input[1] = 'update'  # Make like daily update <name>, which defaults to +1
        elif input_length == 3:  # Looking for daily +name 5
            user_input.append(user_input[2])  # Take update value, move to index 3, ie [daily, +name, 5, 5]
            user_input[2] = user_input[1][1:]  # Splice after + symbol
            user_input[1] = 'update'  # Like [daily, update, name, 2]


def print_mode_success(mode):
    if mode in {'complete', 'reset', 'rename', 'retask', 'denominator', 'set', 'position', 'edit'}:
        mode = 'update'  # All have the same print message
    mode_success_dict = {
        'add': 'Item successfully added',
        'update': 'Item successfully updated',
        'setall': 'Dictionary successfully updated',
        'swap': 'Items successfully updated',
        'remove': 'Item successfully removed',
    }
    print(mode_success_dict[mode], end='\n\n')


# def invalid_parameter(parameter_number, *expected):  # Takes which parameter # and what was expected
#     # expected should be a list of potential expected words
#     expected = list(expected)  # List so we can use pop()
#     print(f'Invalid parameter #{parameter_number}. Expected "{expected.pop(0)}"', end='')
#     while expected:  # If there are more words left
#         if len(expected) > 1:  # If it isn't the last one
#             print(f', "{expected.pop(0)}"', end='')
#         else:  # Last one
#             print(f', or "{expected.pop(0)}"', end='')
#     print()  # Newline
