import os  # For os.system('cls')
import documentation
import console_display
import dict_management  # For objective_search
import file_management  # For saving


def launch_history_interface(database, dict_name):
    def print_current_page():
        # Header
        print(f'Page {current_page:,}/{total_pages:,} ({total_keys:,} items total):', end='\n\n')

        index_offset = (current_page - 1) * keys_per_page  # Skip past prior pages
        keys_left_on_page = total_keys - (current_page - 1) * keys_per_page
        # Get min between keys_per_page and # of keys left for that page (so last page doesn't index error)
        for n in range(min(keys_per_page, keys_left_on_page)):  # Iterate for # of items to print on that page
            # Start printing from the desired index
            # value is a dict of {display_name, times_completed, denominator, total_percent_completed, first_completed}
            index = index_offset + n
            value = dictionary[keys[index]]

            times_completed = value['times_completed']
            total_percent_completed = value['total_percent_completed']

            print(f"#{console_display.print_commas(index + 1)}: {value['display_name']}\n"
                  f"-----------------------------------\n"
                  f">>> Times completed: {console_display.print_commas(times_completed)}\n"
                  f">>> Denominator sum: {console_display.print_commas(times_completed * value['denominator'])}\n"
                  f">>> Total % completed: {console_display.print_commas(total_percent_completed, percent=True)}\n"
                  f">>> Average % completed: "
                  f"{console_display.print_commas(total_percent_completed/times_completed, percent=True)}", end='\n\n')

    def key_index_to_page(key_index):  # key_index starts counting from 0
        return 1 + key_index // keys_per_page  # 0 = 0 page, 1-20 = 1 page, 21-40 = 2 pages w/ 20

    def print_header():
        print(f"Entered the [{dict_name}] history interface\n"
              f"Normal commands will not work until interface is exited ('exit')\n"
              f"'help' for help", end='\n\n')

    def refresh_display():
        os.system('cls')
        print_header()
        print_current_page()

    dictionary = database['history'][dict_name]
    keys = list(dictionary)
    total_keys = len(keys)

    current_page = 1  # Default page
    keys_per_page = 5
    total_pages = key_index_to_page(total_keys - 1)  # Get page # of the last key. len starts at 1, index starts at 0

    print_header()
    print_current_page()
    print()  # Newline to separate input from print

    while True:
        user_input = input().lower().split()
        if not user_input:
            console_display.print_display(database)
            return
        input_length = len(user_input)
        command = user_input[0]
        print()  # Newline to separate input from print

        if input_length > 2:
            refresh_display()
            print('Unnecessary arguments!', end='\n\n')
            continue

        if command in {'next', 'n'}:
            pages_to_next = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    refresh_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                pages_to_next = eval(second_parameter)
            current_page += pages_to_next
            if current_page > total_pages:
                current_page = total_pages
            refresh_display()

        elif command in {'previous', 'p'}:
            pages_to_previous = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    refresh_display()
                    print('Invalid parameter. Only allows positive integers', end='\n\n')
                    continue
                pages_to_previous = eval(second_parameter)
            current_page -= pages_to_previous
            if current_page < 1:
                current_page = 1
            refresh_display()

        elif command in {'page', 'pg'}:
            if input_length < 2:
                refresh_display()
                print('Missing required arg!', end='\n\n')
                continue
            page_index = user_input[1]
            try:
                page_index = eval(page_index)
            except (NameError, SyntaxError):
                refresh_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue
            if not isinstance(page_index, int):
                refresh_display()
                print('Invalid page, must be an integer', end='\n\n')
                continue

            if page_index < 0:
                page_index += total_pages - 1  # ie 5 pages and -1 index.. -1 + 5 + 1 = 5th page.
                # -1 at the end because negative indexing starts at -1, not -0; so an offset correction is needed
            current_page = page_index
            if current_page > total_pages:
                current_page = total_pages
            elif current_page < 1:  # If 0 was given or a negative index exceeding total keys
                current_page = 1
            refresh_display()

        elif command in {'find', 'f'}:
            if input_length < 2:
                refresh_display()
                print('Missing required arg!', end='\n\n')
                continue
            item_name = user_input[1]
            item_index = 0
            for key in keys:
                if key.startswith(item_name):
                    break
                item_index += 1
            if item_index == total_keys:  # If loop went through all and found nothing, they will be equal
                refresh_display()
                print('Item not found', end='\n\n')
                continue
            current_page = key_index_to_page(item_index)
            refresh_display()

        elif command in {'tag'}:
            # tag add
            # tag remove
            # tag edit

            if input_length < 2:
                refresh_display()
                print('Missing required arg!', end='\n\n')
                continue
            mode = user_input[1]
            if not mode in {'add', 'remove', 'edit'}:
                refresh_display()
                print("Invalid mode. Expected 'add', 'remove', or 'edit'", end='\n\n')
                continue
            
            print('Enter item name', end='\n\n')
            item_name = input().lower()
            if not (item_value := dict_management.objective_search(database, dictionary, item_name)):
                refresh_display()
                print('Item could not be found', end='\n\n')
                continue
            item_tags = dictionary[item_name]['tags']
            tags_length = len(item_tags)

            if mode == 'add':
                print('At what index should the tag be inserted? (Starts at 0) (Blank = put at end)', end='\n\n')
                item_index = input()
                if not item_index:
                    item_index = tags_length
                elif item_index.isnumeric():
                    item_index = eval(item_index)
                else:
                    refresh_display()
                    print('Index must be a positive integer', end='\n\n')
                    continue
                print('Enter tag text (Blank to cancel)', end='\n\n')
                tag_text = input()
                if not tag_text:
                    refresh_display()
                    print('Cancelled tag add', end='\n\n')
                    continue
                item_tags.insert(item_index, tag_text)
                file_management.update(database)
                refresh_display()
                print('Successfully added tag', end='\n\n')
                
            elif mode == 'remove':
                print('What index should be deleted? (Starts at 0) (Blank = cancel)', end='\n\n')
                item_index = input()
                if not item_index:
                    refresh_display()
                    print('Cancelled tag remove', end='\n\n')
                    continue
                elif item_index.isnumeric():
                    item_index = eval(item_index)
                else:
                    refresh_display()
                    print('Index must be a positive integer', end='\n\n')
                    continue
                while True:
                    print(f'Remove tag {item_index}? (y/n) [{item_tags[item_index]}]', end='\n\n')
                    user_response = input().lower()
                    if user_response in {'yes', 'y', 'no', 'n'}:
                        break
                if user_response in {'no', 'n'}:
                    refresh_display()
                    print('Cancelled tag remove', end='\n\n')
                    continue
                item_tags.pop(item_index)
                file_management.update(database)
                refresh_display()
                print('Successfully removed tag', end='\n\n')

            elif mode == 'edit':
                print('What index should be edited? (Starts at 0) (Blank = cancel)', end='\n\n')
                item_index = input()
                if not item_index:
                    refresh_display()
                    print('Cancelled tag edit', end='\n\n')
                    continue
                elif item_index.isnumeric():
                    item_index = eval(item_index)
                else:
                    refresh_display()
                    print('Index must be a positive integer', end='\n\n')
                    continue
                print('Enter tag text (Blank to cancel)', end='\n\n')
                tag_text = input()
                if not tag_text:
                    refresh_display()
                    print('Cancelled tag edit', end='\n\n')
                    continue
                item_tags[item_index] = tag_text
                file_management.update(database)
                refresh_display()
                print('Successfully edited tag', end='\n\n')

        elif command == 'help':
            refresh_display()
            documentation.print_history_commands()

        elif command in {'exit', 'e'}:
            console_display.print_display(database)
            print('Returned to menu', end='\n\n')
            return
        else:
            refresh_display()
            print("Invalid command ('exit' or enter blank to return to normal menu)", end='\n\n')
        print()  # Newline to separate input from print
