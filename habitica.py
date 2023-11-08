# /* ========================================== */
# /* [Users] Required script data to fill in    */
# /* ========================================== */
import requests
import logging
import toggl_punish_utils.toggl as toggl

TIMEOUT = 10

USER_ID = "e544ce9c-d7a4-448c-8b1b-f6b4c4595be1"
API_TOKEN = "c0b7ac19-9616-4f1a-b0d9-7e9ae9de0465"  # // Do not share this to anyone
# WEB_APP_URL = "https://script.google.com/macros/s/AKfycbza2ycTHQAfNt_L53DrjXKf1uJOiePT3x1R5SGl7vbwSojuLMSsRWh5z6ujZfzrdkNu6A/exec"

# /* ========================================== */
# /* [Users] Required customizations to fill in */
# /* ========================================== */
# // [Developers] Place all mandatory user-modified variables here
# // - e.g, skill to use, number of times to use, task to use skill on, etc.

# /* ========================================== */
# /* [Users] Optional customizations to fill in */
# /* ========================================== */
# // [Developers] Place all optional user-modified variables here
# // - e.g. enable/disable notifications, enable/disable script features, etc.

# /* ========================================== */
# /* [Users] Do not edit code below this line   */
# /* ========================================== */
# // [Developers] Place your user ID and script name here
# // - This is used for the "X-Client" HTTP header
# // - See https://habitica.fandom.com/wiki/Guidance_for_Comrades#X-Client_Header
AUTHOR_ID = "e544ce9c-d7a4-448c-8b1b-f6b4c4595be1"
SCRIPT_NAME = "OneScriptToRuleThemAll"
HEADERS = {
    "x-client": AUTHOR_ID + "-" + SCRIPT_NAME,
    "x-api-user": USER_ID,
    "x-api-key": API_TOKEN,
}

# // [Developers] Add global variables here
# // - Note that these do not persist in between script calls
# // - If you want to save values between calls, use PropertiesService
# // - See https://developers.google.com/apps-script/reference/properties/properties-service


def create_reward(alias, cost):
    """
    Creates a Reward in Habitica with the given alias and cost, the name is the same as the alias
    Note the alias must not have spaces, (It must be a valid identifier)
    """
    payload = {"text": alias, "type": "reward", "alias": alias, "value": cost}

    # params = {
    #   'method' : 'POST',
    #   'headers' : HEADERS,
    #   'contentType' : 'application/json',
    #   "payload" : JSON.stringify(payload),
    #   "muteHttpExceptions" : true
    # }
    url = "https://habitica.com/api/v3/tasks/user"
    response = requests.post(url=url, headers=HEADERS, json=payload, timeout=TIMEOUT)
    # response = UrlFetchApp.fetch(url, params)
    logging.info("create_reward response: %s", toggl.log_str(response))
    return response


def buy_reward(alias):
    """
    Purchases a reward with the given alias on behalf of the user
    """
    # const params = {
    #   'method': 'POST',
    #   'headers': HEADERS,
    #   "muteHttpExceptions" : true
    # };
    url = "https://habitica.com/api/v3/tasks/" + alias + "/score/down"
    response = requests.post(url=url, headers=HEADERS, timeout=TIMEOUT)
    logging.info("buy_reward response: %s", toggl.log_str(response))
    return response


def delete_reward(alias):
    """
    Deletes the reward with the given alias on behalf of the user
    """
    # const params = {
    #   'method': 'DELETE',
    #   'headers': HEADERS,
    #   "muteHttpExceptions" : true
    # };
    url = "https://habitica.com/api/v3/tasks/" + alias
    response = requests.delete(url=url, headers=HEADERS, timeout=TIMEOUT)
    logging.info("delete_reward response: %s", toggl.log_str(response))
    return response


# function doOneTimeSetup() {

#   createReward(ALIAS, 3);
#   buyReward(ALIAS);
#   deleteReward(ALIAS);
#   // [Developers] These are one-time initial setup instructions that we'll ask
#   //   the user to manually execute only once, during initial script setup
#   // - Add api_createWebhook() here, already set up to activate the trigger to the
#   //   event that you want to service
#   // - Feel free to do all other one-time setup actions here as well
#   //   e.g. creating tasks, reward buttons, etc.
# }

# function doPost(e) {

#   // [Developers] This is the function that will be executed whenever Habitica
#   //   encounters the designated event

#   const dataContents = JSON.parse(e.postData.contents);
#   const webhookType = dataContents.type;

#   console.log(dataContents);

#   if(!(webhookType === "scored" && dataContents.task.down && dataContents.task.type === "habit")) {
#     return HtmlService.createHtmlOutput();
#   }

#   const name = dataContents.task.text;
#   let coinsCost = 0;
#   const coinsRegex = /cost:\s*(\d+)/;
#   if (coinsRegex.test(name)) {
#     coinsCost = parseInt(name.match(coinsRegex)[1]);
#   }
#   const ALIAS = "PunishReward";
#   createReward(ALIAS, coinsCost);
#   buyReward(ALIAS);
#   deleteReward(ALIAS);
#   ///const punishCost = Math.trunc(coinsCost * 7.5);

#   //console.log(e);

#   // Logger.log(e);
#   //throw new Error(JSON.stringify(e));

#   // [Developers] Add script actions here

#   return HtmlService.createHtmlOutput();
# }

# // [Developers] Place all other functions below doOneTimeSetup() and doPost()
# // - Ideally prefix functions that access the API with "api_" to quickly see which ones
# //   access the API and be able budget your 30 requests per minute limit well
