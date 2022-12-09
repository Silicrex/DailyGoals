import os  # For os.system('cls')

import date_logic
import documentation
import console_display
import dict_management  # For key_search
import file_management  # For saving


def launch_history_interface(database, dict_name):
    def print_current_page():
        # Header
        print(f'Page {current_page:,}/{total_pages:,} '
              f'({total_keys:,} {console_display.pluralize("item", total_keys)} total):', end='\n\n')

        index_offset = (current_page - 1) * keys_per_page  # Skip past prior pages
        keys_left = total_keys - (current_page - 1) * keys_per_page
        # Get min between keys_per_page and # of keys left for that page (so last page doesn't index error)
        for n in range(min(keys_per_page, keys_left)):  # Iterate for # of items to print on that page
            # Start printing from the desired index
            # value is a dict of {display_name, times_completed, denominator, total_percent_completed, first_completed}
            index = index_offset + n
            print_item(index)

    def print_item(index):
        history_value = dictionary[keys[index]]
        tags_container = history_value['tags']
        times_completed = history_value['times_completed']
        first_completed = date_logic.string_date(database, history_value['first_completed'])

        print(f"#{index + 1:,}: {history_value['display_name']}\n"
              f"-----------------------------------\n"
              f">>> Times goal completed: {times_completed:,}\n"
              f">>> Denominator sum: {times_completed * history_value['denominator']:,}\n"
              f">>> First completed: {first_completed}\n"
              f">>> Tags: {len(tags_container)}")
        print()  # Newline

    def print_header():
        print(f"Entered the [{dict_name}] history interface\n"
              f"Normal commands will not work until interface is exited (blank or 'exit')\n"
              f"'help' for help", end='\n\n')

    def print_display():
        os.system('cls')
        print_header()
        print_current_page()

    # Utility, main loop ------------------------------------------------------------------------------------------
    def key_index_to_page(key_index):  # key_index starts counting from 0
        return 1 + key_index // keys_per_page  # 0 = 0 page, 1-20 = 1 page, 21-40 = 2 pages w/ 20

    dictionary = database['history'][dict_name]
    keys = list(dictionary)
    total_keys = len(keys)

    current_page = 1  # Default page
    keys_per_page = 5
    total_pages = key_index_to_page(total_keys - 1)  # Get page # of the last key. len starts at 1, index starts at 0

    print_header()
    print_current_page()

    while True:
        user_input = input().lower().split()
        if not user_input:
            console_display.print_display(database)
            return
        input_length = len(user_input)
        command = user_input[0]
        print()  # Newline to separate input from print

        if input_length > 2:
            print_display()
            print('Unnecessary arguments!', end='\n\n')
            continue

        # Page commands ------------------------------------------------------------------------------------------
        if command in {'next', 'n'}:
            pages_to_next = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    print_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                pages_to_next = eval(second_parameter)
            current_page += pages_to_next
            if current_page > total_pages:
                current_page = total_pages
            print_display()

        elif command in {'previous', 'p'}:
            pages_to_previous = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    print_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                pages_to_previous = eval(second_parameter)
            current_page -= pages_to_previous
            if current_page < 1:
                current_page = 1
            print_display()

        elif command in {'page', 'pg'}:
            if input_length < 2:
                print_display()
                print('Missing required arg!', end='\n\n')
                continue
            page_index = user_input[1]
            try:
                page_index = eval(page_index)
            except (NameError, SyntaxError):
                print_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue
            if not isinstance(page_index, int):
                print_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue

            if page_index < 0:
                page_index += total_pages + 1  # ie 5 pages and -1 index.. -1 + 5 + 1 = 5th page.
                # -1 at the end because negative indexing starts at -1, not -0; so an offset correction is needed
            current_page = page_index
            if current_page > total_pages:
                current_page = total_pages
            elif current_page < 1:  # If 0 was given or a negative index exceeding total keys
                current_page = 1
            print_display()

        elif command in {'find', 'f'}:
            if input_length < 2:
                print_display()
                print('Missing required arg!', end='\n\n')
                continue
            item_name = user_input[1]
            item_index = 0
            for key in keys:
                if key.startswith(item_name):
                    break
                item_index += 1
            if item_index == total_keys:  # If loop went through all and found nothing, they will be equal
                print_display()
                print('Item not found', end='\n\n')
                continue
            current_page = key_index_to_page(item_index)
            print_display()

        # Tags ------------------------------------------------------------------------------------------
        elif command in {'tags', 'tag'}:
            # ex input: tags wanikani

            print()  # Newline to separate input from print
            item_name = ' '.join(user_input[1:])
            history_auto_match = database['settings']['history_auto_match']
            if not (item_name := dict_management.key_search(database, dictionary, item_name,
                                                            force_manual_match=history_auto_match)):
                print_display()
                print('Item could not be found', end='\n\n')
                continue
            tags = dictionary[item_name]['tags']
            os.system('cls')
            print_item(keys.index(item_name))  # print_item() goes by index, not by name
            print(f'Tags: {len(tags)}', end='\n\n')
            for tag in tags:
                print(f'[{date_logic.string_date(database, tag[0])}]:\n{tag[1]}', end='\n\n')  # Date:\ntag

        # Misc commands/not found --------------------------------------------------------------------------------------
        elif command == 'help':
            print_display()
            documentation.print_history_commands()

        elif command in {'exit', 'e'}:
            console_display.print_display(database)
            print('Returned to menu', end='\n\n')
            return
        else:
            print_display()
            print("Invalid command ('exit' or enter blank to return to normal menu)", end='\n\n')
