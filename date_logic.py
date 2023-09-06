from database import DB


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


def increment_date():  # Takes and mutates a calendar_date dict
    calendar_date = DB['settings']['calendar_date']
    day = calendar_date['day']
    month = calendar_date['month']
    year = calendar_date['year']
    week_day = calendar_date['week_day']
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
    if week_day < 7:
        week_day += 1
    else:  # It's 7
        week_day = 1
    calendar_date['day'] = day
    calendar_date['month'] = month
    calendar_date['year'] = year
    calendar_date['week_day'] = week_day


def check_leap_year(year):
    leap_year = False
    if year % 4 == 0:
        if year % 100 == 0:
            leap_year = True if year % 400 == 0 else False
        else:
            leap_year = True
    return leap_year


def get_week_days():
    week_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    return week_days


def get_week_day_abbreviation(num):
    abbreviations = ['', 'Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa']  # Blank string to offset, since Sunday = 1
    return abbreviations[num]


def convert_day_number(day_number_input):
    if day_number_input not in range(1, 8):  # Must be 1-7
        return False
    days = [x.capitalize() for x in get_week_days()]
    return days[day_number_input - 1]  # Adjust for offset (Sunday starts at 1, index starts at 0)


def convert_month_number(month_number_input):
    if month_number_input not in range(1, 13):  # Must be 1-7
        return False
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    return months[month_number_input - 1]  # Adjust for offset (January starts at 1, index starts at 0)


def convert_day(day_input):
    if not day_input or day_input in {'t', 's'}:  # 't' and 's' could be mixed between tues/thurs, sat/sun
        return False
    week_days = get_week_days()
    for index, day in enumerate(week_days):
        if day.startswith(day_input):
            return index + 1  # Sunday starts at 1, enumerate() starts at 0
    return False


def string_date(calendar_date):
    # date = dict with year, month, day, week_day
    year = calendar_date['year']
    month = calendar_date['month']
    day = calendar_date['day']
    week_day = convert_day_number(calendar_date['week_day'])
    if day in {1, 21, 31}:
        suffix = 'st'
    elif day in {2, 22}:
        suffix = 'nd'
    elif day in {3, 23}:
        suffix = 'rd'
    else:
        suffix = 'th'

    return f"{week_day}, {convert_month_number(month)} {day}{suffix}, {year}"
    # return (f"{calendar_date['year']}-{calendar_date['month']:02d}-{calendar_date['day']:02d}, "
    #        f"{convert_day_number(calendar_date['week_day'])}")
    # return f'{months[month]} {day}{suffix}, {year}'
