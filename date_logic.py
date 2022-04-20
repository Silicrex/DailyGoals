import console_display  # For confirm()


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


def convert_day_number(week_day):
    if week_day == 1:
        return 'Sunday'
    elif week_day == 2:
        return 'Monday'
    elif week_day == 3:
        return 'Tuesday'
    elif week_day == 4:
        return 'Wednesday'
    elif week_day == 5:
        return 'Thursday'
    elif week_day == 6:
        return 'Friday'
    elif week_day == 7:
        return 'Saturday'


def convert_day(day):
    if day == 'sunday':
        return 1
    elif day == 'monday':
        return 2
    elif day == 'tuesday':
        return 3
    elif day == 'wednesday':
        return 4
    elif day == 'thursday':
        return 5
    elif day == 'friday':
        return 6
    elif day == 'saturday':
        return 7
