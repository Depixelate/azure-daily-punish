"""
An App to Run every day, and then to see which dailies occured, and based on that punish the user.
"""
import logging
from datetime import time, datetime, timedelta, timezone
import re
import azure.functions as func
import toggl_punish_utils.habitica as habitica
import toggl_punish_utils.request_utils as ru
import toggl_punish_utils.punish as punish
import toggl_punish_utils.toggl as toggl



app = func.FunctionApp()


#6:30 AM = 0630 in UTC = 0100
# @app.schedule(
#     schedule="0 0 1 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True
# )
def timer_trigger(myTimer) -> None:
    """
    The trigger which runs every day at 6:30am(ist)
    """
    dailies = ru.run_request(habitica.get_dailies)["data"]

    for daily in dailies:
        if "(temp)" in daily["text"].casefold():
            new_text = re.sub(r"\(temp\)", "", daily["text"], re.IGNORECASE)
            ru.run_request(habitica.set_task_text, daily["id"], new_text)


    cron_history = ru.run_request(habitica.get_cron_history)
    last_cron_utc = toggl.from_toggl_format(cron_history[-1]["date"])
    last_cron_local = toggl.to_local(last_cron_utc)

    print("Last Cron Local Date Time: %s", last_cron_local)

    # if last_cron_local.date() == toggl.get_now().date():
    #     logging.info("Cron was already run today, skipping")
    #     return
    
        #if time(0, 0, 0) <= last_cron_local.time() <= time(1, 0, 0): #Cron was done by toggl punish, therefore user was in inn, skip this.
        #     logging.info("Cron was done by toggl punish, therefore user was in inn, skip this.")
        #     return
    
    ru.run_request(habitica.run_cron)

    if habitica.does_reward_exist(habitica.WAS_IN_INN_ALIAS): # The reason why we do this, where we have the timer manually bring us out of the inn, and then create a dummy reward to send a signal to the daily function not to calc. punish is because having the daily function bring us out, and not do punish, solely based on the fact that the player is in the inn means that the player can't choose to leave the inn until 6:30, which I don't want.
        logging.info("Player in inn, so not punishing, toggling in inn")
        ru.run_request(habitica.delete_reward, habitica.WAS_IN_INN_ALIAS)
        #ru.run_request(habitica.toggle_player_in_inn)
        return
    # if ru.run_request(habitica.is_player_in_inn):
    #     logging.info("Player in inn, so not punishing, toggling in inn")
    #     ru.run_request(habitica.run_cron)
    #     workspace_id = ru.run_request(toggl.get_default_workspace_id)
    #     ru.run_request(toggl.start_timer, toggl.get_now_utc(), "Back From Rest", workspace_id) # meant to immediately trigger an alarm.
    #     ru.run_request(habitica.toggle_player_in_inn)
    #     return

    COIN_COST_PER_DAILY = 8
    PUNISH_COST_PER_DAILY = 60

    logging.info("Daily/Cron Triggered")

    max_coin_cost = ru.run_request(habitica.get_coins)
    cron_history = ru.run_request(habitica.get_cron_history)

    last_cron_utc = toggl.from_toggl_format(cron_history[-1]["date"])
    last_last_cron_utc = toggl.from_toggl_format(cron_history[-2]["date"])

    adjusted_last_cron_utc = last_cron_utc + timedelta(minutes=1) # The reason we do this, is because if a daily was missed, it will be marked not done slightly after cron was run.
    adjusted_last_last_cron_utc = last_last_cron_utc + timedelta(minutes=1)

    logging.info("Adjusted Time Period For Dailies: [%s - %s]", adjusted_last_last_cron_utc, adjusted_last_cron_utc)

    
    
    coin_cost, punish_cost = 0, 0

    # cur_datetime = toggl.get_now()
    # cur_date = cur_datetime.date()
    # logging.info("Cur datetime: %s", cur_datetime)
    tags = []
    for daily in dailies:

        cur_daily_coin_cost = COIN_COST_PER_DAILY
        cur_daily_punish_cost = PUNISH_COST_PER_DAILY

        logging.info(
            "Name: %s, History: %s, Streak: %d",
            daily["text"],
            "History in debug",
            daily["streak"],
        )

        logging.debug("History: %s", daily["history"])


        if "(skip)" in daily["text"].casefold():
            continue 

        if res := re.findall(r"\(\s*count:\s*(\d+)\s*\)", daily["text"], re.IGNORECASE):
            cur_daily_coin_cost = int(res[0])
            cur_daily_punish_cost = int(cur_daily_coin_cost * 7.5)


        history = daily["history"]

        for record in history[::-1]:
            rec_date_utc = datetime.fromtimestamp(record["date"]/1000, timezone.utc)
            if adjusted_last_last_cron_utc <= rec_date_utc <= adjusted_last_cron_utc:
                if record["isDue"] and not record["completed"]:
                    logging.info("Incomplete Daily: %s", daily["text"])
                    tags.append(daily["text"])
                    coin_cost += cur_daily_coin_cost
                    punish_cost += cur_daily_punish_cost
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
    initial_punish_val = punish.get_last_count()
    final_punish_val = punish.clamp_punish_val(initial_punish_val, initial_punish_val + punish_cost)
    logging.info(
        "Initial Punish Val: %d, Final Punish Val: %d",
        initial_punish_val,
        final_punish_val,
    )
    punish.update_punish_val(final_punish_val, tags)
    # LIAS = "togglHabiticaPunishDaily"A
#timer_trigger()

if __name__ == "__main__":
    timer_trigger(None)

#  if myTimer.past_due:
#         logging.info('The timer is past due!')

#     logging.info('Python timer trigger function executed.')