import os  # To check if json file exists yet
import json  # For dumping/loading database
import welcome_messages


def get_template_dict():  # Database structure
    template_dict = {
        # Date/today stuff
        'calendar_date': {'month': 1, 'day': 1, 'week_day': 1},
        'week_day': 1,  # Day of the week 1-7
        'welcome_message': None,
        # Dictionaries
        'daily_objectives': {},  # Dailies dictionary
        'optional_objectives': {},  # Optional dailies dictionary
        'todo_objectives': {},  # To-do dictionary
        'cycle_objectives': {},  # Cycle dictionary
        'longterm_objectives': {},  # Long-term dictionary
        'counter_dict': {},  # Counter dictionary
        'history_dict': {},  # Completed objectives
        'stats': {
            'total_completed': 0,  # Total completed dailies integer
            'days_completed': 0,
            'streak': 0,  # Current streak integer
            'best_streak': 0, },  # Best streak integer
        'settings': {
            'date_switch': False,  # Switch MM/DD to DD/MM
            'welcome_toggle': True,  # Toggle welcome messages
            'total_toggle': True,  # Always display total completed dailies
            'daily_toggle': True,  # Always display dailies
            'todo_toggle': True,  # Always display todos
            'cycle_toggle': True,  # Always display active cycles
            'full_cycle_toggle': False,  # Always display active AND inactive cycles
            'longterm_toggle': True,  # Always display long-terms
            'counter_toggle': False,  # Always display counters
            'auto_match_toggle': False,  # Automatically match first objective when searching
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
                database = load_backup()  # Either gets data or aborts if failed
    else:  # If data.json doesn't exist, create new one
        database = get_template_dict()
        database['welcome_message'] = welcome_messages.get_welcome()  # Used to persist a welcome msg per day
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
            exit()


def update(database, file_name='data.json'):  # By default, write to primary json file
    with open(file_name, 'w') as file:
        json.dump(database, file, indent=4)
