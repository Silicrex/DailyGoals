import date_logic
import file_management


def set_week_day(line_data, input_week_day):
    week_day_number = date_logic.convert_day(input_week_day)  # Convert day to day #

    line_data['streak'] = 0
    line_data['cycle_objectives'].clear()
    line_data['active_cycle_objectives'].clear()

    line_data['week_day'] = week_day_number


def set_date(line_data, input_month, input_day):
    line_data['streak'] = 0
    line_data['cycle_objectives'].clear()
    line_data['active_cycle_objectives'].clear()

    line_data['calendar_date'][0] = input_month
    line_data['calendar_date'][0] = input_day


def toggle(toggle_item, toggle_value):
    # toggle_item is a string of which switch to change
    # toggle_value is the current value of that switch
    if toggle_value:  # If it's set to True
        print(toggle_item, "turned OFF")
        return False  # Set it to False
    else:  # It's currently False
        print(toggle_item, "turned ON")
        return True  # Set it to True
