import os  # For os.system('cls')

import date_logic
import documentation
import console_display
import dict_management  # For key_search
import file_management  # For saving
import pages


def launch_history_interface(database, dict_name):
    keys_per_page = database['settings']['history_keys_per_page']
    if dict_name in {'longterm', 'counter'}:  # Special Pages subclasses
        pm = getattr(pages, dict_name.capitalize() + 'Pages')(database, dict_name)  # ie LongtermPages()
    else:
        pm = pages.HistoryPages(database, dict_name)  # Page manager
    pm.set_keys_per_page(keys_per_page)
    launch_pages_interface(database, pm, dict_name)


def launch_tags_interface(database, objective_name, dictionary):
    keys_per_page = database['settings']['tags_keys_per_page']
    pm = pages.TagPages(objective_name, dictionary)
    pm.set_keys_per_page(keys_per_page)
    launch_pages_interface(database, pm, 'tags')


def launch_pages_interface(database, pm, mode):
    pm.print_display()
    while True:
        user_input = input().lower().split()
        if not user_input or user_input[0] in {'exit', 'e'}:  # Exit
            return
        print()  # Newline to separate input from print
        input_length = len(user_input)
        command = user_input[0]

        if input_length > 2:
            pm.print_display()
            print('Unnecessary arguments!', end='\n\n')
            continue

        # Page commands ------------------------------------------------------------------------------------------
        if command in {'next', 'n'}:
            value = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    pm.print_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                value = eval(second_parameter)
            pm.next_page(value)
            pm.print_display()

        elif command in {'previous', 'prev', 'p'}:
            value = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    pm.print_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                value = eval(second_parameter)
            pm.prev_page(value)
            pm.print_display()

        elif command in {'page', 'pg'}:
            if input_length < 2:
                pm.print_display()
                print('Missing required arg!', end='\n\n')
                continue
            value = user_input[1]
            try:
                value = eval(value)
            except (NameError, SyntaxError):
                pm.print_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue
            if not isinstance(value, int):
                pm.print_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue

            if value < 0:  # For negative indexing
                value += pm.total_pages + 1  # ie 5 pages and -1 index.. -1 + 5 + 1 = 5th page.
                # -1 at the end because negative indexing starts at -1, not -0; so an offset correction is needed
            pm.set_page(value)
            pm.print_display()

        elif command in {'find', 'f'}:
            if input_length < 2:
                pm.print_display()
                print('Missing required arg!', end='\n\n')
                continue
            item_name = user_input[1]
            item_index = 0
            for key in pm.keys:
                if key.startswith(item_name):
                    break
                item_index += 1
            if item_index == pm.total_keys:  # If loop went through all and found nothing
                pm.print_display()
                print('Item not found', end='\n\n')
                continue
            pm.current_page = pm.key_index_to_page(item_index)  # Found
            pm.print_display()

        # Tags ------------------------------------------------------------------------------------------
        elif command in {'tags', 'tag', 't'} and mode != 'tags':
            # ex input: tags wanikani

            print()  # Newline to separate input from print
            item_name = ' '.join(user_input[1:])
            history_auto_match = database['settings']['history_auto_match']
            if not (item_name := dict_management.key_search(database, pm.dictionary, item_name,
                                                            force_manual_match=history_auto_match)):
                pm.print_display()
                print('Item could not be found', end='\n\n')
                continue
            tags = pm.dictionary[item_name]['tags']
            launch_tags_interface(database, item_name, tags)
            pm.print_display()

        # Misc commands/not found --------------------------------------------------------------------------------------
        elif command == 'help':
            pm.print_display()
            pm.print_help()

        else:
            pm.print_display()
            print("Invalid command ('exit' or enter blank to return to normal menu)", end='\n\n')
