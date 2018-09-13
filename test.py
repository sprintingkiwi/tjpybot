from tjpybot import *

bot = TJBot("192.168.1.157")

bot.led("red")

print(bot.recognize())

bot.set_volume("100")
# bot.speak("ciao ")
# bot.speak("come stai?")
t = bot.translate("Oggi mi sento molto felice", source="it", target="en")
print(t)

bot.speak(bot.analyze_tone(t))
# a = bot.listen()
# print(a)
