import documentation


def launch_history_interface(database, dict_name):
    def print_current_page():
        print(f'Page {current_page}/{total_pages}:', end='\n\n')

        keys_left_on_page = total_keys - (current_page - 1) * keys_per_page
        index_offset = (current_page - 1) * keys_per_page  # Skip past prior pages
        # Get min between keys_per_page and # of keys left for that page (so last page doesn't index error)
        for n in range(min(keys_per_page, keys_left_on_page)):  # Iterate for # of items to print on that page
            # Start printing from the desired index
            index = index_offset + n
            print(f'#{index + 1}: {dictionary[index]}')

    def key_index_to_page(key_place):  # key_index starts counting from 0
        return 1 + (key_place - 1) // keys_per_page  # 0 = 0 page, 1-20 = 1 page, 21-40 = 2 pages w/ 20

    dictionary = database['history'][dict_name]
    keys = list(dictionary)
    total_keys = len(keys)

    current_page = 1  # Default page
    keys_per_page = 10
    total_pages = key_index_to_page(total_keys - 1)  # Get page # of the last key. len starts at 1, index starts at 0

    print(f"Entered the [{dict_name}] history interface\n"
          f"Normal commands will not work until interface is exited ('exit')\n"
          f"'help' for help", end='\n\n')
    print_current_page()
    print()  # Newline to separate input from print

    while True:
        user_input = input().lower().split()
        input_length = len(user_input)
        command = user_input[0]
        print()  # Newline to separate input from print

        if input_length > 2:
            print('Invalid amount of parameters (expected 1 or 2)')
            continue

        if command in {'next', 'n'}:
            pages_to_next = 1  # Default
            if input_length == 2:  # Specific value given
                try:
                    pages_to_next = eval(user_input[1])
                except (NameError, SyntaxError, TypeError):
                    print('Invalid command usage, expected number of pages to jump')
                    continue
            current_page += pages_to_next
            if current_page > total_pages:
                current_page = total_pages
            print_current_page()

        elif command in {'previous', 'p'}:
            pages_to_previous = 1  # Default
            if input_length == 2:  # Specific value given
                try:
                    pages_to_previous = eval(user_input[1])
                except (NameError, SyntaxError, TypeError):
                    print('Invalid command usage, expected number of pages to jump')
                    continue
            current_page -= pages_to_previous
            if current_page < 1:
                current_page = 1
            print_current_page()

        elif command in {'page', 'pg'}:
            try:
                current_page = eval(user_input[1])
            except (NameError, SyntaxError, TypeError):
                print('Invalid command usage for history interface')
                continue

            if current_page > total_pages:
                current_page = total_pages
            elif current_page < 1:
                current_page = 1
            print_current_page()

        elif command in {'find', 'f'}:
            item_name = eval(user_input[1])
            try:
                item_index = keys.index(item_name)
            except ValueError:
                print('Item not found')
                continue
            current_page = key_index_to_page(item_index)
            print_current_page()

        elif command == 'help':
            documentation.print_history_commands()

        elif command in {'exit', 'e'}:
            print('Returning to menu')

        else:
            print('Invalid command')
        print()  # Newline to separate input from print
