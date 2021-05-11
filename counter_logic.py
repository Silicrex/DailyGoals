import core_dict_logic


def add_counter_item(counter_dict, objective_name):
    if objective_name in counter_dict:
        print('Objective exists already')
        return False

    if not (task_string := core_dict_logic.get_task()):  # Enter blank string = cancel
        return False

    counter_dict.update({objective_name: [task_string, 0]})  # 0 is the counter

    print(f"Added '{objective_name}'")
    return True


def reset_counter_item(counter_dict, objective_name):
    if counter_dict[objective_name][1] != 0:
        counter_dict[objective_name][1] = 0
    else:
        print('That counter is already at 0')
        return False
    return True


def update_counter_item(counter_dict, objective_name, add_value):
    add_value = eval(add_value)
    counter_dict[objective_name][1] += add_value  # Add to numerator
    return True
