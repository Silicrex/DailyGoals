def command_flow(database, user_input):
    # elif command == 'endday':  # sadpofjd oifdS fgod FIX THIS
    #     if wrong_parameters(0):
    #         continue
    #     if daily_objectives:  # Skip all of this part if there are none
    #         all_complete = True
    #         for key, value in daily_objectives.items():
    #             # value = [task_string, denominator, numerator]
    #             objective_complete = value[2] >= value[1]  # numerator >= denominator
    #             if objective_complete:
    #                 total_completed += 1
    #             elif all_complete:  # If not set to False already
    #                 all_complete = False
    #             value[2] = 0  # Reset numerator to 0
    #         if all_complete:
    #             streak += 1
    #             if streak > best_streak:
    #                 best_streak = streak
    #         else:
    #             streak = 0
    #     if todo_objectives:
    #         remove_list = []
    #         for key, value in todo_objectives.items():
    #             # value = [task_string, denominator, numerator]
    #             objective_complete = value[2] >= value[1]  # numerator >= denominator
    #             if objective_complete:
    #                 remove_list.append(key)
    #         for key in remove_list:
    #             todo_objectives.pop(key)
    #
    #     calendar_date = date_logic.next_day(calendar_date)
    #     week_day = date_logic.next_week_day(week_day)
    #     update()
    #     print_display()