import random
import os
import date_logic
import core_dict_logic
import file_modification

version_number = 0.8


def print_display(line_data):
    os.system('cls')
    settings = line_data['settings']
    stats = line_data['stats']

    # Print top header/welcome message
    print(f"[Daily] ('help' for commands) (v{version_number})")
    if settings['welcome_toggle']:
        if line_data['welcome_message'] is None:  # If no welcome has been set before (used to prevent dupe roll)
            line_data['welcome_message'] = (get_welcome(),)  # Make it a tuple for literal_eval
            file_modification.update(line_data)
        print(line_data['welcome_message'][0])
    print()  # Extra newline

    # Print date: - 01/01 Sunday -
    calendar_date = line_data['calendar_date']  # Date dictionary
    month_text = date_logic.format_month_text(calendar_date['month'])
    day_text = date_logic.format_day_text(calendar_date['day'])
    week_day_text = date_logic.convert_day_number(calendar_date['week_day'])
    if not settings['date_switch']:
        print(f"- {month_text}/{day_text} {week_day_text} -")
    else:
        print(f"- {day_text}/{month_text} {week_day_text} -")
    print()  # Extra newline

    # Streak/total header: Streak: 0
    print(f"Streak: {stats['streak']}")
    if settings['total_toggle']:
        print('Total dailies completed:', stats['total_completed'])
    print(end='\n\n')  # Extra newlines

    display_list = core_dict_logic.get_display_list(line_data)
    for dict_name in display_list:
        print_dictionary(line_data, dict_name)
        print()  # Extra newline


def print_dictionary(line_data, dict_name):
    if dict_name == 'daily':
        daily_dict = line_data['daily_objectives']
        if daily_dict: # Skip if empty
            print('>>> Daily objectives:', end='\n\n')
            print_base_dictionary(daily_dict)
            print()  # Extra newline
            print('(Optional)', end='\n\n')
            print_base_dictionary(line_data['optional_objectives'])
    elif dict_name == 'todo':
        todo_dict = line_data['todo_objectives']
        if todo_dict:  # Skip if empty
            print('>>> To-dos:', end='\n\n')
            print_base_dictionary(todo_dict)
    elif dict_name == 'cycle':
        active_cycle_list = core_dict_logic.get_active_cycle_list(line_data)
        if active_cycle_list:  # Skip if empty
            print('>>> Active cycles', end='\n\n')
            print_active_cycle_objectives(line_data, active_cycle_list)
        if line_data['settings']['full_cycle_toggle']:
            print()  # Extra newline
            print('(Inactive cycles)')
            print_inactive_cycle_objectives(line_data)
    elif dict_name == 'longterm':
        print('>>> Long-term goals:', end='\n\n')
        print_base_dictionary(line_data['longterm_objectives'])
    elif dict_name == 'counter':
        print('>>> Counters:', end='\n\n')
        print_counters(line_data)
    return


def print_base_dictionary(dictionary):
    for key, value in dictionary.items():
        # Expects [task_string, progress_denominator, progress numerator]
        task_string = value[0]
        denominator = value[1]
        numerator = value[2]
        if numerator >= denominator:  # Complete
            print(f'[x] {key} ({task_string}): {numerator}/{denominator} ', end='')
            print('({:.2%}) (DONE!!)'.format(numerator / denominator))
        else:  # Incomplete
            print(f'[ ] {key} ({task_string}): {numerator}/{denominator} ', end='')
            print('({:.2%})'.format(numerator / denominator))


def print_active_cycle_objectives(line_data, active_cycle_list):
    active_cycles = {}
    for objective in active_cycle_list:
        active_cycles.update({objective: line_data['cycle_objectives'][objective]})
    for key, value in active_cycles.items():
        # [task_string, progress_denominator, progress numerator, cycle length, current offset]
        task = value[0]
        denominator = value[1]
        numerator = value[2]
        length = value[3]
        percent = numerator/denominator
        if numerator >= denominator:  # Complete
            print(f'[x] {key} ({task}) (every {length}d): {numerator}/{denominator} (DONE!!)', end='')
            print('({:.2%})'.format(percent))
        else:  # Incomplete
            print(f'[ ] {key} ({task}) (every {length}d): {numerator}/{denominator} ', end='')
            print('({:.2%})'.format(percent))


def print_inactive_cycle_objectives(line_data):
    # [task_string, progress_denominator, progress numerator, cycle length, current offset]
    for key, value in line_data['cycle_objectives'].items():
        if value[4] == 0:  # Skip actives
            continue
        print(f'{key} ({value[0]}): Every {value[3]}d, next in {value[4]}d')


def print_counters(line_data):
    for key, value in line_data['counter_dict'].items():
        # value = [task_string, number]
        print(f'{key} ({value[0]}): {value[1]}')


def print_stats(line_data):
    print(f"Total completed daily goals: {line_data['total_completed']}\n"
          f"Days completed: {line_data['days_completed']}\n"
          f"Current streak: {line_data['streak']}\n"
          f"Best streak: {line_data['best_streak']}")


def print_settings(line_data):
    print(f"Print DD/MM: {line_data['date_switch']}\n"
          f"Print welcome: {line_data['welcome_toggle']}\n"
          f"Show total completed dailies on startup: {line_data['total_toggle']}\n"
          f"Always show dailies: {line_data['daily_toggle']}\n"
          f"Always show todos: {line_data['todo_toggle']}\n"
          f"Always show active cycles: {line_data['cycle_toggle']}\n"
          f"Always show all cycles: {line_data['full_cycle_toggle']}\n"
          f"Always show longterms: {line_data['longterm_toggle']}\n"
          f"Always show counters: {line_data['counter_toggle']}\n"
          f"Auto-match closest objective when given not found: {line_data['auto_match_toggle']}")



    print('Print MM/DD:', not line_data['date_switch'])
    print('Welcome message:', line_data['welcome_toggle'])
    print('Always show total:', line_data['total_toggle'])
    print('Always show long-terms:', line_data['longterm_toggle'])


def get_welcome():
    welcome_messages = [
        "WELCOME! HOW IS YOUR DAY GOING?",
        "EAT YOUR FRUITS AND VEGGIES!!",
        "STAY HYDRATED!!!!",
        "THESE WERE NOT TYPED WITH CAPS LOCK, I HOLD LEFT SHIFT",
        "POSTURE CHECK!",
        "WHY DO PEOPLE SAY VIOLETS ARE BLUE? THEY'RE VIOLET! GOOGLE IT IF YOU DON'T KNOW!!!",
        "I FEEL LIKE I SHOULD HAVE BEEN TRACKING THE DEVELOPMENT OF THIS ON GITHUB LOL. HMM..",
        "THE ORIGINAL WELCOME MESSAGES FELT TOO CHEESY TO ME, SO I REPLACED THEM WITH RAMBLINGS",
        "DO YOU LIKE FRENCH TOAST? WHAT ABOUT CREPES? BELGIAN WAFFLES? I CALLED THOSE 'BELGIUM WAFFLES' FOR A WHILE.",
        "HOW DO YOU FEEL ABOUT COMPETITIVE PROGRAMMING?",
        "HOW'S THE WEATHER?",
        "CHOCOLATE OR VANILLA ICE CREAM? I LIKE VANILLA-CHOCOLATE SWIRLED SOFT-SERVED!!",
        "HAVE YOU EVER MADE YOUR OWN DISCORD BOT? GOT ANY IDEAS?",
        "IF YOU USE THIS TO ACHIEVE GOOD, PRODUCTIVE GOALS, I SALUTE YOU AND AM PROUD!",
        "TRY TO SPEND AT LEAST A GOOD 3 HOURS ON CHALLENGING EXERCISE PER WEEK!",
        "HAVE YOU MADE YOUR OWN GAME BEFORE? GOT ANY IDEAS?",
        "SETTING REGULAR GOALS IS A GREAT WAY TO ENCOURAGE CONSISTENCY!",
        "DO YOU LIKE READING BOOKS? IF SO; ANY BOOKS YOU'RE LOOKING FORWARD TO RIGHT NOW?",
        "KEEP YOUR EQUIPMENT CLEAN!",
        "MAKE SURE YOU GET ENOUGH SLEEP!",
        "I CHALLENGE YOU TO SPECIFICALLY TRY ENCOURAGING SOMEBODY TODAY!!",
        "DON'T PROCRASTINATE!",
        "QUICK! WHAT'S 13 SQUARED?",
        "ANY LANGUAGES YOU WANT TO LEARN/PROGRESS WITH; PROGRAMMING OR OTHERWISE? IF SO, HOW'S THAT GOING?",
        "ANY MUSICAL INSTRUMENTS YOU WANT TO LEARN/PROGRESS WITH? IF SO, HOW'S THAT GOING?",
        "QUICK! WHAT'S 27 * 12 WITHOUT USING A CALCULATOR?",
        "OKAY, SORRY, WRITING THESE WELCOME MESSAGES IS A LOT HARDER THAN I ANTICIPATED. HERE; YOU THINK OF ONE! "
        "CREATIVE EXERCISE!",
        "HAVE ANY GOOD PLANS AFTER FINISHING YOUR GOALS TODAY? IF SO, USE THAT AS MOTIVATION TO FINISH THEM FIRST!",
        "WELCOME! HAVE A GOOD DAY!",
        "WELCOME!!!!!",
        "WELCOME!",
        "ANYONE YOU'VE BEEN MEANING TO TALK TO?",
        "QUICK! WHAT'S THE 13TH LETTER OF THE ALPHABET?",
        "GREETINGS!",
        "BONJOUR!",
        "HI!!!",
        "WHY HELLO THERE!",
        "HOLA!",
        "PLAY ANY GAMES LATELY? IF SO, WHAT'S BEEN YOUR FAVORITE?",
        "ALOHA!",
    ]
    return random.choice(welcome_messages)
