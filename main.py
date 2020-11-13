import os
import time
import re
import sys
from slackclient import SlackClient
from WaterBot.bot import WaterBot
import sched, time
# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
# commands
HELP_COMMAND = "help"
SUBSCRIBE_COMMAND = "subscribe"
UNSUBSCRIBE_COMMAND = "unsubscribe"
SET_USER_WATER = "set"
SET_USER_TIME = "set_time"

bot = WaterBot()
"""
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot command is found, this function returns a tuple of command and channel.
    If its not found, then this function returns None, None.
"""
def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]
    return None, None, None
"""
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, returns None
"""
def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

"""
Sends the response to the channel
"""
def send_message(channel, response):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )
"""
    Executes bot command if the command is known
"""
def handle_command(command, channel, user_id):
    # Default response is help text for the user
    default_response = "Non conosco questo comando. Prova con *{}*.".format(HELP_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(HELP_COMMAND):
        response = "Sono un bot che ti ricorda di bere!"
    elif command.startswith(SUBSCRIBE_COMMAND):
        bot.addUser(user_id)
        response = "Ti sei iscritto al programma di WaterBot"
    elif command.startswith(UNSUBSCRIBE_COMMAND):
        bot.removeUser(user_id)
        response = "Disiscritto da WaterBot"
    elif command.startswith(SET_USER_WATER):
        try:
            command, water = command.split(" ")
            bot.setUserWater(user_id, water)
            response = "Ho aggiornato la tua dose giornaliera di acqua"
        except KeyError:
            response = "Non sei iscritto. lancia il comando *{}*.".format(SUBSCRIBE_COMMAND)
        except ValueError:
            response = "Errore parametro. Il comando deve essere nel formato @WaterBot set x"
    elif command.startswith(SET_USER_TIME):
        # your code here
        
    # Sends the response back to the channel
    send_message(channel, response or default_response)
    #send_message(user_id, response or default_response)

def notifyUsers():
    notify_users = bot.update()
    for user in notify_users:
        send_message(user.id, "Prenditi una pausa e bevi un bicchiere!")


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        #s = sched.scheduler(time.time, time.sleep)
        #s.enter(60, 1, notifyUsers, (s,))
        #s.run()
        s = 0
        while True:
            try:
                command, channel, user_id = parse_bot_commands(slack_client.rtm_read())
                if command:
                    print("command", command, "ch", channel, "user_id", user_id)
                    handle_command(command, channel, user_id)
                #notify_users every minute
                s += RTM_READ_DELAY
                if s >= 60:
                    notifyUsers()
                    s = 0
                time.sleep(RTM_READ_DELAY)
            except KeyboardInterrupt:
                sys.exit("Keyboard interrupt")
            except Exception as e:
                print("An exception occurred", sys.exc_info()[0], "msg", str(e))
    else:
        print("Connection failed. Exception traceback printed above.")


