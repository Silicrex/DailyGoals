import console_display

def toggle(database, toggle_item, manual_value=None):
    def enable_item():
        settings[toggle_item] = True
        console_display.refresh_and_print(database, f'[{toggle_item}] enabled')

    def disable_item():
        settings[toggle_item] = False
        console_display.refresh_and_print(database, f'[{toggle_item}] disabled')

    settings = database['settings']
    if manual_value is None:  # No manual value (on/off) specified, so just invert
        if settings[toggle_item]:  # If it's on, turn it off
            disable_item()
        else:  # If it's off, turn it on
            enable_item()
    else:  # On/off was specified
        if manual_value == 'on':
            if settings[toggle_item]:  # If it's on already
                console_display.refresh_and_print(database, f'[{toggle_item}] is already enabled')
            else:  # It's not on, so turn it on
                enable_item()
        elif manual_value == 'off':
            if not settings[toggle_item]:  # If it's disabled already
                console_display.refresh_and_print(database, f'[{toggle_item}] is already disabled')
            else:  # It's not off, so turn it off
                disable_item()
