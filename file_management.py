import os  # To check if json file exists yet
import json  # For dumping/loading database

import console_display
import welcome_messages


def get_template_dict():  # Database structure
    template_dict = {
        # Welcome
        'welcome_message': None,
        # Main data
        'daily': {},  # Dailies dictionary
        'optional': {},  # Optional dailies dictionary
        'todo': {},  # To-do dictionary
        'cycle': {},  # Cycle dictionary
        'longterm': {},  # Long-term dictionary
        'counter': {},  # Counter dictionary
        'note': [],  # Notes list
        'containers': {  # Organizational display structure
            'daily': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'optional': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'todo': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'cycle': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'longterm': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'counter': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}},
            'note': {
                '_default': {'display_name': None, 'expanded': True, 'items': []}}, },
        'history': {  # Completed objectives
            'daily': {},
            'optional': {},
            'todo': {},
            'cycle': {},
            'longterm': {}, },
        # Stats/settings
        'stats': {
            'total_completed': 0,  # Total completed dailies integer
            'days_completed': 0,
            'streak': 0,  # Current streak integer
            'best_streak': 0, },  # Best streak integer
        'settings': {
            'calendar_date': {'month': 1, 'day': 1, 'week_day': 1},
            'date_switch': False,  # Switch MM/DD to DD/MM
            'welcome': True,  # Toggle welcome messages
            'display_total': True,  # Always display total completed dailies in header
            'daily': True,  # Always display dailies
            'optional': True,  # Always display optionals
            'todo': True,  # Always display todos
            'cycle': True,  # Always display cycles
            'full_cycle': False,  # Always display active AND inactive cycles
            'longterm': True,  # Always display long-terms
            'counter': True,  # Always display counters
            'note': True,  # Always display notes
            'auto_match': False,  # Automatically match first objective when searching
            'track_history': True, }  # Tracks completed objectives
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
        update(database)
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


def update(database, file_name='data.json'):  # By default, write to primary json file
    with open(file_name, 'w') as file:
        json.dump(database, file, indent=4)
