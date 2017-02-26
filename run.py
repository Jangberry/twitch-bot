#-*- coding: utf-8 -*-
from Bot_Twitch import main
from threading import Timer

continuer=True
while continuer==1:
    main()
    t = Timer(10, print, ['Reprise...'])
    t.start()
    arret = input('Arreter ? (O/N) Reprise si reponse absente dans 10 sec')
    t.cancel()
    if 'o' in arret or 'O' in arret:
        continuer=False
    else:
        continuer = True