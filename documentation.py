import os


def get_modules():
    modules = ('dictionary', 'display', 'settings', 'file')
    return modules


def get_dictionary_list(database):
    dictionary_list = [database['daily'], database['optional'], database['todo'], database['cycle'],
                       database['longterm'], database['counter'], database['note']]
    return dictionary_list


def get_dictionary_names():
    dictionaries = ('daily', 'optional', 'todo', 'cycle', 'longterm', 'counter', 'note')
    return dictionaries


def get_goal_dictionary_names():
    goal_dictionaries = ('daily', 'optional', 'todo', 'cycle', 'longterm')
    return goal_dictionaries


def get_enforced_dict_names():
    enforced_dictionaries = ('daily', 'enforced_todo', 'active_cycle')
    return enforced_dictionaries


def get_modes(command):
    if command != 'daily' and command in get_goal_dictionary_names():
        command = 'goal'  # For any of the normal goal dictionaries other than daily (which have the same modes)
    modes_dict = {
        'goal': {'add', 'complete', 'reset', 'remove', 'retask', 'set', 'setall', 'update', 'rename', 'denominator',
                 'containercreate', 'containeradd', 'containeredit', 'tag'},
        'daily': {'add', 'complete', 'reset', 'remove', 'retask', 'set', 'setall', 'update', 'rename', 'denominator',
                  'containercreate', 'containeradd', 'containeredit', 'tag', 'link', 'unlink'},
        'counter': {'add', 'reset', 'remove', 'retask', 'set', 'setall', 'update', 'rename'},
        'note': {'add', 'remove', 'edit', 'position', 'swap'}
    }
    return modes_dict[command]


def get_command_alias():
    command_alias_dict = {
        'c': 'cycle',
        'com': 'complete',
        'd': 'daily',
        'o': 'optional',
        't': 'todo',
        'p': 'print'
    }
    return command_alias_dict


def get_mode_alias():
    mode_alias_dict = {
        'a': 'add',
        'c': 'complete',
        'del': 'remove'
    }
    return mode_alias_dict


def print_help(command=None):
    modules = get_modules()
    if command is None:  # No specific command given, print general help
        print("<> = parameter, [] = optional, () = choose between", end='\n\n')
        for module in modules[:-1]:  # Splice out the last one to avoid extra newline
            print(f'{module.capitalize()}:', end='\n\n')
            print_module(module)
            print('\n')  # Extra newline
        print(f'{modules[-1].capitalize()}:', end='\n\n')
        print_module(modules[-1])
    else:  # Specific command given
        for module_name in modules:
            module = get_module(module_name)
            if command in module:
                print(module[command])
                return
            else:
                print('Command not found')


def print_submodule(command, submodule=None):
    dictionaries = get_dictionary_names()
    goal_dictionaries = get_goal_dictionary_names()
    if command not in dictionaries:
        print('That command does not have submodules')
        return
    if command in goal_dictionaries:
        if submodule:  # If specific one
            pass
        else:  # No specific one, print general
            print()
    elif command == 'counter':
        pass


def print_toggle_help():
    os.system('cls')
    print("toggle <keyword>\n"
          "[Keyword]: <description>\n"
          "'settings' to view current values\n\n"
          ">>> Settings to display dictionaries in main display (doesn't impact commands like 'dailies')\n\n"
          "[daily]: Show dailies\n"
          "[todo]: Show to-dos\n"
          "[cycle]: Show active cycle objectives\n"
          "-> [full_cycle]: Show inactive cycle objectives as well (requires 'cycle' enabled to work)\n"
          "[longterm]: Show longterms\n"
          "[counter]: Show counters\n"
          "[note]: Show notes\n\n\n"
          ">>> Show these things in main display header\n\n"
          "[date_switch]: Display DD/MM instead of MM/DD\n"
          "[welcome]: Show welcome message\n"
          "[display_total]: Include overall number of completed daily objectives\n\n\n"
          ">>> Dictionary functionality\n\n"
          "[auto_match]: If a given objective isn't found,"
          " automatically match to the closest without confirmation\n"
          "              (looks for as a substring; prioritizes matches *starting with* the substring)", end='\n\n')


def print_history_commands():
    print("\n'next'/'n', 'previous'/'p', 'page <#>'/'pg <#>', 'find <obj>'/'f <item value>', 'help', 'exit'\n"
          "Notes:\n"
          "- Can also provide a number with next/previous, ie 'next 5' goes forward 5 pages\n"
          "- 'exit' or enter blank to return to main menu")


def print_modules():
    print(get_modules())


def print_module(module_name):
    modules = get_modules()
    if module_name not in modules:
        print('Invalid module name')
        return

    module = get_module(module_name)
    values = tuple(module.values())
    for value in values[:-1]:  # Splice to avoid extra newline after the last one
        print(value, end='\n\n')
    for value in values[-1:]:
        print(value)


def get_module(module_name):
    if module_name == 'dictionary':
        return dictionary_module
    elif module_name == 'display':
        return display_module
    elif module_name == 'settings':
        return settings_module
    elif module_name == 'file':
        return file_module
    else:
        raise ValueError("Invalid module name")


def print_alias():
    print("'update': special form '+<name> (value)', ie daily +wanikani 5\n")


# Template:
#           - command
#           Usage:
#           ex: (skipped if usage has no parameters)
#           Notes (optional)
# <> = parameter
# [] = optional
# () = choose between
# ... = Can be a variable amount required (including none)

dictionary_module = {
    'daily': "- 'daily'\n"
             "Usage: daily <mode> ...\n"
             "Modes: add, complete, denominator, remove, rename, reset, retask, setall, update\n"
             "ex: daily add\n"
             "ex: daily update some_task 5\n"
             "Note: See submodule help for more info on a mode (ie 'help daily add')",
    'optional': "- 'optional'\n"
                "Usage: optional <mode> ...\n"
                "Modes: add, complete, denominator, remove, rename, reset, retask, setall, update\n"
                "ex: optional add\n"
                "ex: optional complete some_task\n"
                "Note: See submodule help for more info on a mode (ie 'help optional update')",
    'todo': "- 'todo'\n"
            "Usage: todo <mode> ...\n"
            "Modes: add, complete, denominator, remove, rename, reset, retask, setall, update\n"
            "ex: todo add\n"
            "ex: todo reset some_task\n"
            "Note: See submodule help for more info on a mode (ie 'help todo complete')",
    'cycle': "- 'cycle'\n"
             "Usage: cycle <mode> ...\n"
             "Modes: add, complete, denominator, remove, rename, reset, retask, setall, update\n"
             "ex: cycle add\n"
             "ex: cycle setall (complete/reset)\n"
             "Note: See submodule help for more info on a mode (ie 'help cycle reset')",
    'longterm': "- 'longterm'\n"
             "Usage: longterm <mode> ...\n"
             "Modes: add, complete, denominator, remove, rename, reset, retask, setall, update\n"
             "ex: longterm add\n"
             "ex: longterm denominator some_item <new_value>\n"
             "Note: See submodule help for more info on a mode (ie 'help longterm setall')",
    'counter': "- 'counter'\n"
             "Usage: counter <mode> ...\n"
             "Modes: add, remove, rename, reset, retask, setall, update\n"
             "ex: counter add\n"
             "ex: counter retask some_item\n"
             "Note: See submodule help for more info on a mode (ie 'help counter retask')",
    'complete': "- 'complete'\n"
                "Usage: complete <dictionary>\n"
                "ex: complete todo\n"
                "Note: Sets all active members of the dictionary to completed",
    'reset': "- 'reset'\n"
             "Usage: reset <dictionary>\n"
             "ex: reset cycle\n"
             "Note: Sets all active members of the dictionary to 0 progress (0 numerator)",
    'delete': "- 'delete'\n"
              "Usage: delete <dictionary>\n"
              "ex: delete daily\n"
              "Note: COMPLETELY erases data of the given dictionary",
    'endday': "- 'endday'\n"
              "Usage: endday\n"
              "Note: Marks the day as over\n"
              "Date/day ticks over one, and completion/streak/etc. calculations are performed\n"
              "Designed to be used according to your 'relative' day"
}

display_module = {
    'dailies': "- 'dailies'\n"
               "Usage: dailies\n"
               "Note: Displays only the daily dictionary (and optional dictionary if applicable)",
    'todos': "- 'todos'\n"
             "Usage: todos\n"
             "Note: Displays only the to-do dictionary",
    'cycles': "- 'cycles'\n"
              "Usage: cycles\n"
              "Note: Displays only the cycle dictionary (both actives & inactives)",
    'longterms': "- 'longterms'\n"
                 "Usage: longterms\n"
                 "Note: Displays only the longterm dictionary",
    'counters': "- 'counters'\n"
                "Usage: counters\n"
                "Note: Displays only the counter dictionary",
    'print': "- 'print'\n"
             "Usage: print\n"
             "Note: Clears console, prints display",
    'stats': "- 'stats'\n"
             "Usage: stats\n"
             "Note: Prints some user statistics",
    'help': "- 'help'\n"
            "Usage: help <command> ...\n"
            "ex: help\n"
            "ex: help cycle\n"
            "ex: help todo add\n"
            "Note: Without parameters, prints full help display\n"
            "Note: If command is specified, print base-level help display\n"
            "Note: For commands with modes, mode can be specified to view the submodule in greater detail"
}

settings_module = {
    'settings': "- 'settings'\n"
                "Usage: settings\n"
                "Note: Lists all settings and their current value",
    'toggle': "- 'toggle'\n"
              "Usage: toggle <setting>\n"
              "ex: toggle automatch\n"
              "Note: Toggles the given setting (on to off or off to on)",
    'setday': "- 'setday'\n"
              "Usage: setday <day>\n"
              "ex: setday monday\n"
              "Note: Sets the weekday accordingly. Set from the start\n"
              "Note: WARNING: Changing date resets streak, and clears the cycle dictionary",
    'setdate': "- 'setdate'\n"
               "Usage: setdate <MM> <DD>\n"
               "ex: setdate 5 26\n"
               "Note: Sets the date. MM-DD format\n"
               "Note: WARNING: Changing date resets streak, and clears the cycle dictionary",
}

file_module = {
    'backup': "- 'backup'\n"
              "Usage: backup\n"
              "Note: Creates a manual backup. This is separate from the automatic backup\n"
              "Note: The automatic backup is created upon successful loading, when the program is launched",
    'exit': "- 'exit'\n"
            "Usage: exit\n"
            "Note: Terminates the program",
}
