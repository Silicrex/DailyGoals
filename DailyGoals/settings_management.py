def toggle(database, toggle_item, manual_value=None):
    def enable_item():
        settings[toggle_item] = True
        print(f'[{toggle_item}] enabled', end='\n\n')

    def disable_item():
        settings[toggle_item] = False
        print(f'[{toggle_item}] disabled', end='\n\n')

    settings = database['settings']
    if manual_value is None:  # No manual value (on/off) specified, so just invert
        if settings[toggle_item]:  # If it's on, turn it off
            disable_item()
        else:  # If it's off, turn it on
            enable_item()
    else:  # On/off was specified
        if manual_value == 'on':
            if settings[toggle_item]:  # If it's on already
                print(f'[{toggle_item}] is already enabled', end='\n\n')
            else:  # It's not on, so turn it on
                enable_item()
        elif manual_value == 'off':
            if not settings[toggle_item]:  # If it's disabled already
                print(f'[{toggle_item}] is already disabled', end='\n\n')
            else:  # It's not off, so turn it off
                disable_item()


def force_date_change_prompt(database):  # If week day or date is changed, need to clear streak/cycles
    while True:
        print('WARNING: Resets streak and *DELETES* ALL CYCLE OBJECTIVES. Proceed? (y/n)')
        user_input = input().lower()
        if user_input == 'y':
            database['streak'] = 0
            database['cycle'].clear()
            return True
        elif user_input == 'n':
            return False
