"""
An App to Run every day, and then to see which dailies occured, and based on that punish the user.
"""
import logging
from datetime import datetime, timedelta, timezone
import re
import azure.functions as func
import toggl_punish_utils.habitica as habitica
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.punish as punish
import toggl_punish_utils.toggl as toggl


app = func.FunctionApp()


# 8:30 AM = 0830 in UTC = 0300
@app.schedule(
    schedule="0 0 3 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True
)

def timer_trigger(myTimer: func.TimerRequest) -> None:
    """
    The trigger which runs every day at 8:30am(ist)
    """

    ru.run_request(habitica.run_cron)


    COIN_COST_PER_DAILY = 8
    PUNISH_COST_PER_DAILY = 60

    logging.info("Daily/Cron Triggered")

    max_coin_cost = ru.run_request(habitica.get_coins)
    cron_history = ru.run_request(habitica.get_cron_history)

    last_cron = toggl.from_toggl_format(cron_history[-1]["date"])
    last_last_cron = toggl.from_toggl_format(cron_history[-2]["date"])

    adjusted_last_cron = last_cron + timedelta(minutes=1) # The reason we do this, is because if a daily was missed, it will be marked not done slightly after cron was run.
    adjusted_last_last_cron = last_last_cron + timedelta(minutes=1)

    logging.info("Adjusted Time Period For Dailies: [%s - %s]", adjusted_last_last_cron, adjusted_last_cron)

    dailies = ru.run_request(habitica.get_dailies)["data"]
    
    coin_cost, punish_cost = 0, 0

    # cur_datetime = toggl.get_now()
    # cur_date = cur_datetime.date()
    # logging.info("Cur datetime: %s", cur_datetime)
    for daily in dailies:

        logging.info(
            "Name: %s, History: %s, Streak: %d",
            daily["text"],
            daily["history"],
            daily["streak"],
        )

        if "(skip)" in daily["text"].casefold():
            continue

        if "(temp)" in daily["text"].casefold():
            new_text = re.sub(r"\(temp\)", "", daily["text"], re.IGNORECASE)
            ru.run_request(habitica.set_task_text, daily["id"], new_text)
            continue 

        history = daily["history"]


        for record in history[::-1]:
            rec_date = datetime.fromtimestamp(record["date"]/1000, timezone.utc)
            if rec_date <= adjusted_last_cron and rec_date >= adjusted_last_last_cron:
                if record["isDue"] and not record["completed"]:
                    logging.info("Incomplete Daily: %s", daily["text"])
                    coin_cost += COIN_COST_PER_DAILY
                    punish_cost += PUNISH_COST_PER_DAILY
            
                break

        # creation_datetime = toggl.to_local(toggl.from_toggl_format(daily["createdAt"]))
        # creation_date = creation_datetime.date()
        
        # logging.info("Creation date: %s", creation_datetime)
        # streak_before_today = (
        #     daily["streak"] - 1 if daily["completed"] else daily["streak"]
        # )
        # logging.info("streak_before_today: %s", streak_before_today)

        # if streak_before_today == 0 and cur_date != creation_date:
        #     coin_cost += COIN_COST_PER_DAILY
        #     punish_cost += PUNISH_COST_PER_DAILY
        logging.info("Coin Cost: %d, Punish Cost: %d", coin_cost, punish_cost)

    coin_cost = min(coin_cost, max_coin_cost)
    habitica.remove_coins(coin_cost)
    #ru.run_request(habitica.sync_stats())
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
