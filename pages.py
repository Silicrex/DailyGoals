import os  # for os.system('cls')
import console_display
import date_logic


class Pages:
    def __init__(self, dictionary):
        # Constructor args
        self.dictionary = dictionary

        # Base values
        self.keys = list(dictionary)
        self.total_keys = len(dictionary)
        self.current_page = 1
        self.keys_per_page = 5
        self.total_pages = self.key_index_to_page(self.total_keys - 1)

    def print_display(self):
        os.system('cls')
        self.print_header()
        self.print_current_page()

    def print_current_page(self):
        print(f'Page {self.current_page:,}/{self.total_pages:,} '
              f'({self.total_keys:,} {console_display.pluralize("item", self.total_keys)} total):', end='\n\n')

        index_offset = (self.current_page - 1) * self.keys_per_page  # Skip past prior pages
        keys_left = self.total_keys - (self.current_page - 1) * self.keys_per_page
        # Get min between keys_per_page and # of keys left (so last page doesn't index error)
        for n in range(min(self.keys_per_page, keys_left)):  # Print items on page
            index = index_offset + n
            self.print_item(index)

    def key_index_to_page(self, key_index):  # key_index starts counting from 0
        # Ex with keys_per_page = 10:
        # 0-9 = page 1, 10-19 = page 2
        return 1 + key_index // self.keys_per_page

    def print_header(self):
        print('[Header text]', end='\n\n')

    def print_item(self, index):  # index from the list of keys
        print(self.keys[index])

    def set_keys_per_page(self, value):
        self.keys_per_page = value


class HistoryPages(Pages):
    def __init__(self, database, dict_name):
        self.database = database
        self.dict_name = dict_name
        super().__init__(database['history'][dict_name])

    def print_header(self):
        print(f"Entered the [{self.dict_name}] history interface\n"
              f"Normal commands will not work until interface is exited (enter blank or 'exit')\n"
              f"'help' for help", end='\n\n')

    def print_item(self, index):
        history_value = self.dictionary[self.keys[index]]
        tags_container = history_value['tags']
        times_completed = history_value['times_completed']
        first_completed = date_logic.string_date(self.database, history_value['first_completed'])

        print(f"#{index + 1:,}: {history_value['display_name']}\n"
              f"-----------------------------------\n"
              f">>> Times goal completed: {times_completed:,}\n"
              f">>> Total completion value: {times_completed * history_value['denominator']:,}\n"
              f">>> First completed: {first_completed}\n"
              f">>> Tags: {len(tags_container)}")
        print()  # Newline


class LongtermPages(HistoryPages):
    def print_item(self, index):
        history_value = self.dictionary[self.keys[index]]
        tags_container = history_value['tags']
        times_completed = history_value['times_completed']
        first_completed = date_logic.string_date(self.database, history_value['first_completed'])

        print(f"#{index + 1:,}: {history_value['display_name']}\n"
              f"-----------------------------------\n"
              f">>> Completion status: {times_completed:,}\n"
              f">>> Date of completion: {first_completed}\n"
              f">>> Tags: {len(tags_container)}")
        print()  # Newline


class CounterPages(HistoryPages):
    def print_item(self, index):
        history_value = self.dictionary[self.keys[index]]
        tags_container = history_value['tags']

        print(f"#{index + 1:,}: {history_value['display_name']}\n"
              f"-----------------------------------\n"
              f">>> Highest value: {history_value['highest_value']:,}\n"
              f">>> Lowest value: {history_value['lowest_value']:,}\n"
              f">>> Tags: {len(tags_container)}")
        print()  # Newline
