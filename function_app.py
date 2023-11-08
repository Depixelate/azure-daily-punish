import logging
import azure.functions as func
import toggl_punish_utils.habitica as habitica
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.punish as punish
import toggl_punish_utils.toggl as toggl

app = func.FunctionApp()


@app.schedule(
    schedule="0 1 6 * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    COIN_COST_PER_DAILY = 8
    PUNISH_COST_PER_DAILY = 60
    logging.info("Daily/Cron Triggered")
    max_coin_cost = ru.run_request(habitica.get_coins)
    dailies = ru.run_request(habitica.get_dailies)["data"]

    coin_cost, punish_cost = 0, 0
    cur_date = toggl.get_now()
    logging.info("Cur date: %s", cur_date)
    for daily in dailies:
        creation_date = toggl.to_local(toggl.from_toggl_format(daily["createdAt"]))
        logging.info(
            "Name: %s, Completed: %s, Streak: %d",
            daily["text"],
            daily["completed"],
            daily["streak"],
        )
        logging.info("Creation date: %s", creation_date)
        streak_before_today = (
            daily["streak"] - 1 if daily["completed"] else daily["streak"]
        )
        logging.info("streak_before_today: %s", streak_before_today)
        if streak_before_today == 0 and cur_date.day != creation_date.day:
            coin_cost += COIN_COST_PER_DAILY
            punish_cost += PUNISH_COST_PER_DAILY
        logging.info("Coin Cost: %d, Punish Cost: %d", coin_cost, punish_cost)

    coin_cost = min(coin_cost, max_coin_cost)
    habitica.remove_coins(coin_cost)
    initial_punish_val = punish.get_last_count()
    final_punish_val = initial_punish_val + punish_cost
    logging.info("Initial Punish Val: %d, Final Punish Val: %d", initial_punish_val, final_punish_val)
    punish.update_punish_val(punish.get_last_count() + punish_cost)
    # LIAS = "togglHabiticaPunishDaily"A


#  if myTimer.past_due:
#         logging.info('The timer is past due!')

#     logging.info('Python timer trigger function executed.')
