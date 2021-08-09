# Set to enforce ASCII just because it's what Windows cmd can display. Can be avoided if this is interfaced
# If interfaced; could definitely use containers. Group objectives within a dictionary,
# complete with collapsing/minimizing.
# TODO: Help dialog, tutorial dialog, mention bakcup when running program, mention case sensitviity
# TODO: Error handling/polishing

# TODO: Finish cycles (need to work around endday, fix for active vs inactive)
# TODO: uhhhh END DAY Cycles etc. count for streak, todo for total etc
#       Make the stats increment, make sure auto toggle actually does something
# TODO: history dict toggle. {'dict_type': {obj_name + task_string: {count: #, tag: str}}}
#       Long-term one doesn't need a count
#       Pages
#       History combine command to sum up different objects that refer to the same exact thing
# TODO: Notes
# TODO: warn about clearing
# TODO: print help on the command for commands not being used right?
# TODO: reset data comandd
# TODO: setting for sorting counter by counter val instead of name
# TODO: Note groups (have naems and load different configs). Notes that autoload on certain days?
# TODO: Counter groups in the same fashion
# TODO: Audo date switching setting
import file_management  # For loading/saving
import commands  # Command functions, alias_format()
import console_display  # To print the initial console display
import exceptions

# main gets input
# -> checks for validity and matching command. If found, pass to commands.py
# -> Corresponding command function executes


def main():
    # Load the database from file
    database = file_management.load_data()  # If json successfully loaded, use that. Else default to base template

    # Update backup right after loading (to save state before user performs any actions)
    file_management.update(database, 'data_autobackup.json')

    console_display.print_display(database)

    while True:
        user_input = input().lower()  # Lower for string comparisons
        if not user_input:  # It's possible to enter nothing- continue loop
            console_display.print_display(database)
            continue
        if not user_input.isascii():
            print('Please only use ASCII characters')  # Limitation from lack of interfacing
            continue
        user_input = user_input.split()  # Split into a list of space-separated terms
        commands.alias_format(user_input)  # Reformats input list according to alias dict
        command = user_input[0]

        print()  # Newline to separate input from printing
        try:
            # Try to get corresponding function from commands.py
            # Command functions have '_command' appended to name, ie daily_command
            command_function = getattr(commands, command + '_command')
        except AttributeError:  # If function is not found
            print('Invalid command')
            print()  # Newline to separate input from printing
            continue

        try:
            command_function(database, user_input)  # All is well, proceed to command function
        except exceptions.InvalidCommandUsage as error:
            print(f'help for {error.command} {error.subcommand} :)')


if __name__ == '__main__':
    main()
