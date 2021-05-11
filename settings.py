import date_logic
import file_management


def set_week_day(database, input_week_day):
    week_day_number = date_logic.convert_day(input_week_day)  # Convert day to day #

    database['streak'] = 0
    database['cycle_objectives'].clear()
    database['active_cycle_objectives'].clear()

    database['week_day'] = week_day_number


def set_date(database, input_month, input_day):
    database['streak'] = 0
    database['cycle_objectives'].clear()
    database['active_cycle_objectives'].clear()

    database['calendar_date'][0] = input_month
    database['calendar_date'][0] = input_day


def toggle(toggle_item, toggle_value):
    # toggle_item is a string of which switch to change
    # toggle_value is the current value of that switch
    if toggle_value:  # If it's set to True
        print(toggle_item, "turned OFF")
        return False  # Set it to False
    else:  # It's currently False
        print(toggle_item, "turned ON")
        return True  # Set it to True
