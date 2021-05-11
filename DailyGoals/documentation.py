def print_help(command=None):
    if not command:  # If not a specific command
        print("<> = parameter, [] = optional, () = choose between", end='\n\n')
        for module in modules[:-1]:
            print(f'{module.capitalize()}:')
            print_module(module)
            print('\n')  # Extra newline
        for module in modules[-1:]:
            print(f'{module.capitalize()}:')
            print_module(module)
    else:  # A specific command
        for module_name in modules:
            module = get_module(module_name)
            if command in module:
                print(module[command])
                return
        else:
            print('Command not found')


def print_help():
    print("Commands shown in apostrophes ''. Value fields in angled brackets <>\n"
          "Optional parameters in brackets [] (optional parameters can be skipped)\n"
          "'help'\n"
          "  - Displays this dialog\n"
          "'add <objective> <task> [single]'\n"
          "  - Adds <objective> with <task> (space-separated)\n"
          "  - \"single\" specifies an objective as one-time (deleted after day)\n"
          "  - Examples:\n"
          "    add wanikani 50_reviews\n"
          "    add clean desk,floor single\n"
          "'update <objective> <decimal % to ADD>'\n"
          "  - Updates objective to +% completion\n"
          "  - Works with fractions.\n"
          "  - Examples:\n"
          "    update wanikani 0.5\n"
          "    update wanikani 2/6\n"
          "'remove <objective>'\n"
          "  - Deletes the objective\n"
          "'exit', 'quit', 'stop'\n"
          "  - Closes program")



def print_modules():
    print(modules)


def print_module(module_name):
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
    if module_name == 'item':
        return item_module
    elif module_name == 'display':
        return display_module
    elif module_name == 'settings':
        return settings_module
    elif module_name == 'file':
        return file_module
    else:
        raise ValueError("Invalid module name")


def print_alias():
    print("'adjustednet': 'anet', 'an'\n"
          "'buy': 'b'\n"
          "'dividend': 'div', 'd'\n"
          "'expand': 'e'\n"
          "'fee': 'f'\n"
          "'history': 'h'\n"
          "    'next': 'n'\n"
          "    'previous': 'p'\n"
          "    'page': 'pg'\n"
          "    'refresh': 'r'\n"
          "    'exit': 'e':\n"
          "'sell': 's'\n"
          "'watchlist': 'wl'\n"
          "    'peaks': 'peak', 'p'\n"
          "'yes': 'y'\n"
          "'no': 'n'\n"
          "'cancel': 'c'\n"
          "'exit': 'quit', 'stop'"
          )


modules = ('item', 'display', 'settings', 'file')

# Template:
#           - command
#           Usage:
#           ex: (skipped if usage has no parameters)
#           Notes (optional)
# <> = parameter
# [] = optional
# () = choose between

item_module = {
    'buy': "- 'buy'\n"
           "Usage: buy <quantity> <symbol> <cost each> [<YEAR-MONTH-DATE date>]\n"
           "ex: buy 1 cake 59.01\n"
           "ex: buy 1 pfe 38.35 2021-04-30\n"
           "Note: When providing a date, trailing zeroes are optional (will be formatted anyway)\n"
           "Note: Date will be ignored if it's not the first time obtaining the item.\n"
           "Note: Change date manually in dat file if wrong one was given.",
    'dividend': "- 'dividend'\n"
                "Usage: dividend <symbol> <amount>\n"
                "ex: dividend abbv 15.12\n"
                "Note: Used to track dividends from an item (affects net too)",
    'fee': "- 'fee'\n"
           "Usage: fee <symbol> <amount>\n"
           "ex: fee cake 0.01\n"
           "Note: Used to track trade fees from an item (affects net too)",
    'remove': "- 'remove'\n"
              "Usage: remove <mode (current/history)> <item>\n"
              "ex: remove current cake\n"
              "Note: Used to remove an item forcefully (different than selling for 0; doesn't count as an action)",
    'sell': "- 'sell'\n"
            "Usage: sell <quantity> <symbol> <price each>\n"
            "ex: sell 1 cake 59.55"
}

display_module = {
    '$': "- '$'\n"
         "Usage: $\n"
         "Note: Prints live price of items currently owned",
    'adjustednet': "- 'adjustednet'\n"
                   "Usage: adjustednet\n"
                   "Note: Prints net that factors live value of currently-owned items",
    'alias': "- 'alias'\n"
             "Usage: alias\n"
             "Note: Displays all text shortcuts",
    'expand': "- 'expand'\n"
              "Usage: expand <item>\n"
              "Note: Displays extra information on an item from your history database",
    'help': "- 'help'\n"
            "Usage: help [<command>]\n"
            "ex: help buy\n"
            "Note: Prints usage information",
    'high': "- 'high'\n"
            "Usage: high\n"
            "Note: Prints live daily high price of all items currently owned",
    'history': "- 'history'\n"
               "Usage: history\n"
               "Note: Enters the history interface. Records long-term data\n"
               "Note: When an item is currently owned, includes unsettled category\n"
               "Note: Unsettled category shows live price per, not bought cost basis like 'list'",
    'list': "- 'list'\n"
            "Usage: list\n"
            "Note: Displays currently-owned items and their cost basis",
    'low': "- 'low'\n"
           "Usage: low\n"
           "Note: Prints live daily low price of all items currently owned",
    'module': "- 'module'\n"
              "Usage: module [<module name>]\n"
              "ex: module item\n"
              "Note: 'module' alone lists modules. When specified, print command help of a module",
    'peaks': "- 'peaks'\n"
             "Usage: peaks\n"
             "Note: Prints live daily peak (low, high) prices of all items currently owned",
    'watchlist': "- 'watchlist'\n"
                 "Usage: watchlist [((add/remove) <item>, peaks)]\n"
                 "ex: watchlist\n"
                 "ex: watchlist add otgly\n"
                 "ex: watchlist peaks\n"
                 "Note: When alone, display watchlist items. Can also add/remove items"
}

settings_module = {
    'settings': "- 'settings'\n"
                "Usage: settings\n"
                "Note: Displays current settings",
    'automatch': "- 'automatch'\n"
                 "Usage: automatch\n"
                 "Note: Toggles automatch"
                 "Note: When item specified isn't found, looks for recorded items starting with search term\n"
                 "Note: Automatch automatically proceeds without confirmation if one is found\n"
                 "Note: Affects sell, expand, fee, and dividend"
}

file_module = {
    'backup': "- 'backup'\n"
              "Usage: backup\n"
              "Note: Creates a manual backup, separate from the automatic one",
    'reset': "- 'reset'\n"
             "Usage: reset\n"
             "Note: WIPES ALL DATA. Asks for confirmation first.",
    'start': "- 'start'\n"
             "Usage: start [YEAR-MONTH-DATE date]\n"
             "ex: start"
             "ex: start 2021-04-01"
             "Note: Lets you set an initial date. Just for display purposes\n"
             "Note: When providing a date, trailing zeroes are optional (will be formatted anyway)\n"
             "Note: Does nothing after the first time. Edit dat manually if need to change",
    'exit': "- 'exit'\n"
            "Usage: exit\n"
            "Note: Terminates the program"
}
