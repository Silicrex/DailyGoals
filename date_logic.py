def valid_date(month, day, year):
    # Given month 1-12, day 1-31
    if month in {1, 3, 5, 7, 8, 10, 12}:  # 31 days
        return True  # We already know day is in the range [1, 31]
    elif month in {4, 6, 9, 11}:  # 30 days
        if day <= 30:
            return True
    elif month == 2:  # 28/29 days based on leap year
        if day <= 28:
            return True
        elif day == 29:
            return check_leap_year(year)  # 29 only valid in Feb for leap years
        else:
            return False


def increment_date(database):
    day = database['settings']['calendar_date']['day']
    month = database['settings']['calendar_date']['month']
    year = database['settings']['calendar_date']['year']
    if day < 28:
        day += 1
    # Else, month matters
    elif month in {1, 3, 5, 7, 8, 10, 12}:  # 31 days
        if day < 31:
            day += 1
        elif month == 12:  # Day is 31, meaning month/year changes. Is it December?
            month = 1  # It's December 31st, reset date to Jan 1st
            day = 1
            year += 1
        else:
            month += 1  # Not December, just increase month by 1 and reset day
            day = 1
    elif month in {4, 6, 9, 11}:  # 30 days
        if day < 30:
            day += 1
        else:  # Day is 30
            month += 1
            day = 1
    else:  # month == 2
        if day < 28:
            day += 1
        elif day == 28 and check_leap_year(year):  # Day is 28 on a leap year
            day += 1
        else:  # It was either the 28th on a non-leap-year or it was the 29th on a leap year
            month += 1
            day = 1
    database['settings']['calendar_date']['day'] = day
    database['settings']['calendar_date']['month'] = month
    database['settings']['calendar_date']['year'] = year


def check_leap_year(year):
    leap_year = False
    if year % 4 == 0:
        if year % 100 == 0:
            leap_year = True if year % 400 == 0 else False
        else:
            leap_year = True
    return leap_year


def next_week_day(week_day):
    if week_day < 7:
        return week_day + 1
    else:  # It's 7
        return 1


def get_week_days():
    week_days = {'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'}
    return week_days


def convert_day_number(day_number):
    if day_number == 1:
        return 'Sunday'
    elif day_number == 2:
        return 'Monday'
    elif day_number == 3:
        return 'Tuesday'
    elif day_number == 4:
        return 'Wednesday'
    elif day_number == 5:
        return 'Thursday'
    elif day_number == 6:
        return 'Friday'
    elif day_number == 7:
        return 'Saturday'


def convert_day(day):
    if day in {'sunday', 'su', 'sun', 'sund', 'sunda'}:
        return 1
    elif day in {'monday', 'm', 'mo', 'mon', 'mond', 'monda'}:
        return 2
    elif day in {'tuesday', 'tu', 'tu', 'tue', 'tues', 'tuesd', 'tuesda'}:
        return 3
    elif day in {'wednesday', 'w', 'we', 'wed', 'wedn', 'wedne', 'wednes', 'wednesd', 'wednesda'}:
        return 4
    elif day in {'thursday', 'th', 'thu', 'thur', 'thurs', 'thursd', 'thursda'}:
        return 5
    elif day in {'friday', 'f', 'fr', 'fri', 'frid', 'frida'}:
        return 6
    elif day in {'saturday', 'sa', 'sat', 'satu', 'satur', 'saturd', 'saturda'}:
        return 7
    else:
        return False


def string_date(database, string):
    # String should be YYYY-MM-DD
    months = ['', 'January', 'February', 'March', 'April', 'May', 'June',  # Blank to line up 1 = January
              'July', 'August', 'September', 'October', 'November', 'December']  # Or just import calendar
    date = string.split('-')
    if database['settings']['date_switch']:
        date[1], date[2] = date[2], date[1]

    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    str_day = str(day)

    if str_day in {'1', '21', '31'}:
        suffix = 'st'
    elif str_day in {'2', '22'}:
        suffix = 'nd'
    elif str_day in {'3', '23'}:
        suffix = 'rd'
    else:
        suffix = 'th'

    return f'{months[month]} {day}{suffix}, {year}'
