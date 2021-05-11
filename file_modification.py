import ast
import os
import core_dict_logic


def check_for_dat():
    if not os.path.isfile('daily.dat'):
        print('daily.dat not detected. Attempting to generate...')
        create_dat()
        print('daily.dat generated')


def create_dat():
    with open('daily.dat', 'w') as daily_dat:
        template_dict = core_dict_logic.get_template_dict()
        for key, value in template_dict.items():
            daily_dat.write(f'{value}\n')


def initialize_data():
    with open('daily.dat', 'r') as file:  # Get list of all lines
        lines_list = file.readlines()
    line_data = core_dict_logic.get_template_dict()  # Load template for structure
    lines = iter(lines_list)
    for key in line_data:  # Fill each value line-by-line
        line_data[key] = ast.literal_eval(next(lines))
    with open('daily_backup.dat', 'w') as daily_backup:
        back_up(line_data, daily_backup)
    return line_data


def update(line_data):
    with open('daily.dat', 'w') as daily_dat:  # Writes line_data to file
        for key, value in line_data.items():
            daily_dat.write(f'{str(value)}\n')


def back_up(line_data, file):
    for key in line_data:
        file.write(f'{str(line_data[key])}\n')

