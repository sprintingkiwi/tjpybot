from tjpybot import *


workspace = str(sys.argv[1])

bot = TJBot()

############################################################
# CONVERSATION CYCLE
############################################################

user_input = ""

print("Starting conversation in workspace: " + workspace)
while True:

    bot.speak(bot.converse(user_input, workspace))
    user_input = bot.listen()

    # Only for testing purpose (comment line above)
    # user_input = "Ciao, mi chiamo Alessandro"


############################################################
# The end
############################################################

print("Goodbye")
time.sleep(1)
