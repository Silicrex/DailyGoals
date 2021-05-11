import core_dict_logic
import counter_logic
import cycle_logic
import file_modification
import console_display
import date_logic
import settings

# main gets input
# -> command_flow for parameter confirmation and sorting
# -> dict_route to modify right data right way
# -> goal_modification or counter_modification
# -> core_dict_logic or counter_logic

# Don't really need the return Falses, just handle updating farther down the chain


def command_flow(line_data, user_input):
    def wrong_parameter_count(*expected):
        # Convert to list of len # instead of parameter #'s. List for pop() and list comprehension convenience
        expected = [x + 1 for x in expected]
        if input_length not in expected:
            print(f'Invalid amount of parameters (expected {expected.pop(0)}', end='')  # Pop to check for more
            if expected:  # If there are more term numbers left after popping the first one
                for value in expected:
                    print(' or', value, end='')  # Print 'or x' for them all
            print(')')  # Print the close-parenthesis and newline
            return True  # Return True, as in to say there were a wrong # of terms
        return False  # Else return False, as in not wrong #

    def invalid_parameter(parameter_number, *expected):  # Takes which parameter # and what was expected
        # expected should be a list of potential expected words
        expected = list(expected)  # List so we can use pop()
        print(f'Invalid parameter #{parameter_number}. Expected "{expected.pop(0)}"', end='')
        while expected:  # If there are more words left
            if len(expected) > 1:  # If it isn't the last one
                print(f', "{expected.pop(0)}"', end='')
            else:  # Last one
                print(f', or "{expected.pop(0)}"', end='')
        print()  # Newline

    input_length = len(user_input)
    command = user_input[0]

    # Dictionaries
    if command in {'daily', 'optional', 'todo', 'cycle', 'longterm', 'counter'}:
        if wrong_parameter_count(1, 2, 3):
            return
        mode = user_input[1]
        items = {'command': command}  # Just a misc dict for any info might need

        # Aliases other than update one
        if mode in {'c', 'r', 'd'}:
            if mode == 'c':
                mode = 'complete'
            if mode == 'r':
                mode = 'reset'
            if mode == 'd':
                mode = 'denominator'

        if command == 'counter':
            if wrong_parameter_count(2):
                return
            if mode not in {'add', 'reset', 'remove', 'retask', 'rename', 'update'} and not mode.startswith('+'):
                invalid_parameter(1, 'add', 'reset', 'remove', 'retask', 'rename', 'update')
                return

        # Seen as command, mode, second parameter, third parameter, etc.

        if mode in {'add', 'complete', 'c', 'reset', 'r', 'remove', 'retask'}:  # 2 parameters
            # ex: 'daily add wanikani'
            if wrong_parameter_count(2):
                return
            items.update({'objective_name': user_input[2]})

        elif mode == 'setall':  # 2 parameters, 2nd perm isn't obj name
            # ex: 'daily setall complete'
            if wrong_parameter_count(2):
                return
            items.update({'setall_value': user_input[2]})

        elif mode == 'update':  # 2 or 3 parameters
            # ex: 'daily update wanikani' or 'daily update wanikani 50'
            if wrong_parameter_count(2, 3):
                return
            items.update({'objective_name': user_input[2]})
            if input_length == 4:  # If an update value was specified
                items.update({'update_value': user_input[3]})
            else:  # No update value specified, default to 1, string because eval() is later
                items.update({'update_value': '1'})
        elif mode.startswith('+') and len(mode) > 1:  # Update shorthand
            # ex: 'daily +wanikani' or 'daily +wanikani 50'
            if wrong_parameter_count(1, 2):
                return
            items.update({'objective_name': mode[1:]})  # Take all chars after + as the objective name
            if input_length == 3:  # If an update value was specified
                items.update({'update_value': user_input[2]})
            else:  # Default to 1 otherwise; string because eval() is later
                items.update({'update_value': '1'})
            mode = 'update'  # Set mode to update so it's passed to the right place

        elif mode in {'rename', 'denominator'}:  # 3 parameters, extra item
            # ex: daily rename wanikani super_wow, daily denominator wanikani 2
            if wrong_parameter_count(3):
                return
            items.update({'objective_name': user_input[2]})
            items.update({'replace_value': user_input[3]})
        else:
            invalid_parameter(1, 'add', 'complete', 'reset', 'remove', 'retask', 'rename',
                              'denominator', 'setall', 'update')
            return

        dict_route(line_data, command, mode, items)
        # Saving/printing is managed in modify functions

    # elif command == 'endday':  # sadpofjd oifdS fgod FIX THIS
    #     if wrong_parameters(0):
    #         continue
    #     if daily_objectives:  # Skip all of this part if there are none
    #         all_complete = True
    #         for key, value in daily_objectives.items():
    #             # value = [task_string, denominator, numerator]
    #             objective_complete = value[2] >= value[1]  # numerator >= denominator
    #             if objective_complete:
    #                 total_completed += 1
    #             elif all_complete:  # If not set to False already
    #                 all_complete = False
    #             value[2] = 0  # Reset numerator to 0
    #         if all_complete:
    #             streak += 1
    #             if streak > best_streak:
    #                 best_streak = streak
    #         else:
    #             streak = 0
    #     if todo_objectives:
    #         remove_list = []
    #         for key, value in todo_objectives.items():
    #             # value = [task_string, denominator, numerator]
    #             objective_complete = value[2] >= value[1]  # numerator >= denominator
    #             if objective_complete:
    #                 remove_list.append(key)
    #         for key in remove_list:
    #             todo_objectives.pop(key)
    #
    #     calendar_date = date_logic.next_day(calendar_date)
    #     week_day = date_logic.next_week_day(week_day)
    #     update()
    #     print_display()

    elif command == 'dailies':
        if wrong_parameter_count(0):
            return
        console_display.print_daily_objectives(line_data)

    elif command == 'optionals':
        if wrong_parameter_count(0):
            return
        print('Optional daily objectives:')
        console_display.print_optional_objectives(line_data)

    elif command == 'todos':
        if wrong_parameter_count(0):
            return
        console_display.print_todo_objectives(line_data)

    elif command == 'cycles':
        if wrong_parameter_count(0):
            return
        console_display.print_active_cycle_objectives(line_data)
        console_display.print_inactive_cycle_objectives(line_data)

    elif command == 'longterms':
        if wrong_parameter_count(0):
            return
        console_display.print_base_dictionary(line_data)

    elif command == 'counters':
        if wrong_parameter_count(0):
            return
        console_display.print_counters(line_data['counter_dict'])

    elif command == 'print':
        if wrong_parameter_count(0):
            return
        console_display.print_display(line_data)

    elif command in {'complete', 'reset'}:
        if wrong_parameter_count(0):
            return
        core_dict_logic.change_all_dailies(line_data, command)

    elif command == 'delete':
        if wrong_parameter_count(1):
            return
        mode = user_input[1]
        if mode not in {'daily', 'optional', 'todo', 'cycle', 'longterm', 'counter', 'all'}:
            invalid_parameter(1, 'daily', 'optional', 'todo', 'cycle', 'longterm', 'counter', 'all')
            return

        core_dict_logic.clear_dictionary(line_data, mode)

        file_modification.update(line_data)
        console_display.print_display(line_data)

    # elif command == 'stats':
    #     if wrong_parameters(0):
    #         continue
    #     printing.print_stats(create_stats())
    #
    # elif command == 'settings':
    #     if wrong_parameters(0):
    #         continue
    #
    # elif command == 'toggle':
    #     if wrong_parameters(1):
    #         continue
    #     toggle_item = user_input[1]
    #     if toggle_item not in {'dateformat', 'welcome', 'longterm', 'total'}:
    #         print('Invalid 1st parameter. Expected "dateformat", "welcome", "longterm", or "total"')
    #         continue
    #     if toggle_item == 'dateformat':
    #         date_switch = loading.toggle(toggle_item, date_switch)
    #     elif toggle_item == 'welcome':
    #         welcome_toggle = loading.toggle(toggle_item, welcome_toggle)
    #     elif toggle_item == 'longterm':
    #         longterm_toggle = loading.toggle(toggle_item, longterm_toggle)
    #     elif toggle_item == 'total':
    #         total_toggle = loading.toggle(toggle_item, total_toggle)
    #     else:
    #         print('ERROR HOW WHY 624')
    #         continue
    #
    #     update()
    #     print_display()

    elif command == 'setday':
        if wrong_parameter_count(1):
            return
        input_week_day = user_input[1]
        if input_week_day not in {'sunday', 'monday', 'tuesday', 'wednesday',
                                  'thursday', 'friday', 'saturday'}:
            invalid_parameter(1, 'sunday', 'monday', 'tuesday', 'wednesday',
                              'thursday', 'friday', 'saturday')

        if not confirm_date_change():  # Returns True or False
            return

        settings.set_week_day(line_data, input_week_day)
        file_modification.update(line_data)
        console_display.print_display(line_data)

    elif command == 'setdate':
        if wrong_parameter_count(2):
            return
        input_month = int(user_input[1])
        input_day = int(user_input[2])
        calendar_date = line_data['calendar_date']
        if input_month == calendar_date[0] and input_day == calendar_date[1]:
            print('That date is already set')
            return
        if input_month > 12 or input_month < 1 or input_day > 31 or input_day < 1:
            print('Invalid inputs. Expected 1-12 range for month, 1-31 range for day')
            return
        if not date_logic.valid_date(input_month, input_day):
            print('Invalid day for that month')
            return

        if not confirm_date_change():  # Returns True or False
            return

        settings.set_date(line_data, input_month, input_day)
        file_modification.update(line_data)
        console_display.print_display(line_data)

    # elif command == 'help':
    #     printing.print_help()
    #
    # elif command == 'backup':
    #     if wrong_parameters(0):
    #         continue
    #     with open('daily_manual_backup.dat', 'w') as manual_backup:
    #         loading.back_up(manual_backup, create_line_data())
    #     print('Backup updated')

    elif command in {'exit', 'quit', 'stop'}:
        quit('Process ended')

    else:
        print('Unrecognized command')


def dict_route(line_data, command, mode, items):
    if command == 'daily':
        modify_goals(line_data, line_data['daily_objectives'], mode, items)
    elif command == 'optional':
        modify_goals(line_data, line_data['optional_objectives'], mode, items)
    elif command == 'todo':
        modify_goals(line_data, line_data['todo_objectives'], mode, items)
    elif command == 'cycle':
        if mode in {'add', 'update', 'complete', 'reset', 'setall'}:  # Needs to be handled differently for cycle
            modify_cycles(line_data, mode, items)
        else:
            modify_goals(line_data, line_data['cycle_objectives'], mode, items)
    elif command == 'longterm':
        modify_goals(line_data, line_data['longterm_objectives'], mode, items)
    elif command == 'counter':
        modify_counters(line_data, mode, items)


def modify_goals(line_data, dictionary, mode, items):
    # Requires no objective name
    if mode == 'setall':
        if not core_dict_logic.dict_setall(dictionary, items['setall_value']):
            return

    # Requires objective name
    else:
        objective_name = items['objective_name']

        if mode == 'add':
            if not core_dict_logic.add_item(line_data, dictionary, objective_name, items['command']):
                return

        # All these modes require a specific objective to exist, so check first
        if objective_name not in dictionary:
            # Returns found objective or False
            if not (objective_name := objective_search(objective_name, dictionary, line_data['auto_match_toggle'])):
                print('Item not found')
                return

        if mode == 'update':
            if not core_dict_logic.update_item(dictionary, objective_name, items['update_value']):
                return

        elif mode == 'complete':
            if not core_dict_logic.complete_item(dictionary, objective_name):
                return

        elif mode == 'reset':
            if not core_dict_logic.reset_item(dictionary, objective_name):
                return

        elif mode == 'remove':
            if not core_dict_logic.remove_item(dictionary, objective_name):
                return

        elif mode == 'rename':
            if not core_dict_logic.rename_item(line_data, dictionary, objective_name, items['replace_value'],
                                               items['command']):
                return

        elif mode == 'denominator':
            if not core_dict_logic.change_denominator(dictionary, objective_name, items['replace_value']):
                return

        elif mode == 'retask':
            if not core_dict_logic.retask_item(dictionary, objective_name):
                return

    file_modification.update(line_data)
    console_display.print_display(line_data)


def modify_cycles(line_data, mode, items):
    # Requires no objective name
    if mode == 'setall':
        pass

    else:
        dictionary = line_data['cycle_objectives']
        objective_name = items['objective_name']

        if mode == 'add':
            if not cycle_logic.add_cycle_item(line_data, objective_name):
                return

        # All these modes require a specific objective to exist, so check first
        elif objective_name not in dictionary:
            # Returns found objective or False
            if not (objective_name := objective_search(objective_name, dictionary, line_data['auto_match_toggle'])):
                print('Item not found')
                return

        elif mode == 'update':
            pass
        elif mode == 'complete':
            pass
        elif mode == 'reset':
            pass

    file_modification.update(line_data)
    console_display.print_display(line_data)


def modify_counters(line_data, mode, items):
    dictionary = line_data['counter_dict']
    objective_name = items['objective_name']

    if mode == 'add':
        if not counter_logic.add_counter_item(dictionary, objective_name):
            return

    # All these modes require a specific objective to exist, so check first
    if objective_name not in dictionary:
        # Returns found objective or False
        if not (objective_name := objective_search(objective_name, dictionary, line_data['auto_match_toggle'])):
            print('Item not found')
            return

    if mode == 'update':
        if not counter_logic.update_counter_item(dictionary, objective_name, items['update_value']):
            return

    elif mode == 'reset':
        if not counter_logic.reset_counter_item(dictionary, objective_name):
            return

    elif mode == 'remove':
        if not core_dict_logic.remove_item(dictionary, objective_name):
            return

    elif mode == 'rename':
        if not core_dict_logic.rename_item(dictionary, objective_name, items['replace_value']):
            return

    elif mode == 'retask':
        if not core_dict_logic.retask_item(dictionary, objective_name):
            return

    file_modification.update(line_data)
    # If counters are toggled to always show, then show full display instead of just counters
    if line_data['counter_toggle']:
        console_display.print_display(line_data)
    else:
        console_display.print_counters(line_data)


def objective_search(input_objective_string, dictionary, auto_match_toggle):
    objective_keys = list(dictionary.keys())
    objective_keys.sort()
    objectives_seen = set()  # Track objectives already suggested as similar
    for objective in objective_keys:
        if objective.startswith(input_objective_string):

            if auto_match_toggle:  # If the automatic match toggle is on, don't ask, just proceed
                return objective

            objectives_seen.add(objective)
            print(f"Could not find '{input_objective_string}', but found '{objective}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)')
                user_response = input().lower()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return objective
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    for objective in objective_keys:
        if objective not in objectives_seen and objective.find(input_objective_string) != -1:

            if auto_match_toggle:  # If the automatic match toggle is on, don't ask, just proceed
                return objective

            print(f"Could not find '{input_objective_string}', but found '{objective}'\n")
            while True:
                print('Is this what you meant? (y/n/cancel)')
                user_response = input().lower()
                if user_response in {'y', 'n', 'cancel'}:
                    break
            if user_response == 'y':
                return objective
            elif user_response == 'n':
                continue
            elif user_response == 'cancel':
                return False
    return False


def confirm_date_change():  # If week day or date is changed, need to clear streak/cycles
    while True:
        print('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)')
        user_input = input().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
