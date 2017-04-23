#-*- coding: utf-8 -*-
import Bot_Twitch
import importlib
import time

while 1:
    Bot_Twitch()
    print('Redemarrage du bot...')
    time.sleep(5)
    reload(Bot_Twitch)
    time.sleep(3)
