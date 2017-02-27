#-*- coding: utf-8 -*-
import Bot_Twitch
import importlib
import time

lol = True

while lol:
    try:
        Bot_Twitch()
    except TypeError:
        pass
    print('Redemarrage du bot...')
    time.sleep(5)
    reload(Bot_Twitch)
    time.sleep(3)