"""
Checks toggl track to see if person idle for too long, if so punishes them.
"""
import logging
import re
import toggl_punish_utils.toggl as toggl

# import azure.functions as func


# PATH_PREFIX = "" #str(Path.home()) + "/data"

# app = func.FunctionApp()


# @app.schedule(
#     schedule="0 * * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
# )
# #Azure expects this name, so it has to be in camelCase, so we disable the pylint warning.
# def timer_trigger(myTimer: func.TimerRequest) -> None: #pylint: disable=C0103
#     """
#     The basic timer trigger function.
#     """
#     if myTimer.past_due:
#         logging.info("The timer is past due!")

#     main()

#!/usr/bin/python3


PERIOD = 60


class Regex:
    """
    Regular Expression Constants.
    """

    TIME = r"^\((\d{1,2}):(\d{1,2})\)"
    DURATION = r"^\((\d+)\)"
    COUNT = r"\(\s*count:\s*(\d+)\s*\)$"  # the /s at the beginning and end is there, because it might not start at end.


regex_dict = {"time": Regex.TIME, "duration": Regex.DURATION, "count": Regex.COUNT}

# COUNT_KEY = "punish_val"
# LAST_UPDATE_KEY = "last_update"
# DATA_PATH = f"{PATH_PREFIX}/punish_data.db"


def get_last_count():
    """
    Looks at the currently running entries, and based on that, returns the count value of the latest entry.
    """
    entries = toggl.get_entries()
    last_count = 0
    for entry in entries:
        # logging.info(entry["description"])
        count = re.findall(Regex.COUNT, entry["description"])
        # logging.info(count)
        if count:
            last_count = int(count[0])
            break
    return last_count


def gen_new_desc(desc_no_extras, punish_val, end=None):
    """
    The timer description should always have the punish count displayed on it.
    This takes the desc. without the punish count, and the punish count,
    and combines them together to give the proper timer description.
    """
    end_str = toggl.to_local(end).strftime("(%I:%M)") if end else ""
    new_desc = f"{end_str}{desc_no_extras}(count: {punish_val})"
    return new_desc


def update_punish_val(new_val):
    """
    takes the new value that the program wants to assign to punish_val,
    and then adjusts it so that it lies within proper bounds.
    """
    if new_val < 0:
        new_val = 0
        logging.warning("punish_val was found to be negative, resetting to 0.")
    elif new_val > 5000:
        new_val = 0
        logging.warning("punish_val was found to be > 5000, resetting to 0.")

    return new_val


def get_results(regexs, desc):
    """
    Takes the description of the timer, and then runs the attribute regexs
    to extract information, like the punish count.
    """
    results = {name: re.findall(regex, desc) for name, regex in regexs.items()}
    return results


def strip_desc(regexs, desc):
    """
    This removes all the extras/attributes in the timer description
    as defined by the regexs, and then returns the resulting pure desc.
    """
    for regex in regexs:
        desc = re.sub(regex, "", desc)

    return desc


def remove_extras(regexs, desc):
    """
    This removes all the extras/attributes in the timer description
    as defined by the regexs, and then returns the resulting pure desc.
    """
    return strip_desc(regexs.values(), desc)


# regexs = {k.lower() : v for k, v in vars(Regex)} //doesn't work, includes extra stuff.

# logging.basicConfig(
#     filemode="w",
#     filename="toggl_punish.log",
#     format="%(asctime)s %(levelname)s:%(message)s",
#     level=logging.INFO,
# )
# logging.info("=================NEW RUN=====================")
# my_scheduler = sched.scheduler(time.time, time.sleep)
# start_time = time.time()
# my_scheduler.enterabs(start_time, 1, main, (my_scheduler, start_time))
# my_scheduler.run()
