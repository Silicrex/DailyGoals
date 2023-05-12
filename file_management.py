import os  # To check if json file exists yet
import json  # For dumping/loading database

import welcome_messages

PROGRAM_VERSION = 'PRE-RELEASE'


def get_template_dict():  # Database structure
    template_dict = {
        # Welcome
        'welcome_message': None,
        # Main data
        'version': PROGRAM_VERSION,
        'daily': {},  # Dailies dictionary
        'optional': {},  # Optional dailies dictionary
        'todo': {},  # To-do dictionary
        'cycle': {},  # Cycle dictionary
        'longterm': {},  # Long-term dictionary
        'counter': {},  # Counter dictionary
        'note': [],  # Notes list
        'groups': {  # Organizational display structure
            'daily': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'optional': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'todo': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'cycle': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'longterm': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'counter': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}},
            'note': {
                '_Default': {'display_name': None, 'manual_order': [], 'sort_override': None, 'expanded': True,
                             'items': []}}, },
        'groups_display': {
            'daily': [],
            'optional': [],
            'todo': [],
            'cycle': [],
            'longterm': [],
            'counter': [],
            'note': [], },
        'history': {  # Completed objectives
            'daily': {},
            'optional': {},
            'todo': {},
            'cycle': {},
            'longterm': {},
            'counter': {}},
        # Stats/settings
        'stats': {
            'total_completed': 0,  # Total completed dailies integer
            'days_completed': 0,
            'streak': 0,  # Current streak integer
            'best_streak': 0, },  # Best streak integer
        'settings': {
            'calendar_date': {'month': 1, 'day': 1, 'year': 2022, 'week_day': 1},
            'date_switch': False,  # Switch MM/DD to DD/MM
            'welcome': True,  # Toggle welcome messages
            'display_total': True,  # Always display total completed dailies in header
            'daily': True,  # Always display dailies
            'daily_sort': 'completion_then_alpha_sort',
            'optional': True,  # Always display optionals
            'optional_sort': 'completion_then_alpha_sort',
            'todo': True,  # Always display todos
            'todo_sort': 'todo_sort',
            'cycle': True,  # Always display cycles
            'cycle_sort': 'cycle_sort',
            'cycle_preview': 7,  # Amount of days to preview
            'longterm': True,  # Always display long-terms
            'longterm_sort': 'completion_then_alpha_sort',
            'counter': True,  # Always display counters
            'counter_sort': 'alpha_sort',
            'note': True,  # Always display notes
            'note_sort': None,
            'auto_match': False,  # Automatically match first objective when searching
            'history_auto_match': False,  # auto_match but for history interface
            'single_line_tag_input': False,  # Switch between multi-line and single-line tag input
            'show_history_link': True,  # Toggle objectives always showing their History item link
            'history_keys_per_page': 5,  # History items to display per page
            'tags_keys_per_page': 5,  # Tags to display per page
            'end_day_warning': True}  # Warning when ending day if dailies are not all completed?
    }
    return template_dict


def load_data():
    if os.path.isfile('data.json'):
        with open('data.json', 'r') as data_json:
            try:
                database = json.load(data_json)
            except json.JSONDecodeError:
                print('data.json could not be read. Attempting to use backup')
                database = load_backup()  # Either gets data or aborts program if failed
    else:  # If data.json doesn't exist, create new one
        database = get_template_dict()
        database['welcome_message'] = welcome_messages.get_welcome()  # First-time-user welcome text
        save(database)
    return database


def load_backup():
    with open('data_autobackup.json', 'r') as autobackup:
        try:
            database = json.load(autobackup)
            return database
        except json.JSONDecodeError:
            print('Backup read failed. Please contact developer or manually investigate json files.')
            print('Please abort program. Delete data file to reset (likely unnecessary).')
            input('Press enter to close . . .')  # To pause before exiting
            quit()


def save(database, file_name='data.json'):  # By default, write to primary json file
    with open(file_name, 'w') as file:
        json.dump(database, file, indent=4)
