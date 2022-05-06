import dict_management
import file_management
import date_logic
import console_display
import documentation
import errors


# Base core dict functions need to take (database, context, args)
# Return False = abort, return True = sort and save

def mode_route(database, context, args):
    command = context['command']
    if not args:  # Needs to at least have a mode specified
        console_display.refresh_and_print(database, 'Mode must be given')
        raise errors.InvalidCommandUsage(command)
    mode = args[0]
    context['mode'] = mode
    valid_modes = documentation.get_modes(command)  # Returns set of valid modes for given dict command
    if mode in valid_modes:  # If valid mode, retrieve corresponding function
        mode_function = globals()[mode + '_mode']  # ie 'add' goes to add_mode()
    else:
        console_display.refresh_and_print(database, 'Invalid mode')
        raise errors.InvalidCommandUsage(command)
    mode_function(database, context, args[1:])  # Mode was args[0]


# Adding items ------------------------------------------------------------------------------------------
def add_mode(database, context, args):
    # ex input: daily add
    command = context['command']
    dictionary = database[command]

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if command in {'counter', 'cycle', 'todo'}:  # Different processes
        special_add_function = globals()['add_' + command + '_mode']  # ie add_cycle_mode, gets corresponding func
        special_add_function(database, dictionary)
        return

    objective_name = get_name()
    objective_key = objective_name.lower()
    if objective_key in dictionary:
        console_display.refresh_and_print(database, 'Objective by that name already exists. Returning to menu')
        return
    task_string = get_task_string()
    denominator = get_denominator()
    dictionary.update({objective_key: {'display_name': objective_name, 'task_string': task_string,
                                       'denominator': denominator, 'numerator': 0, 'link': [[], []],
                                       'tag': None}})
    dict_management.add_to_container(database, command, objective_key)  # Add to default container
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully added!')


def add_cycle_mode(database, dictionary):
    objective_name = get_name()
    objective_key = objective_name.lower()
    if objective_key in dictionary:
        console_display.refresh_and_print(database, 'Objective by that name already exists. Returning to menu')
        return
    task_string = get_task_string()
    denominator = get_denominator()

    print('> Enter a frequency (every x days) or a week day name', end='\n\n')
    frequency = input().lower()
    print()  # Newline
    # Going by day name automatically fills day frequency and offset
    if frequency in date_logic.get_week_days():
        current_week_day = database['week_day']
        input_week_day = date_logic.convert_day(frequency)
        cycle_frequency = 7  # If a day is specified, it's weekly
        current_offset = input_week_day - current_week_day  # Diff between given day and today
    elif frequency.isnumeric():  # A number was given, not specific day
        cycle_frequency = eval(frequency)
        if cycle_frequency == 0:
            console_display.refresh_and_print(database, 'Item frequency cannot be 0. Returning to menu')
            return
        print('> Enter offset until next occurrence (ie 0 if today, 1 if tomorrow)', end='\n\n')
        current_offset = eval(input())
    else:  # Neither a weekday nor integer were given
        console_display.refresh_and_print(database, 'Invalid input. Expected day name or day offset integer. '
                                                    'Returning to menu.')
        return

    dictionary.update({objective_key: {'display_name': objective_name, 'task_string': task_string,
                                       'denominator': denominator, 'numerator': 0,
                                       'cycle_frequency': cycle_frequency, 'current_offset': current_offset,
                                       'link': [[], []], 'tag': None}})
    dict_management.add_to_container(database, 'cycle', objective_key)  # Add to default container
    # Save, sort, and print display
    dict_management.sort_dictionary(database, 'cycle')
    file_management.update(database)
    console_display.refresh_and_print(database, 'Cycle item successfully added!')


def add_counter_mode(database, dictionary):
    objective_name = get_name()
    objective_key = objective_name.lower()
    if objective_key in dictionary:
        console_display.refresh_and_print(database, 'Counter by that name already exists. Returning to menu')
        return
    task_string = get_task_string()
    dictionary.update({objective_key: {'display_name': objective_name, 'task_string': task_string,
                                       'numerator': 0, 'link': [[], []]}})
    dict_management.add_to_container(database, 'counter', objective_key)  # Add to default container
    # Save, sort, and print display
    dict_management.sort_dictionary(database, 'counter')
    file_management.update(database)
    console_display.refresh_and_print(database, 'Counter item successfully added!')


def add_todo_mode(database, dictionary):
    objective_name = get_name()
    objective_key = objective_name.lower()
    if objective_key in dictionary:
        console_display.refresh_and_print(database, 'Objective by that name already exists. Returning to menu')
        return
    task_string = get_task_string()
    denominator = get_denominator()
    if console_display.confirm('> Should this todo objective count towards daily requirement? (y/n)'):
        enforced_todo = True
    else:
        enforced_todo = False
    dictionary.update({objective_key: {'display_name': objective_name, 'task_string': task_string,
                                       'denominator': denominator, 'numerator': 0,
                                       'enforced_todo': enforced_todo, 'link': [[], []], 'tag': None}})
    dict_management.add_to_container(database, 'todo', objective_key)  # Add to default container
    # Save, sort, and print display
    dict_management.sort_dictionary(database, 'todo')
    file_management.update(database)
    console_display.refresh_and_print(database, 'Todo item successfully added!')


def add_note_mode(database, context, args):
    # ex input: note add
    # ex input: note add 0
    if len(args) > 1:
        print('Unnecessary arguments!', end='\n\n')
        raise errors.InvalidCommandUsage('note', 'add')

    dictionary = database[context['command']]
    note_count = len(dictionary)
    if args:
        note_index = args[0]
        try:
            note_index = eval(note_index)
        except (NameError, SyntaxError):
            print('Invalid index', end='\n\n')
            raise errors.InvalidCommandUsage('note', 'add')
        if not isinstance(note_index, int):
            print('Invalid index', end='\n\n')
            raise errors.InvalidCommandUsage('note', 'add')

        if note_index > note_count - 1:  # If specified index is higher than list length, bump down to end index
            print('Index adjusted as given value was higher than list length')
            note_index = note_count
    else:
        note_index = note_count  # If no index specified, default to end of list
    while True:
        print(f'Enter note for index [{note_index}]:', end='\n\n')
        note_input = input()  # Lower for string comparisons
        if not note_input:  # It's possible to enter nothing
            continue
        if not note_input.isascii():
            print('Please only use ASCII characters')
            continue
        break
    dictionary.insert(note_index, note_input)
    ### add_to_container(database, 'note', objective_key)
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, 'Note item successfully added!')


def get_name(prompt='> Enter a name for the objective (must be unique to goal type)'):
    while True:
        print(prompt, end='\n\n')
        name = input().strip()  # Get input and remove leading/trailing spaces
        print()  # Extra newline
        if not name:
            print('Name cannot be blank')
            continue
        if not name.isascii():
            print('Please only use ASCII characters')
            continue
        return name


def get_task_string():
    while True:
        print('> Enter a brief task description/couple keywords; can be blank', end='\n\n')
        task_string = input()

        if not task_string:  # If it's empty, that's fine, but print something to signify
            print('Task string skipped')

        print()  # Extra newline
        if not task_string.isascii():
            print('Please only use ASCII characters')
            continue
        return task_string


def get_denominator():
    while True:
        print('> Enter a progress denominator (ie 2 becomes 0/2) (blank defaults to 1)', end='\n\n')
        denominator = input()
        print()  # Extra newline

        if denominator == '':  # Default to 1
            return 1
        if not (denominator := format_integer(denominator)):
            continue
        if denominator < 0:  # Case of 0 is already handled in format_integer(), but not negatives
            print('Denominator must be greater than 0')
            continue
        return denominator


# Updating/editing items ------------------------------------------------------------------------------------------
def update_mode(database, context, args):
    # ex input: daily update wanikani 50
    # ex input: daily update clean dishes

    # Spaces in names complicates. Prioritize searching for objective name over valid update value.
    # Can have a case where obj name is something like "Do number 9". Command could potentially be
    # "daily update do number 9" to increment it by one, or "daily update do number 9 1" for specified.

    command = context['command']  # Cycle handled differently
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to update')
        raise errors.InvalidCommandUsage(command, context['mode'])

    full_string = ' '.join(args).lower()  # Lowercase string of entire rest of input
    # Search for full string as an objective name; assuming no update value specified
    if (objective_name := dict_management.key_search(database, dictionary, full_string)) in dictionary:
        update_value = '1'  # str because format_integer takes a string
    else:  # Objective wasn't found. Assume update value was specified
        sub_string = ' '.join(args[:-1]).lower()  # Last element should be update value
        if not (objective_name := dict_management.key_search(database, dictionary, sub_string)):
            console_display.refresh_and_print(database, 'Objective name not found')
            raise errors.InvalidCommandUsage(command, context['mode'])
        update_value = args[-1]  # Worked out this way, proceed

    # Validate/format update value from str to int
    if not (update_value := format_integer(update_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        console_display.refresh_and_print(database, 'Invalid update value')
        raise errors.InvalidCommandUsage(command, context['mode'])  # Invalid update value

    if command == 'cycle':  # Can't update inactive item
        if objective_name not in dict_management.get_active_cycle_dict(database):
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle objectives')
            return

    dict_management.update_item(database, dictionary, objective_name, update_value)

    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully updated!')


def set_mode(database, context, args):
    # ex input: daily set wanikani 50

    command = context['command']  # Cycle handled differently
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to update and set value')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args[:-1]).lower()  # Last element should be set value
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if not (set_value := format_integer(args[-1])):  # Enforces non-zero integer. Accepts extension ie 1k
        console_display.refresh_and_print(database, 'Invalid set value')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_dict(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle objectives')
            return

    current_value = dictionary[objective_name]['numerator']
    difference = set_value - current_value  # Used to make handling links easier
    dict_management.update_item(database, dictionary, objective_name, difference)

    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully updated!')


def complete_mode(database, context, args):
    # ex input: daily complete wanikani

    command = context['command']
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to set as complete')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_dict(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle objectives')
            return

    dict_management.complete_item(database, dictionary, objective_name)
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item marked as complete!')


def reset_mode(database, context, args):
    # ex input: daily reset wanikani

    command = context['command']
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to reset')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if command == 'cycle':
        if objective_name not in dict_management.get_active_cycle_dict(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle objectives')
            return

    dict_management.reset_item(database, dictionary, objective_name)
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully updated!')


def setall_mode(database, context, args):
    # ex input: daily setall complete

    command = context['command']
    dictionary = database[command]

    if not args or len(args) > 1:
        console_display.refresh_and_print(database, 'Must provide a setall type')
        raise errors.InvalidCommandUsage(command, context['mode'])

    setall_value = args[0]

    if command == 'cycle':
        context['dictionary'] = dictionary = dict_management.get_active_cycle_dict(database)
    elif command == 'counter':
        setall_counter_mode(database, dictionary, setall_value)
        return

    if setall_value not in {'complete', 'reset'}:
        console_display.refresh_and_print(database, 'Invalid parameter setall value')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if not dictionary:
        console_display.refresh_and_print(database, 'That dictionary is empty')
        return

    if setall_value == 'complete':
        for key in dictionary:
            dict_management.complete_item(database, dictionary, key)
    elif setall_value == 'reset':
        for key in dictionary:
            dict_management.reset_item(database, dictionary, key)
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} items successfully updated!')


def setall_counter_mode(database, dictionary, setall_value):
    if not (setall_value := format_integer(setall_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        raise errors.InvalidCommandUsage('counter', 'setall')

    if not dictionary:
        console_display.refresh_and_print(database, 'There are no counters')
        return

    if not console_display.confirm(f'> Change ALL counters to a value of {setall_value}? (y/n)'):
        return

    for counter, value in dictionary.items():
        current_value = value['numerator']
        difference = setall_value - current_value  # Used to make handling links easier
        dict_management.update_item(database, dictionary, counter, difference)

    # Save, sort, and print display
    dict_management.sort_dictionary(database, 'counter')
    file_management.update(database)
    console_display.refresh_and_print(database, f'Counter items successfully updated!')


def rename_mode(database, context, args):
    # ex input: daily rename wanikani

    command = context['command']
    dictionary = database[command]

    if not args:  # arg = name of objective to rename
        console_display.refresh_and_print(database, 'Must provide an objective to rename')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    new_name = get_name()
    if new_name in dictionary:
        console_display.refresh_and_print(database, f'That name is already in use for [{context["mode"]}]. '
                                                    'Returning to menu')
        return
    dictionary[new_name] = dictionary.pop(objective_name)

    # Handle links
    dict_management.remove_from_linked_from(database, command, objective_name, rename_value=new_name)
    dict_management.remove_from_linked_to(database, command, objective_name, rename_value=new_name)

    # Handle containers
    command_containers = database['containers'][command]
    current_container = dict_management.find_current_container(command_containers, objective_name)
    container_items = command_containers[current_container]['items']
    container_items.remove(objective_name)
    container_items.append(new_name)

    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully renamed!')


def retask_mode(database, context, args):
    # ex input: daily retask wanikani
    command = context['command']
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to give a new task string for')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    new_task_string = get_task_string()
    dictionary[objective_name]['task_string'] = new_task_string
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f"{command.capitalize()} item's task string successfully updated!")


def denominator_mode(database, context, args):
    # ex input: daily denominator wanikani
    command = context['command']
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to change the denominator of')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if not (new_denominator := get_denominator()):
        return
    dictionary[objective_name]['denominator'] = new_denominator
    # Save, sort, and print display
    dict_management.sort_dictionary(database, command)
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully updated!')


def tag_mode(database, context, args):
    # ex input: daily tag wanikani
    command = context['command']
    dictionary = database[command]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to tag')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])
    objective_completed = objective_name['numerator'] >= objective_name['denominator']
    if not objective_completed:
        console_display.refresh_and_print(database, 'Objective must be completed to be tagged')
        return
    tag = get_name('> Enter a tag')
    objective_name['tag'] = tag
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'[{objective_name}] successfully tagged!')


def link_mode(database, context, args):
    # ex input: daily link wanikani
    command = context['command']
    dictionary = database[command]

    # Input validation
    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to link')
        raise errors.InvalidCommandUsage(command, context['mode'])
    objective_input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, objective_input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])
    type_string = input('> What objective type would you like to link this objective to? '
                        '(Blank input = cancel)\n\n').lower()
    if not type_string:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    if type_string not in documentation.get_linkable_dictionary_names():
        console_display.refresh_and_print(database, 'Invalid objective type')
        raise errors.InvalidCommandUsage(command, context['mode'])
    print()  # Extra newline
    link_input_string = input('> What objective would you like to link this objective to? '
                              '(Blank input = cancel)\n\n').lower()
    if not link_input_string:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    if not (linked_objective_name := dict_management.key_search(database, database[type_string],
                                                                link_input_string)):
        console_display.refresh_and_print(database, 'Objective not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    origin = [command, objective_name]
    new_link = [type_string, linked_objective_name]

    # Make sure link is not to itself or circular
    if origin == new_link:
        console_display.refresh_and_print(database, 'Cannot link an objective to itself')
        return
    link_chain = dict_management.get_link_chain(database, origin, new_link)
    if link_chain[0] == link_chain[-1]:  # Circular behavior
        console_display.refresh_and_print(database, f'Invalid link as it would be circular: '
                                                    f'{dict_management.format_link_chain(link_chain)}')
        return

    # Check if it's already linked
    link = dictionary[objective_name]['link']
    linked_to = link[0]

    if linked_to:
        if linked_to == [type_string, linked_objective_name]:  # Already linked to given input
            console_display.refresh_and_print(database, 'This link already exists')
            return
        # A different link was inputted, overwrite previous
        dict_management.remove_from_linked_from(database, command, objective_name)  # Undo link from other side

    # Set this objective's linked_to
    link[0] = [type_string, linked_objective_name]

    # Set the linked objective's linked_from
    database[type_string][linked_objective_name]['link'][1].append([command, objective_name])

    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'[{objective_name}] successfully linked to [{linked_objective_name}]! '
                                                f'Link sequence: {dict_management.format_link_chain(link_chain)}')


def unlink_mode(database, context, args):
    # ex input: daily unlink wanikani
    command = context['command']
    dictionary = database[command]

    # Input validation
    if not args:
        console_display.refresh_and_print(database, 'Must provide an objective to unlink')
        raise errors.InvalidCommandUsage(command, context['mode'])
    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])
    link = dictionary[objective_name]['link']
    linked_to = link[0]
    if not linked_to:
        console_display.refresh_and_print(database, 'Objective is not linked')
        return

    # Remove from the objective it's linked to
    dict_management.remove_from_linked_from(database, command, objective_name)

    # Reset this objective's link
    link[0] = []

    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'[{objective_name}] successfully unlinked!')


# Removing items ------------------------------------------------------------------------------------------
def remove_mode(database, context, args):
    # ex input: daily remove wanikani
    command = context['command']
    dictionary = database[command]

    if not args:
        print('Must provide an objective to remove', end='\n\n')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = ' '.join(args).lower()
    if not (objective_name := dict_management.key_search(database, dictionary, input_string)):
        print('Objective name not found', end='\n\n')
        raise errors.InvalidCommandUsage(command, context['mode'])
    dict_management.remove_item(database, command, objective_name)

    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'{command.capitalize()} item successfully removed!')


# Containers ------------------------------------------------------------------------------------------

def containeradd_mode(database, context, args):
    # ex input: daily containercreate
    command = context['command']
    command_containers = database['containers'][command]  # Corresponding containers dict

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(command, context['mode'])

    container_name = get_name('> Enter a name for the container (must be unique to goal type)')
    container_key = container_name.lower()
    if container_key in command_containers:
        console_display.refresh_and_print(database, 'Container by that name already exists. Returning to menu')
        return
    command_containers.update({container_key: {'display_name': container_name, 'expanded': True, 'items': []}})
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'[{command.capitalize()}] container successfully created!')


def containerdelete_mode(database, context, args):
    # ex input: daily containerdelete
    command = context['command']
    command_containers = database['containers'][command]  # Corresponding containers dict

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = input('> What container would you like to delete?\n\n').lower()
    if not (container_key := dict_management.key_search(database, command_containers, input_string)):
        console_display.refresh_and_print(database, 'Container name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    for objective_key in command_containers[container_key].items():
        command_containers['_default']['items'].append(objective_key)
    command_containers.remove(container_key)
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'Successfully deleted [{container_key}]'
                                                f'and moved objectives back to default!')


def containeredit_mode(database, context, args):
    # ex input: daily containeradd
    command = context['command']
    dictionary = database[command]
    command_containers = database['containers'][command]  # Corresponding containers dict

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = input('> What item would you like to change the container of?\n\n').lower()
    if not (objective_key := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Objective name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    print()  # Extra newline
    input_string = input('> What container would you like to move this item to? '
                         '(BLANK INPUT = REMOVE FROM CONTAINER)\n\n').lower()
    if input_string == '':  # Then put back into _default
        destination_name = '_default'
    elif not (destination_name := dict_management.key_search(database, command_containers, input_string)):
        console_display.refresh_and_print(database, 'Container name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])

    dict_management.move_to_container(database, command, objective_key, destination_name)
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'Successfully moved [{objective_key}] to [{destination_name}]!')


def containermove_mode(database, context, args):
    # ex input: daily containermove

    command = context['command']
    command_containers = database['containers'][command]  # Corresponding containers dict

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(command, context['mode'])

    input_string = input('What container would you like to reposition?\n\n').lower()
    if not (container_key := dict_management.key_search(database, command_containers, input_string)):
        console_display.refresh_and_print(database, 'Container name not found')
        raise errors.InvalidCommandUsage(command, context['mode'])
    if container_key == '_default':
        console_display.refresh_and_print(database, 'Cannot move the default container. Returning to menu')
        return
    current_index = command_containers.index(container_key)

    input_string = input("'up' to move 1 up, 'down' to move 1 down. Can specify number like: up 2\n"
                         "'set <number>' ie 'set 5' for manually setting index (1 = first container below defaults)\n"
                         "Out-of-range values automatically adjusted to boundaries\n\n").lower()
    input_list = input_string.split()
    input_length = len(input_list)
    if input_length == 2:
        if not input_list[1].isnumeric():
            console_display.refresh_and_print(database, 'Invalid second arg; should be an integer. '
                                                        'Returning to menu')
            raise errors.InvalidCommandUsage(command, context['mode'])
    elif input_list != 1:
        console_display.refresh_and_print(database, 'Invalid number of args. Returning to menu')
        raise errors.InvalidCommandUsage(command, context['mode'])
    arg1 = input_list[0]
    if arg1 in {'up', 'u', 'down', 'd'}:
        move_amount = 1  # Default to 1
        if len(input_list) == 2:
            move_amount = input_list[1]
        if arg1 in {'up', 'u'}:
            move_amount *= -1  # Up = lower index
        new_index = current_index + move_amount
    elif arg1 in {'set', 's'}:
        if len(input_list) != 2:
            console_display.refresh_and_print(database, 'Invalid number of args. Returning to menu')
            raise errors.InvalidCommandUsage(command, context['mode'])
        new_index = input_list[1]
    else:
        console_display.refresh_and_print(database, 'Invalid first arg. Returning to menu')
        raise errors.InvalidCommandUsage(command, context['mode'])

    if new_index <= 0:
        new_index = 1
    elif new_index >= len(command_containers):
        new_index = len(command_containers) - 1

    container_copy = command_containers[current_index].copy()
    command_containers.remove(container_key)
    command_containers.insert(container_copy, new_index)
    # Save and print display
    file_management.update(database)
    console_display.refresh_and_print(database, f'Successfully repositioned [{container_key}]!')


# Misc utility ------------------------------------------------------------------------------------------
def format_integer(value: str):
    multiplier = 1  # Default value
    if value[-1] in {'k', 'm', 'b', 't'}:  # Extension
        extension = value[-1]
        value = value[:-1]
        if extension == 'k':
            multiplier = 1e3
        elif extension == 'm':
            multiplier = 1e6
        elif extension == 'b':
            multiplier = 1e9
        elif extension == 't':
            multiplier = 1e12
    try:  # Try an eval
        value = eval(value)
    except (SyntaxError, NameError):
        print('Value must be a number', end='\n\n')
        return False

    try:  # The input base value can be a float, as long as the end result is an integer
        # We need output to be an integer. But, something like "1.5b" will result in a float, since there is
        # multiplication by a float involved. Don't want any implicit conversions, so compare int result to float
        # result, and see if they're numerically equal.
        if not (number := int(value * multiplier)) == value * multiplier:
            print('Value must be an integer', end='\n\n')
            return False
    except TypeError:  # Valid eval happened, but not a valid number
        print('Value must be an integer*', end='\n\n')
        return False

    if number == 0:
        print('Value cannot be 0', end='\n\n')
        return False
    return number
