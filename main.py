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
# TODO: Setting for sorting counter by numerator
# TODO: Option to combine history entries
# TODO: show list of options in groupchange
# TODO: Way to view links. When you link, should also specify dict type
# TODO: Break command, indicate a daily isn't needed today
# TODO: Fix display settings stuff
# TODO: Banner text, "Daily completion (by # of items): x/y (z%)

# TODO: Pause system
# TODO: Individual item streak backend
# TODO: Pluralize items in minimized container display
# TODO: Figure out weird history forced automatch
# TODO: Add way to rename history item & update references
# TODO: Move toggles to a toggle section?
# TODO: Automatch for toggle settings
# TODO: Give backup an arg for name
# TODO: Add todo by DATE
# TODO: Individual Group sort override
# TODO: Setting for cycle preview
# TODO: Start cd for mode 2 cycles
# TODO: Full cycle toggle redesign (currently broken)
# TODO: Avoid scenarios where you have to close to cancel? (ie submitting a tag)
# TODO: Completion links
# TODO: a get_item() func instead of copy/pasting validating args and then searching in a dict
# TODO: depth param in update feels sloppy
# TOOD: idk how I feel about the whole printing system rn
import commands  # Command functions and formatting
import errors
from console_display import refresh_display
from database import save

# main gets input
# -> checks for validity and matching command. If found, pass to commands.py
# -> Corresponding command function executes


def main():
    # Make backup before user performs any actions
    save('data_autobackup.json')

    # Used to pass around non-persisted/contextual data, ie command used,
    context_template = {'last_printed': None, 'command': ''}
    # last_printed is used to tell what display to print after a command is used

    refresh_display()  # Initial main screen print

    while True:  # Main loop
        user_input = input().lower()  # Lower for string comparisons
        if not user_input:  # It's possible to enter nothing- continue loop
            refresh_display()
            continue
        if not user_input.isascii():
            refresh_display('Please only use ASCII characters')
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
            refresh_display("Invalid command! Use 'help' for help!")
            continue

        # Continue to command execution
        try:
            command_function(context, user_input[1:])  # (context, args)
        except errors.InvalidCommandUsage as error:
            print(f'help for {error.command} {error.subcommand} :)\n')  # Placeholder, will implement info lookup


if __name__ == '__main__':
    main()
