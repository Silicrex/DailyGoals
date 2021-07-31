import os  # For os.system('cls')
import documentation
import console_display


def launch_history_interface(database, dict_name):
    def print_current_page():
        print(f'Page {console_display.print_commas(current_page)}/{console_display.print_commas(total_pages)} '
              f'({console_display.print_commas(total_keys)} items total):', end='\n\n')

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

            avg_percent_completed_str = '{:,.2%}'.format(total_percent_completed/times_completed)
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
    keys_per_page = 10
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
            print('Invalid amount of parameters (expected 1 or 2)')
            continue

        if command in {'next', 'n'}:
            pages_to_next = 1  # Default
            if input_length == 2:  # Specific value given
                second_parameter = user_input[1]
                if not second_parameter.isnumeric():
                    refresh_display()
                    print('Invalid parameter. Only allows positive integers')
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
                    print('Invalid parameter. Only allows positive integers')
                    continue
                pages_to_previous = eval(second_parameter)
            current_page -= pages_to_previous
            if current_page < 1:
                current_page = 1
            refresh_display()

        elif command in {'page', 'pg'}:
            if len(user_input) != 2:
                refresh_display()
                print('Invalid # of parameters. Expected 2')
                continue
            second_parameter = user_input[1]
            if not second_parameter.isnumeric():
                refresh_display()
                print('Invalid parameter. Only allows positive integers')
                continue
            current_page = eval(second_parameter)
            if current_page > total_pages:
                current_page = total_pages
            elif current_page < 1:
                current_page = 1
            refresh_display()

        elif command in {'find', 'f'}:
            item_name = user_input[1]
            try:
                item_index = keys.index(item_name)
            except ValueError:
                refresh_display()
                print('Item not found')
                continue
            current_page = key_index_to_page(item_index)
            refresh_display()

        elif command == 'help':
            refresh_display()
            documentation.print_history_commands()

        elif command in {'exit', 'e'}:
            print('Returning to menu')
            return
        else:
            refresh_display()
            print("Invalid command ('exit' or enter blank to return to normal menu)")
        print()  # Newline to separate input from print
