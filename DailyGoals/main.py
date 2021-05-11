# Set to enforce ASCII just because it's what Windows cmd can display. Can be avoided if this is interfaced
# TODO: Help dialog, tutorial dialog, mention bakcup when running program
# TODO: Error handling/polishing

# TODO: Finish cycles (need to work around endday, fix for active vs inactive)
# TODO: Welcome messages
# TODO: uhhhh END DAY Cycles etc. count for streak, todo for total etc
#       Make the stats increment, make sure auto toggle actually does something
# TODO: Toggle a history dict. {'dict_type': {obj_name + task_string: times done}}
#       Long-term one doesn't need a count
#       Pages
#       History combine command to sum up different objects that refer to the same exact thing
# TODO: Move command aliases up so it doesn't unnecessarily check for alias string twice
# TODO: Notes/reminders box
# TODO: Okay... So to fix the messy disable/enable module print thing, make list comp/get dict system and generate
#       based on toggle flags
# TODO: Probably not going to do this, but interactive welcome messages? Lets you respond so they can be dynamic..
#       If I do though, add a reset command for welcome memory. Ehhhh I think this would require an interface lol
#       Make welcome message only roll once a day instead? Go from there?
# TODO: Enforce full cycle requriing normal cyclet gogel eonon
# TODO: toggle default settings
# TODO: Sort completed to bottom
# TODO: SORT INACTIVE
# TODO: don't always need a task... and maybe allow spaces in obj name
# TODO: change list stuff to dict for key organization? <<<<<<<<<<<<<<
# TODO: warn about clearing
# TODO: idk.. option to hide completed?
# TODO: maybe rename dicts
# TODO: print help on the command for commands not being used right?
import file_management  # For loading/saving
import command_flow_logic  # To pass input to for interpretation
import console_display  # To print the initial console display


def main():
    database = file_management.load_data()  # If json successfully loaded, use that. Else default to base template.

    # Update backup right after loading (to save state before user performs any actions)
    file_management.update(database, 'data_autobackup.json')

    console_display.print_display(database)

    while True:
        user_input = input().lower()  # Lower for string comparisons
        if not user_input:  # It's possible to enter nothing
            continue
        if not user_input.isascii():
            print('Please only use ASCII characters')
            continue
        user_input = user_input.split()  # Split into a list of space-separated terms
        command_flow_logic.command_flow(database, user_input)  # Pass input to command_flow() to be handled


if __name__ == '__main__':
    main()
