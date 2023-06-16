import dict_management
import file_management
import date_logic
import console_display
import documentation
import history_interface
import errors
import os


# Base core dict functions need to take (database, context, args)

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
    dict_name = context['command']
    dictionary = database[dict_name]

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if dict_name in {'todo', 'counter', 'cycle'}:  # Different processes
        special_add_function = globals()[dict_name + '_add_mode']  # ie cycle_add_mode, gets corresponding func
        special_add_function(database, dict_name)
        return

    item_name = get_name()
    if not item_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    item_key = item_name.lower()
    if item_key in dictionary:
        console_display.refresh_and_print(database, 'Item by that name already exists. Returning to menu')
        return
    denominator = get_denominator()
    history_name = get_history_name(database, dict_name)
    start_timer = get_start_timer()
    dictionary.update({item_key: {'display_name': item_name,
                                  'denominator': denominator,
                                  'numerator': 0,
                                  'streak': 0,
                                  'pause_timer': start_timer,
                                  'link': {'linked_to': [], 'linked_from': [], 'chaining': True},
                                  'history_name': history_name,
                                  'tag': None}})
    dict_management.default_group(database, dict_name, item_key)  # Add to default container
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully added!')


def todo_add_mode(database, dict_name):
    dictionary = database[dict_name]
    item_name = get_name()
    if not item_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    item_key = item_name.lower()
    if item_key in dictionary:
        console_display.refresh_and_print(database, 'Item by that name already exists. Returning to menu')
        return
    denominator = get_denominator()
    while True:
        print('> Should this todo item count towards daily requirement? (y/n) (blank = n)', end='\n\n')
        user_input = input().lower()
        print()  # Extra newline

        if user_input in {'yes', 'y'}:
            enforced_todo = True
            print('Item will count towards streak', end='\n\n')
            break
        elif user_input in {'no', 'n', ''}:
            enforced_todo = False
            print('Item will not count towards streak', end='\n\n')
            break
    history_name = get_history_name(database, dict_name)
    start_timer = get_start_timer()
    dictionary.update({item_key: {'display_name': item_name,
                                  'denominator': denominator,
                                  'numerator': 0,
                                  'enforced_todo': enforced_todo,
                                  'pause_timer': start_timer,
                                  'link': {'linked_to': [], 'linked_from': [], 'chaining': True},
                                  'history_name': history_name,
                                  'tag': None}})
    dict_management.default_group(database, 'todo', item_key)  # Add to default container
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, 'Todo item successfully added!')


def cycle_add_mode(database, dict_name):
    def calculate_cooldown_sequence(days_list):
        def next_index():
            if i == len(days_list) - 1:
                return 0
            else:
                return i + 1

        seq = []
        for i, n in enumerate(days_list):
            if i == len(days_list) - 1:  # Last step
                n = n - 7
            seq.append(days_list[next_index()] - n)
        return seq

    dictionary = database[dict_name]
    item_name = get_name()
    if not item_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    item_key = item_name.lower()
    if item_key in dictionary:
        console_display.refresh_and_print(database, 'Item by that name already exists. Returning to menu')
        return
    denominator = get_denominator()
    history_name = get_history_name(database, dict_name)
    mode_input = input('> Enter a number corresponding to a mode for item setup\n'
                       '  [1] Every x days\n'
                       '  [2] Certain week day(s)\n'
                       '  [3] Advanced (manually insert cooldown sequence)\n\n')
    print()  # Extra newline
    if mode_input not in {'1', '2', '3'}:
        console_display.refresh_and_print(database, 'Invalid mode response')
        return

    # Variables that are not used in every mode but need to be set
    frequency_description = None
    abbreviations = None
    week_cooldown = None
    cooldown_iterator = None  # Stop intellisense from complaining

    if mode_input == '1':  # Every x days
        display_mode = 'number'
        # Get cycle sequence
        repeat_input = input('> Every how many days should this item activate? (ie 2 = every other day)\n\n')
        print()  # Extra newline
        if not repeat_input.isnumeric():
            console_display.refresh_and_print(database, 'Invalid input. Should be positive integer days')
            return
        cooldown_sequence = [int(repeat_input)]

        # Get initial cooldown and set cooldown iterator
        start_offset = get_start_timer()
        cooldown_iterator = 0

    elif mode_input == '2':  # Every certain week day(s)
        display_mode = 'week_day'
        # Get cycle sequence
        day_numbers = []
        abbreviations = []  # Letter form of weekdays for later display purposes
        while True:
            days_print = [date_logic.convert_day_number(day_number) for day_number in day_numbers]  # Print full names
            user_response = input(f'> Enter week days one-by-one. Say "done" when finished.\n'
                                  f'> Current days: {days_print}\n\n').lower()
            print()  # Extra newline
            if user_response == 'done':
                break
            elif not (day_number := date_logic.convert_day(user_response)):
                print("Cannot discern week day from input\n")
                continue
            elif day_number in day_numbers:
                print("That day has already been added\n")
                continue
            day_numbers.append(day_number)
            day_numbers.sort()
            print(f'Successfully added {date_logic.convert_day_number(day_number)}\n')
        if not day_numbers:
            console_display.refresh_and_print(database, 'Exited as no days were provided')
            return
        for day_number in day_numbers:
            abbreviations.append(date_logic.get_week_day_abbreviation(day_number))
        cooldown_sequence = calculate_cooldown_sequence(day_numbers)

        # Get in-between cooldown
        week_cooldown_input = input('> Enter an amount of weeks to wait between cycles '
                                    '(0 = every week, 1 = every other week)\n\n')
        print()  # Extra newline
        if not week_cooldown_input.isnumeric():
            console_display.refresh_and_print(database, 'Invalid input, expected positive integer')
            return
        week_cooldown = int(week_cooldown_input)
        cooldown_sequence[-1] += week_cooldown * 7  # Weeks to days, add to end of cycle

        # Get initial offset and set cooldown iterator
        current_day = database['settings']['calendar_date']['week_day']

        cooldown_iterator = None  # Init variables so intellisense doesn't complain
        nearest_active_offset = None

        # Find nearest active and its offset from today
        if current_day > day_numbers[-1]:  # Check for no upcoming this week
            cooldown_iterator = 0
            nearest_active_offset = day_numbers[0]
        else:  # Nearest active is today or upcoming this week
            for index, day in enumerate(day_numbers):
                if day >= current_day:  # Find first one from today
                    cooldown_iterator = index
                    nearest_active_offset = day - current_day
                    break
        next_week_offset = day_numbers[0] - (current_day - 7)  # -7 to correct for 'next week'
        offset_input = input("> When should the cycle start? Pick an option or provide a number of weeks to wait\n"
                             "  [A] ASAP & can start mid-cycle\n"
                             "  [B] Wait until next first day of sequence\n"
                             "  [n > 0] Wait n weeks from next first day of sequence; ie 1 = first day + "
                             "extra 7 days\n\n").lower()
        print()  # Extra newline
        if offset_input == 'a' or int(offset_input) == 0:  # Start ASAP
            start_offset = nearest_active_offset
        elif offset_input == 'b':  # Wait until first active day in sequence from Sunday
            start_offset = next_week_offset
            cooldown_iterator = 0
        elif offset_input.isnumeric():  # n > 0
            offset_input = int(offset_input)
            start_offset = next_week_offset + offset_input * 7
            cooldown_iterator = 0
        else:
            console_display.refresh_and_print(database, "Invalid input, expected 'a', 'b', or a positive integer")
            return

    elif mode_input == '3':  # Manually provide cooldown sequence
        display_mode = 'custom'
        print('> Advanced Mode has three primary fields and then a custom identifier tag to be used for display and '
              'History Mode.\n'
              '> First is days until the first activation (can be mid-cycle; 0 = today).\n'
              '> Second is the cooldown sequence. This is an ordered list of positive integers that corresponds to '
              'how long to wait\n  between each activation, cycling back to the start after the finishing the end.\n'
              '> Third is the index (starting at 0) of the value in the cooldown sequence that the first-activation '
              'timer (from step 1)\n  was configured for (0 = first value).\n>\n'
              '> For example, say today is Friday, and you want to set up a cycle for every other Sat/Sun. This can be '
              'done with\n  '
              '(1) a first-activation timer of 1 day (to Saturday; though could do 2 for Sunday; only affects the '
              'first time)\n  '
              '(2) a cooldown sequence of [1, 13] (1 day from Sat to Sun, 13 days from Sun to next-next Sat)\n  '
              '(3) first-activation index of 0 (the 1 from [1, 13] is for Saturday to Sunday, and we tuned the '
              'first-activation\n  timer for Saturday (would be index of 1 instead if we tuned to start Sunday; this '
              'also only impacts the first run\n  of the cycle and is for convenience)\n>\n>')
        cooldown_sequence = []
        start_offset = input('> In how many days should the first activation be? (0 = today)\n\n')
        if not start_offset.isnumeric():
            console_display.refresh_and_print(database, 'Invalid response, expected 0 or positive integer')
            return
        start_offset = int(start_offset)
        print()  # Extra newline
        while True:
            user_response = input(f'> Enter cooldown (positive integer) sequence values one-by-one.\n'
                                  f'> Say "done" when finished, "del" to delete most recent, or "clear" to delete '
                                  f'all.\n'
                                  f'> Current sequence: {cooldown_sequence}\n\n').lower()
            print()  # Extra newline
            if user_response == 'done':
                break
            elif user_response == 'clear':
                cooldown_sequence.clear()
                continue
            elif user_response == 'del':
                cooldown_sequence.pop()
                continue
            elif not user_response.isnumeric() or int(user_response) == 0:
                print('Invalid input\n')
                continue
            cooldown = int(user_response)
            cooldown_sequence.append(cooldown)
            print(f'Successfully added {cooldown}\n')
        if not cooldown_sequence:
            console_display.refresh_and_print(database, 'Exited as cooldown sequence was not provided')
            return
        while True:
            cooldown_iterator_input = input('> Enter the index (starting from 0) in the cooldown sequence list that '
                                            'the first-activation timer was\n  tuned to transition into\n\n').lower()
            print()  # Extra newline
            if cooldown_iterator_input == 'cancel':
                console_display.refresh_and_print(database, 'Cancelled')
                return
            elif not cooldown_iterator_input.isnumeric():
                print('Invalid response, should be 0 or an integer. Try again or say "cancel" to exit\n')
                continue
            cooldown_iterator = int(cooldown_iterator_input)
            if cooldown_iterator >= len(cooldown_sequence):
                print('Invalid response, index out of range (remember it starts counting at 0), please try again\n')
                continue
            break
        while True:
            frequency_description = input("> Enter a description of the frequency.\n  "
                                          "This is a string that will be displayed in the item title to indicate "
                                          "the item's frequency (BLANK = CANCEL)\n\n")
            if not frequency_description:
                if console_display.confirm('Cancel creation of this item? (y/n)'):
                    console_display.refresh_and_print(database, 'Cancelled')
                    return
                continue
            break

    else:
        console_display.refresh_and_print(database, 'Invalid mode number')
        return

    dictionary.update({item_key: {'display_name': item_name,
                                  'denominator': denominator,
                                  'numerator': 0,
                                  'streak': 0,
                                  'week_days': abbreviations,  # Only for week_day mode
                                  'week_cooldown': week_cooldown,
                                  'cooldown_sequence': cooldown_sequence,
                                  'cooldown_iterator': cooldown_iterator,
                                  'frequency_description': frequency_description,
                                  'remaining_cooldown': start_offset,
                                  'display_mode': display_mode,
                                  'pause_timer': 0,
                                  'link': {'linked_to': [], 'linked_from': [], 'chaining': True},
                                  'history_name': history_name,
                                  'tag': None}})
    dict_management.default_group(database, 'cycle', item_key)  # Add to default container
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, 'Cycle item successfully added!')


def counter_add_mode(database, dict_name):
    dictionary = database[dict_name]
    item_name = get_name()
    if not item_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    item_key = item_name.lower()
    if item_key in dictionary:
        console_display.refresh_and_print(database, 'Counter by that name already exists. Returning to menu')
        return
    history_name = get_history_name(database, dict_name)
    dictionary.update({item_key: {'display_name': item_name,
                                  'numerator': 0,
                                  'pause_timer': 0,
                                  'link': {'linked_to': [], 'linked_from': [], 'chaining': True},
                                  'history_name': history_name,
                                  'tag': None}})
    if history_name:
        dict_management.create_counter_history(database, history_name)
    dict_management.default_group(database, 'counter', item_key)  # Add to default container
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, 'Counter item successfully added!')


def note_add_mode(database, context, args):
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
    ### add_to_groups(database, 'note', item_key)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, 'Note item successfully added!')


def get_name(prompt='> Enter a name for the item (must be unique to goal type, blank = cancel)'):
    while True:
        print(prompt, end='\n\n')
        name = input().strip()  # Get input and remove leading/trailing spaces
        print()  # Extra newline
        if not name:
            return
        if not name.isascii():
            print('Please only use ASCII characters')
            continue
        return name


def get_history_name(database, dictionary_name):
    dictionary = database[dictionary_name]
    history_dict = database['history'][dictionary_name]
    while True:
        history_name = get_name(prompt="> Enter a name for the matching History item title (unique to goal type; "
                                       "persistent; blank = don't track item)")
        if not history_name:
            print('Opted to disable History tracking for this item', end='\n\n')
            return None
        valid_key = True
        for item_key in dictionary:
            name = dictionary[item_key]['history_name']
            if name and name.lower() == history_name.lower():
                valid_key = False
                print(f'That History key is already used by [{item_key}]', end='\n\n')
                break
        if valid_key:
            if history_name.lower() in history_dict:
                history_name = history_dict[history_name.lower()]['display_name']  # Match pre-existing casing
                print(f'Item successfully attached to an already-existing History item: [{history_name}]', end='\n\n')
            return history_name


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


def get_start_timer():
    while True:
        print("> Activate in how many days? (0 = blank = activate now)", end='\n\n')
        user_input = input().lower()
        print()  # Extra newline

        if user_input == '':  # Default to 0
            return 0
        elif not user_input.isnumeric():
            print('Input must be a positive integer')
            continue
        return int(user_input)


# Updating/editing items ------------------------------------------------------------------------------------------
def update_mode(database, context, args):
    # ex input: daily update itemname 50
    # ex input: daily update clean dishes

    # Spaces in names complicates. Prioritize searching for item name over valid update value.
    # Can have a case where item name is something like "Do number 9". Prioritizes updating an item named that by 1
    # rather than updating an item named "Do number" by 9

    dict_name = context['command']  # Cycle handled differently
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to update')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    full_string = ' '.join(args).lower()  # Lowercase string of entire rest of input
    # Search for full string as an item name; assuming no update value specified
    if (item_name := dict_management.key_search(database, dictionary, full_string)) in dictionary:
        update_value = '1'  # str because format_integer takes a string
    else:  # Item wasn't found. Assume update value was specified
        sub_string = ' '.join(args[:-1]).lower()  # Last element should be update value
        if not (item_name := dict_management.key_search(database, dictionary, sub_string)):
            console_display.refresh_and_print(database, 'Item not found')
            raise errors.InvalidCommandUsage(dict_name, context['mode'])
        update_value = args[-1]  # Worked out this way, proceed

    # Validate/format update value from str to int
    if not (update_value := format_integer(update_value)):  # Enforces non-zero integer. Accepts extension ie 1k
        console_display.refresh_and_print(database, 'Invalid update value')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])  # Invalid update value

    if dict_name == 'cycle':  # Can't update inactive item
        if item_name not in dict_management.get_active_cycle(database):
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle items')
            return

    dict_management.update_item(database, dict_name, item_name, update_value)

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully updated!')


def set_mode(database, context, args):
    # ex input: daily set itemname 50

    dict_name = context['command']  # Cycle handled differently
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to update and set value')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args[:-1]).lower()  # Last element should be set value
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if not (set_value := format_integer(args[-1])):  # Enforces non-zero integer. Accepts extension ie 1k
        console_display.refresh_and_print(database, 'Invalid set value')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if dict_name == 'cycle':
        if item_name not in dict_management.get_active_cycle(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle items')
            return

    current_value = dictionary[item_name]['numerator']
    difference = set_value - current_value  # Used to make handling links easier
    dict_management.update_item(database, dict_name, item_name, difference)

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully updated!')


def complete_mode(database, context, args):
    # ex input: daily complete itemname

    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to set as complete')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if dict_name == 'cycle':
        if item_name not in dict_management.get_active_cycle(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle items')
            return

    dict_management.complete_item(database, dict_name, item_name)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item marked as complete!')


def reset_mode(database, context, args):
    # ex input: daily reset itemname

    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to reset')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if dict_name == 'cycle':
        if item_name not in dict_management.get_active_cycle(database):  # Can't update inactive item
            console_display.refresh_and_print(database, 'Cannot update progress for inactive cycle items')
            return

    dict_management.reset_item(database, dict_name, item_name)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully updated!')


def setall_mode(database, context, args):
    # ex input: daily setall complete

    dict_name = context['command']
    dictionary = database[dict_name]

    if not args or len(args) > 1:
        console_display.refresh_and_print(database, 'Must provide a setall type')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    setall_value = args[0]

    if dict_name == 'cycle':
        context['dictionary'] = dictionary = dict_management.get_active_cycle(database)
    elif dict_name == 'counter':
        counter_setall_mode(database, dict_name, setall_value)
        return

    if setall_value not in {'complete', 'reset'}:
        console_display.refresh_and_print(database, 'Invalid parameter setall value')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if not dictionary:
        console_display.refresh_and_print(database, 'That dictionary is empty')
        return

    if setall_value == 'complete':
        for key in dictionary:
            dict_management.complete_item(database, dict_name, key)
    elif setall_value == 'reset':
        for key in dictionary:
            dict_management.reset_item(database, dict_name, key)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} items successfully updated!')


def counter_setall_mode(database, dict_name, setall_value):
    dictionary = database[dict_name]
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
        dict_management.update_item(database, dict_name, counter, difference)

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'Counter items successfully updated!')


def rename_mode(database, context, args):
    # ex input: daily rename itemname

    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to rename')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_key := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    new_name = get_name()
    new_key = new_name.lower()
    if not new_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    if new_key in dictionary:
        console_display.refresh_and_print(database, f'That name is already in use. Returning to menu')
        return

    # Handle links
    if dictionary[item_key]['link']['linked_to']:
        dict_management.rename_linked_from(database, dict_name, item_key, new_key)
    if dictionary[item_key]['link']['linked_from']:
        dict_management.rename_linked_to(database, dict_name, item_key, new_key)

    # Implement rename
    dictionary[new_key] = dictionary.pop(item_key)
    dictionary[new_key]['display_name'] = new_name

    # Handle Group
    current_group = dict_management.get_group(database, dict_name, item_key)
    current_group['items'].remove(item_key)
    current_group['items'].append(new_key)

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully renamed!')


def history_mode(database, context, args):
    # ex input: daily history
    dict_name = context['command']

    if args:
        print('Unnecessary arguments, returning to menu', end='\n\n')
        raise errors.InvalidCommandUsage(context['command'], context['mode'])

    os.system('cls')
    history_interface.launch_history_interface(database, dict_name)  # Enters history loop
    console_display.print_display(database)
    print('Returned to menu', end='\n\n')


def rehistory_mode(database, context, args):
    # ex input: daily rehistory itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to change the History link of')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    new_history_name = get_history_name(database, dict_name)
    dictionary[item_name]['history_name'] = new_history_name
    if dict_name == 'counter':
        dict_management.create_counter_history(database, new_history_name)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'Successfully changed History link to [{new_history_name}]!')


def denominator_mode(database, context, args):
    # ex input: daily denominator itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to change the denominator of')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if not (new_denominator := get_denominator()):
        return
    dictionary[item_name]['denominator'] = new_denominator
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully updated!')


def tag_mode(database, context, args):
    # There are two alternate implementations of getting the tag. The complication comes from inserting newlines
    # #1 is using a backslash-escape syntax. The user pressing 'enter' submits the string they typed to be parsed
    # #2 is  getting lines in a loop and using a keyword to stop, with a check for if they wanted to insert the keyword
    def get_parsed_tag():
        tag = get_name('> Enter a tag (use "\\n" for  newline, backslashes are escapable, blank to cancel')
        if not tag:
            return None
        final = []  # Hold the final, parsed and evaluate string
        search_start = 0
        while True:
            index = tag.find('\\', search_start)
            if index == -1:  # No backslashes remaining
                final.append(tag[search_start:])  # Finalize remainder of the string
                break
            final.append(tag[search_start:index])  # Add in what we've searched past already
            if index + 1 == len(tag):  # String ends in a single unescaped backslash
                final.append('\\')
                break
            next_char = tag[index + 1]  # Get the character following the backslash
            if next_char == '\\':
                final.append('\\')
            elif next_char == 'n':
                final.append('\n')
            search_start = index + 2  # Skip over next_char, which we already processed
        return ''.join(final)

    def get_tag_lines():
        print('Write your tag! Press enter for newlines.'
              'Enter "done" when completed (will confirm if you want to stop or insert that literally,'
              'submit blank to cancel)', end='\n\n')
        lines = []
        while True:
            user_input = input()
            if user_input == "done":
                if console_display.confirm('\nAre you finished (y/n)? (Will insert as a literal line otherwise)'):
                    final = '\n'.join(lines)
                    if not final:
                        return None
                    else:
                        return final
            lines.append(user_input)

    # -------------------------------------------------------------------------------------------
    # ex input: daily tag itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to tag')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    item = dictionary[item_name]

    if not item['history_name']:
        console_display.refresh_and_print(database, 'Item does not have a History link to store a tag in')
        return
    elif item['tag']:
        console_display.refresh_and_print(database, f'Item is currently tagged:\n{item["tag"]}')
        if not console_display.confirm('Overwrite? (y/n)'):
            console_display.refresh_and_print(database, 'Cancelled')
            return

    # Control which method to get the tag string with
    parsed_input_mode = database['settings']['single_line_tag_input']
    if parsed_input_mode:
        tag_input_func = get_parsed_tag
    else:
        tag_input_func = get_tag_lines
    tag_input = tag_input_func()
    if tag_input is None:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    item['tag'] = tag_input
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'[{item_name}] successfully tagged!')


def link_mode(database, context, args):
    # ex input: daily link itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    # Input validation
    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to link')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    item_input_string = ' '.join(args).lower()
    if not (item_key := dict_management.key_search(database, dictionary, item_input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    input_dict_name = input('> What type of item would you like to link this item to? '
                            '(Blank input = cancel)\n\n').lower()
    if not input_dict_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    if input_dict_name not in documentation.get_numeric_dictionary_names():
        console_display.refresh_and_print(database, 'Invalid item type')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    print()  # Extra newline

    input_item_key = input('> What item would you like to link this item to? (Blank input = cancel)\n\n').lower()
    if not input_item_key:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    if not (input_item_key := dict_management.key_search(database, database[input_dict_name], input_item_key)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    print()
    input_item_name = database[input_dict_name][input_item_key]['display_name']

    while True:
        chain_input_string = input('> Would you like this link to trigger other links when applicable? '
                                   '(y/n/blank to cancel)\n\n').lower()

        if chain_input_string in {'yes', 'y'}:
            chaining = True
            break
        elif chain_input_string in {'no', 'n'}:
            chaining = False
            break
        elif not chain_input_string:
            console_display.refresh_and_print(database, 'Cancelled')
            return
        print()

    link = dictionary[item_key]['link']
    link['chaining'] = chaining
    origin = [dict_name, item_key, chaining]
    next_link = [input_dict_name, input_item_key, database[input_dict_name][input_item_key]['link']['chaining']]

    # Make sure link is not to itself or circular
    if origin == next_link:
        console_display.refresh_and_print(database, 'Cannot link an item to itself')
        return
    link_chain = dict_management.get_link_chain(database, origin, next_link)
    if link_chain[0] == link_chain[-1]:  # Circular behavior
        console_display.refresh_and_print(database, f'Invalid link as it would be circular: '
                                                    f'{dict_management.format_link_chain(link_chain)}')
        return

    # Check if it's already linked
    linked_to = link['linked_to']

    if linked_to:
        if linked_to == [input_dict_name, input_item_name]:  # Already linked to given input
            console_display.refresh_and_print(database, 'This link already exists')
            return
        # A different link was inputted, confirm overwriting previous
        if not console_display.confirm(f'This item is already linked to {dictionary[item_key]["link"]["linked_to"]}\n'
                                       f'Overwrite this link? (y/n)'):
            console_display.refresh_and_print(database, 'Cancelled')
            return
        dict_management.remove_from_linked_from(database, dict_name, item_key)  # Undo link from other side

    # Set this item's linked_to
    link['linked_to'] = [input_dict_name, input_item_name]

    # Set the linked item's linked_from
    database[input_dict_name][input_item_name]['link']['linked_from'].append([dict_name, item_key])

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'[{item_key}] successfully linked to [{input_item_name}]! '
                                                f'Link sequence: {dict_management.format_link_chain(link_chain)}')


def unlink_mode(database, context, args):
    # ex input: daily unlink itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    # Input validation
    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to unlink')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item name not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    link = dictionary[item_name]['link']
    linked_to = link['linked_to']
    if not linked_to:
        console_display.refresh_and_print(database, 'Item is not linked')
        return

    # Remove from the item it's linked to
    dict_management.remove_from_linked_from(database, dict_name, item_name)

    # Reset this item's link
    link['linked_to'] = []

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'[{item_name}] successfully unlinked!')


def viewlink_mode(database, context, args):
    # ex input: daily viewlink itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    # Input validation
    if not args:
        console_display.refresh_and_print(database, 'Must provide an item to view the link chain of')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item name not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    linked_to = dictionary[item_name]['link']['linked_to']
    if not linked_to:
        console_display.refresh_and_print(database, 'Item is not linked')
        return

    origin = [dict_name, item_name, dictionary[item_name]['link']['chaining']]
    linked_dict_name, linked_item_name = linked_to
    next_link = [linked_dict_name, linked_item_name, database[linked_dict_name][linked_item_name]['link']['chaining']]
    link_chain = dict_management.get_link_chain(database, origin, next_link)
    console_display.refresh_and_print(database, f'Link: {dict_management.format_link_chain(link_chain)}')


def pause_mode(database, context, args):
    # ex input: daily pause

    dict_name = context['command']
    dictionary = database[dict_name]
    pause_list = []  # Items to pause

    # Input validation
    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    user_response = input('> Enter a response corresponding to a selection mode\n'
                          '  [A] Single item\n'
                          '  [B] Group\n\n').lower()
    if user_response not in {'a', 'b'}:
        console_display.refresh_and_print(database, 'Invalid response')
        return
    if user_response == 'a':
        input_item_name = input('> What item would you like to pause? (Blank input = cancel)\n\n').lower()
        if not input_item_name:
            console_display.refresh_and_print(database, 'Cancelled')
            return
        if not (item_name := dict_management.key_search(database, dictionary, input_item_name)):
            console_display.refresh_and_print(database, 'Item not found')
            raise errors.InvalidCommandUsage(dict_name, context['mode'])
        pause_list.append(item_name)
    else:  # == 'b'
        input_string = input('> What Group would you like to pause? (Blank input = cancel)\n\n').lower()
        if not input_string:
            console_display.refresh_and_print(database, 'Cancelled')
            return
        if not (container_name := dict_management.key_search(database, database['groups'][dict_name],
                                                             input_string)):
            console_display.refresh_and_print(database, 'Container not found')
            raise errors.InvalidCommandUsage(dict_name, context['mode'])
        for item in database['groups'][dict_name][container_name]:
            pause_list.append(item)
    duration_input = input('> How many days should the item be paused for? (-1 = indefinite, 0 = cancel)\n\n')
    if not (duration_input == '-1' or duration_input.isnumeric()):
        console_display.refresh_and_print(database, 'Invalid input. Expected -1 or a positive integer')
        return
    elif duration_input == '0':
        console_display.refresh_and_print(database, 'Cancelled')
        return
    duration = int(duration_input)
    for item in pause_list:
        dictionary[item]['pause_timer'] = duration

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, 'Items successfully paused!')


# Removing items ------------------------------------------------------------------------------------------
def remove_mode(database, context, args):
    # ex input: daily remove itemname
    dict_name = context['command']
    dictionary = database[dict_name]

    if not args:
        print('Must provide an item to remove', end='\n\n')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (item_name := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    dict_management.remove_item(database, dict_name, item_name)  # Link, Group handled here

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'{dict_name.capitalize()} item successfully removed!')


# Groups ------------------------------------------------------------------------------------------

def groupadd_mode(database, context, args):
    # ex input: daily groupadd
    # Creates a new Group
    dict_name = context['command']
    groups = database['groups'][dict_name]  # Corresponding Groups dict
    groups_display = database['groups_display'][dict_name]

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    group_name = get_name('> Enter a name for the Group (must be unique to goal type)')
    if not group_name:
        console_display.refresh_and_print(database, 'Cancelled')
        return
    group_key = group_name.lower()
    if group_key in groups:
        console_display.refresh_and_print(database, 'Group by that name already exists. Returning to menu')
        return
    groups.update({group_key: {'display_name': group_name, 'manual_order': [], 'sort_override': None, 'expanded': True,
                               'items': []}})
    groups_display.append(group_key)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'[{dict_name.capitalize()}] Group successfully created!')


def groupremove_mode(database, context, args):
    # ex input: daily groupremove
    dict_name = context['command']
    groups = database['groups'][dict_name]
    groups_display = database['groups_display'][dict_name]

    if not args:
        print('Must provide a Group to remove', end='\n\n')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = ' '.join(args).lower()
    if not (group_key := dict_management.key_search(database, groups, input_string, ignore_list=['_Default'])):
        console_display.refresh_and_print(database, 'Group name not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    for item_key in groups[group_key]['items']:
        dict_management.default_group(database, dict_name, item_key)  # Back to default
    groups.pop(group_key)
    groups_display.remove(group_key)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'Successfully deleted Group and returned items to default!')


def groupchange_mode(database, context, args):
    # ex input: daily groupchange
    dict_name = context['command']
    dictionary = database[dict_name]
    groups = database['groups'][dict_name]  # Corresponding Groups dict

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = input('> What item would you like to change the Group of?\n\n').lower()
    if not (item_key := dict_management.key_search(database, dictionary, input_string)):
        console_display.refresh_and_print(database, 'Item not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    print()  # Extra newline
    input_string = input('> What Group would you like to move this item to? '
                         '(BLANK INPUT = REMOVE FROM GROUPS)\n\n').lower()
    if input_string == '':  # Then put back into default
        dict_management.remove_from_groups(database, dict_name, item_key)
        dict_management.default_group(database, dict_name, item_key)
    elif not (destination_name := dict_management.key_search(database, groups, input_string, ignore_list=['_Default'])):
        console_display.refresh_and_print(database, 'Group not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    else:
        dict_management.move_to_group(database, dict_name, item_key, destination_name)

    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'Successfully moved [{item_key}]!')


def groupposition_mode(database, context, args):
    # ex input: daily groupposition

    dict_name = context['command']
    groups = database['groups'][dict_name]  # Corresponding group dict
    groups_display = database['groups_display'][dict_name]

    if args:
        console_display.refresh_and_print(database, 'Unnecessary arguments!')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    input_string = input('What Group would you like to reposition?\n\n').lower()
    if not (group_key := dict_management.key_search(database, groups, input_string, ignore_list=['_Default'])):
        console_display.refresh_and_print(database, 'Group not found')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    current_index = groups_display.index(group_key)

    input_string = input("- 'up' to move 1 up, 'down' to move 1 down. Can specify number like: up 2\n"
                         "- 'set <number>' ie 'set 5' for manually setting index (1 = first below default section)\n"
                         "- Out-of-range values automatically adjusted to boundaries\n"
                         "- Negative indexing works\n\n").lower()
    input_list = input_string.split()
    input_length = len(input_list)
    if not input_string or input_length > 2:
        console_display.refresh_and_print(database, 'Invalid number of args. Returning to menu')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])
    if input_length == 2:
        try:
            int(input_list[1])
        except ValueError:
            console_display.refresh_and_print(database, 'Invalid second arg; should be an integer. '
                                                        'Returning to menu')
            return
    arg1 = input_list[0]
    if arg1 in {'up', 'u', 'down', 'd'}:
        move_amount = 1  # Default to 1
        if input_length == 2:
            move_amount = int(input_list[1])
        if arg1 in {'up', 'u'}:  # Make negative since up = lower index
            move_amount *= -1
        new_index = current_index + move_amount
    elif arg1 in {'set', 's'}:
        if input_length != 2:
            console_display.refresh_and_print(database, 'Invalid number of args. Returning to menu')
            raise errors.InvalidCommandUsage(dict_name, context['mode'])
        new_index = int(input_list[1]) - 1  # -1 to fix for 0-index
    else:
        console_display.refresh_and_print(database, 'Invalid first arg. Returning to menu')
        raise errors.InvalidCommandUsage(dict_name, context['mode'])

    if new_index == current_index:
        console_display.refresh_and_print(database, 'Group is already in that position')
        return
    if new_index < 0:
        new_index = 0
    elif new_index >= len(groups):
        new_index = len(groups) - 1

    groups_display.remove(group_key)
    groups_display.insert(new_index, group_key)
    # Save and print display
    file_management.save(database)
    console_display.refresh_and_print(database, f'Successfully repositioned [{group_key}]!')


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
