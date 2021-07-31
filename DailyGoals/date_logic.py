def valid_date(month, day):
    # Given month 1-12, day 1-31
    if month in {1, 3, 5, 7, 8, 10, 12}:  # 31
        return True  # We already know day is in the range [1, 31]
    elif month in {4, 6, 9, 11}:  # 30
        if day < 31:
            return True
    elif month == 2:  # 28/29
        if day < 30:
            return True
    return False


def next_day(month, day):
    if day < 28:
        day += 1
    # Else, month matters
    elif month in {1, 3, 5, 7, 8, 10, 12}:  # 31 days
        if day < 31:
            day += 1
        elif month == 12:  # Day is 31, meaning month changes. Is it December?
            month = 1  # It's December 31st, reset date to Jan 1st
            day = 1
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
        elif day == 28:  # Day is 28
            while True:
                print('Is it a leap year (is tomorrow the 29th)? (y/n)')
                user_response = input().lower()
                if user_response in {'yes', 'y', 'no', 'n'}:
                    break
            if user_response in {'yes', 'y'}:
                day += 1
            else:  # Not a leap year, so set to March 1st
                month = 3
                day = 1
        else:  # It was a leap year and it was the 29th
            month = 3
            day = 1
    return month, day


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


def format_month_text(month_number):  # Takes number input
    if month_number < 10:  # If it's single-digit, add a leading 0
        return '0' + str(month_number)
    else:
        return str(month_number)


def format_day_text(day_number):  # Takes number input
    if day_number < 10:  # If it's single-digit, add a leading 0
        return '0' + str(day_number)
    else:
        return str(day_number)
