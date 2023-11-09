"""
An App to Run every day, and then to see which dailies occured, and based on that punish the user.
"""
import logging
import azure.functions as func
import toggl_punish_utils.habitica as habitica
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.punish as punish
import toggl_punish_utils.toggl as toggl

app = func.FunctionApp()


# 6:01 AM = 0601 in UTC = 0031
@app.schedule(
    schedule="0 31 0 * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    """
    The trigger which runs every day at 6:01am(ist)
    """
    COIN_COST_PER_DAILY = 8
    PUNISH_COST_PER_DAILY = 60

    logging.info("Daily/Cron Triggered")
    max_coin_cost = ru.run_request(habitica.get_coins)
    dailies = ru.run_request(habitica.get_dailies)["data"]

    coin_cost, punish_cost = 0, 0
    cur_datetime = toggl.get_now()
    cur_date = cur_datetime.date()
    logging.info("Cur datetime: %s", cur_datetime)
    for daily in dailies:
        creation_datetime = toggl.to_local(toggl.from_toggl_format(daily["createdAt"]))
        creation_date = creation_datetime.date()
        logging.info(
            "Name: %s, Completed: %s, Streak: %d",
            daily["text"],
            daily["completed"],
            daily["streak"],
        )
        logging.info("Creation date: %s", creation_datetime)
        streak_before_today = (
            daily["streak"] - 1 if daily["completed"] else daily["streak"]
        )
        logging.info("streak_before_today: %s", streak_before_today)

        if streak_before_today == 0 and cur_date != creation_date:
            coin_cost += COIN_COST_PER_DAILY
            punish_cost += PUNISH_COST_PER_DAILY
        logging.info("Coin Cost: %d, Punish Cost: %d", coin_cost, punish_cost)

    coin_cost = min(coin_cost, max_coin_cost)
    habitica.remove_coins(coin_cost)
    ru.run_request(habitica.sync_stats())
    initial_punish_val = punish.get_last_count()
    final_punish_val = punish.clamp_punish_val(initial_punish_val + punish_cost)
    logging.info(
        "Initial Punish Val: %d, Final Punish Val: %d",
        initial_punish_val,
        final_punish_val,
    )
    punish.update_punish_val(final_punish_val)
    # LIAS = "togglHabiticaPunishDaily"A


#  if myTimer.past_due:
#         logging.info('The timer is past due!')

#     logging.info('Python timer trigger function executed.')
