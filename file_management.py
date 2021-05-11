import ast
import os
import json
import core_dict_logic
import welcome_messages


def load_data():
    if os.path.isfile('data.json'):
        try:
            with open('data.json', 'r') as data_json:
                line_data = json.load(data_json)
        except ValueError:
            print('wat')
    else:
        line_data = core_dict_logic.get_template_dict()
        line_data['welcome_message'] = welcome_messages.get_welcome()

    return line_data


def update(line_data):
    with open('daily.dat', 'w') as daily_dat:  # Writes line_data to file
        for key, value in line_data.items():
            daily_dat.write(f'{str(value)}\n')


def back_up(line_data, file):  # merge with update, give update default file
    for key in line_data:
        file.write(f'{str(line_data[key])}\n')

