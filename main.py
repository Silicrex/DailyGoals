# Set to enforce ASCII just because it's what Windows cmd can display. Can be avoided if this is interfaced
# TODO: Help dialog, tutorial dialog, mention backup when running program, mention case sensitivity
# TODO: Error handling/polishing
# TODO: uhhhh END DAY Cycles etc. count for streak, todo for total etc
#       Make the stats increment, make sure auto toggle actually does something
# TODO: Notes
# TODO: print help on the command for commands not being used right?
# TODO: reset data command
# TODO: setting for sorting counter by counter val instead of name
# TODO: Note groups (have names and load different configs). Notes that autoload on certain days?
# TODO: Counter groups in the same fashion
# TODO: Auto date switching setting (endday alternative)
# TODO: 7-day preview for upcoming
# TODO: setdate considers switch_date setting
# TODO: Add ability to attach a url?
# TODO: Remove setdate warning when nothing is lost
# TODO: Setting for sorting counter by numerator
# TODO: Option to combine history entries
# TODO: PLURALIZE CONTAINER ITEMS, show list of options in containeredit, fix extra newline
# TODO: Way to view links. When you link, should also specify dict type
# TODO: Break command, indicate a daily isn't needed today
# TODO: Fix display settings stuff
import file_management  # For loading/saving
import commands  # Command functions and formatting
import console_display  # To print the initial console display
import errors

# main gets input
# -> checks for validity and matching command. If found, pass to commands.py
# -> Corresponding command function executes


def main():
    # Load the database from file
    database = file_management.load_data()  # If json successfully loaded, use that. Else default to base template

    # Update backup right after loading (to save state before user performs any actions)
    file_management.update(database, 'data_autobackup.json')

    # Used to pass around non-persisted/contextual data, ie command used,
    context_template = {'last_printed': None, 'command': ''}
    # last_printed is used to tell what display to print after a command is used

    console_display.print_display(database)  # Initial main screen print

    while True:  # Main loop
        user_input = input().lower()  # Lower for string comparisons
        if not user_input:  # It's possible to enter nothing- continue loop
            console_display.print_display(database)  # Remove the newline from blank input by refreshing
            continue
        if not user_input.isascii():
            console_display.refresh_and_print(database, 'Please only use ASCII characters')
            continue

        user_input = user_input.split()  # Split into a list of space-separated terms
        commands.alias_format(user_input)  # Reformats input list according to alias dict
        command = user_input[0]

        context = context_template.copy()
        context['command'] = command

        print()  # Newline to separate input from printing
        try:
            # Try to get corresponding function from commands.py
            # Command functions have '_command' appended to name, ie daily_command()
            command_function = getattr(commands, command + '_command')
        except AttributeError:  # If function is not found
            console_display.refresh_and_print(database, "Invalid command! Use 'help' for help!")
            continue

        # Continue to command execution
        try:
            command_function(database, context, user_input[1:])  # (database, context, args)
        except errors.InvalidCommandUsage as error:
            print(f'help for {error.command} {error.subcommand} :)')  # Placeholder, will implement info lookup


if __name__ == '__main__':
    main()
