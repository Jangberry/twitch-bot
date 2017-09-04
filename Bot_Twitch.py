#-*- coding: utf-8 -*-
from __future__ import print_function
import json
import random
import socket
import websocket
import requests
import sys
import threading
import time
import codecs
try:
    import lcd_i2c
except Exception:
    print("Pas d'ecran detecte")
    pass
from info import *

# Time
# time.strftime("https://docs.python.org/3/library/time.html#time.struct_time",
# time.struct_time(["https://docs.python.org/3/library/time.html#time.strftime"]))

#gamepad: \ud83c\udfae Coeur: \ud83d\udc9a t\u00e9l\u00e9 : \ud83d\udcfa abeille : \ud83d\udc1d



logfile = codecs.open("chat.log", "a", "utf-8")
#logfile = open("chat.log", "a")
logfile.write(time.ctime() + " $ " + "Nouvelle connexion \r\n")

def log(LOG):
    try:
        logfile.write(time.ctime().decode("utf8") + u" $ " + LOG.decode("utf8") + u"\r\n")
    except Exception, e:
        print("Erreur log "+str(e))
        pass

def connection():  # Connection au serveur + channel
    global s
    s = socket.socket()
    try:
        lcd_i2c.Afficher("Connexion...")
    except Exception:
        pass
    print("connecting...")
    try:
        s.connect(("irc.chat.twitch.tv", 6667))
    except Exception:
        pass
    print("identifing with nickname: " + NICK)
    s.send("PASS " + PASS + "\r\n")
    s.send("NICK " + NICK + "\r\n")
    print("joining channel " + CHANNEL)
    s.send("JOIN " + CHANNEL + "\r\n")
    print("Connected")
    try:
        lcd_i2c.Afficher("Connected", sel)
    except Exception:
        pass

def savejson():
    global infojson
    global CustMess
    jsoninfo = open("info.json", "w")
    jsoninfo.write(json.dumps(infojson))
    jsoninfo.close
    jsoninfo = open("info.json", "r")
    infojson = json.load(jsoninfo)
    jsoninfo.close()
    CustMesstemp = CustMess
    CustMess = open("Messages custom.json", "w")
    CustMess.write(json.dumps(CustMesstemp))
    CustMess = CustMesstemp
    del CustMesstemp


def refreshjson():
    global infojson
    global quotes
    global recurrenceMessages
    global CustMess
    jsoninfo = open("info.json", "r")
    infojson = json.load(jsoninfo)
    jsoninfo.close()
    quotes = infojson[u'quotes']
    recurrenceMessages = infojson[u'reccurence']
    CustMess = open("Messages custom.json")
    CustMess = json.load(CustMess)

def channelInfo():
    global users
    global modos
    global chatnb
    try:
        infos = requests.get("https://tmi.twitch.tv/group/user/" + CHANNEL.split("#")[1] + "/chatters").json()
        users = infos[u"chatters"][u"viewers"]
        # print(str(users))
        modos = infos[u"chatters"][u"moderators"] + infos[u"chatters"][u"global_mods"] + infos[u"chatters"][u"staff"] + infos[u"chatters"][u"admins"]
        # print(str(modos))
        chatters = users + modos
        if 'notch' in chatters:
            send("hlepfbfofdjfofhdocehfodbdfo")
            send("Hi @notch ... no.. I'm not a strange bot.. I'm... diferent... Sooo glad to see you, and thanks a lot for your game ;) Can you learn me how to code ? (by /w you know... i'm only a bot and i haven't as much memory as you can think...")
        chatnb = infos[u"chatter_count"]
        if len(infos[u"chatters"][u"staff"]) > 0:
            send(u"OMG !!! There is someone from the twitch's staff ?!? Welcome @" +infos[u"chatters"][u"staff"][0].encode("utf8"))

    except Exception:
        pass

def PubSub():
    global CHANNELID
    global ws
    print("Connecting to PubSub...")
    ws = websocket.create_connection("wss://pubsub-edge.twitch.tv")
    print("Pubsub connected")
    print("Getting ChannelID for subscribing to a topic")
    CHANNELID = requests.get("https://api.twitch.tv/kraken/channels/" + CHANNEL.split("#")[1] + "?client_id="+CLIENTID).json()[u'_id']
    print("Subscribing to \"bits\" and \"subscribe\" events topic for channel "+CHANNEL.split("#")[1]+" with channelid : "+str(CHANNELID))
    ws.send('{"type": "LISTEN","nonce": "Yolo elemzje c\'est le meilleur", "data": {"topics": ["channel-bits-events-v1.'+str(CHANNELID)+'"],"auth_token": "'+CLIENTID+'"}}') #, \"channel-subscribe-events-v1."+str(CHANNELID)+"\
    print(ws.recv())

def streaminfo():
    global streamstate
    global channelstate
    global followers
    global subs
    retry = True
    while retry:
        try:
            channelstate = requests.get("https://api.twitch.tv/kraken/channels/" + CHANNEL.split("#")[1] + "?client_id="+CLIENTID).json()
            streamstate = requests.get("https://api.twitch.tv/kraken/streams/" + CHANNEL.split("#")[1] + "?client_id="+CLIENTID).json()
            followers = requests.get(channelstate[u'_links'][u"follows"] + "?client_id=" + CLIENTID).json()
            retry = False
        except Exception, e:
            pass

def API():
    streaminfo()
    streamlast = streamstate[u"stream"]
    streamON = True
    while not stop:
        time.sleep(1)
        try:
            while not pause:
                if streamstate[u"stream"] != None and not streamON:
                    streamON = True
                    send(u"Stream on \ud83d\udcfa sur le jeu " + streamstate[u"stream"][u"game"] +u" avec le titre " + channelstate[u"stream"][u"channel"][u"status"])
                if streamstate[u"stream"] == None and streamON:
                    streamON = False
                    send(u"Fin de ce stream \ud83d\udcfa , merci a tous pour votre compagnie durant ce stream de "+ TimeTwitch(streamlast["created_at"]) +u", et à la prochaine ;) Pour etre au courant d'un prochain stream, allez suivre @elemzje sur twitter : https://twitter.com/Elemzje (ou activez la cloche Kappa ) ;) N'hesitez pas à follow la chaine si le contenu vous plait :)")
                if streamON:
                    if streamlast[u"game"] != streamstate[u"stream"][u"game"]:
                        send(u"Nouveau jeu : \ud83c\udfae " + streamstate[u"stream"][u"game"])
                streamlast = streamstate[u"stream"]
                while streamlast == streamstate[u"stream"] and pause == 0 and stop == 0:
                    time.sleep(2.5)
        except Exception, e:
            streaminfo()
            pass


def newfollow():
    global followers
    tempnew = []
    temp = ''
    time.sleep(5)
    streaminfo()
    followlast = followers[u'follows'][0][u"user"][u"_id"]
    while not stop:
        try:
            time.sleep(1)
            while not pause:
                tempnew = []
                temp = ''
                for i in followers[u'follows']:
                    if i == followlast:
                        break
                    temp = i[u"user"][u"display_name"]
                    if i[u"notifications"]:
                        temp = temp + u" (qui a activé(e) les notifications, merci bien <3 ;) )"
                    tempnew.append(temp)
                if len(tempnew) > 0 and len(tempnew) != 25:
                    if len(tempnew) == 1:
                        send(u"Bienvenue à @"+tempnew[0]+u". Merci pour ton follow et ton soutient, amuse-toi bien ;) <3")
                    else:
                        send(u" \ud83d\udc9a Bienvenue aux "+str(len(tempnew)).decode("utf8")+u" nouveaux follows: "+u" <3 ".join(tempnew)+u". Merci pour vos soutients \ud83d\udc9a , amusez vous bien ;)")
                followlast = followers[u'follows'][0][u"user"][u"_id"]
                try:
                    while not pause and not stop and followlast == followers[u'follows'][0][u"user"][u"_id"]:
                        time.sleep(2.5)
                except Exception, e:
                    print("erreur newfollow: "+ str(e))
                    pass
        except Exception, e:
            print("erreur newfollow: "+ str(e))
            log("erreur newfollow: "+ str(e))
            pass

def TimeTwitch(created_at, date=False):
    try:
        depuis = created_at.decode("utf8")
        debut = []
        debut.append(int(depuis.split("-")[0]))
        debut.append(int(depuis.split("-")[1]))
        debut.append(int(depuis.split("-")[2].split("T")[0]))
        debut.append(int(depuis.split("T")[1].split(":")[0]) + 1)
        debut.append(int(depuis.split("T")[1].split(":")[1]))
        debut.append(int(depuis.split("T")[1].split(":")[2].split("Z")[0]))
        debut.append(0)
        debut.append(0)
        debut.append(0)
        if date:
            global TimeTwitchDate
            TimeTwitchDate = time.strftime("%A %d %B %y a %H : %M : %S", debut)
        debut = time.time() - time.mktime(debut)
        depuis = ""
        if debut > 31536000:
            depuis = depuis + str(debut//31536000).split(".")[0] +" an"
            if debut > 63072000:
                depuis = depuis + "s "
            else:
                depuis = depuis + " "
        if debut % 31536000 > 86400:
            depuis = depuis + str((debut % 31536000) // 86400).split(".")[0] + " jour"
            if debut % 31536000 > 172800:
                depuis = depuis + "s "
            else:
                depuis = depuis + " "
        if debut % 31536000 % 8640 > 3600:
            depuis = depuis + str((debut % 31536000 %8640) // 3600).split(".")[0] + " heure"
            if (debut % 31536000 % 8640) // 3600 > 7200:
                depuis = depuis + "s "
            else:
                depuis = depuis + " "
        if debut % 31536000 % 8640 % 3600 > 60:
            depuis = depuis + str((debut % 31536000 % 8640 %3600) // 60).split(".")[0] + " minute"
            if debut % 31536000 % 8640 % 3600 > 120:
                depuis = depuis + "s "
            else:
                depuis = depuis + " "
        depuis = depuis + str((debut % 31536000 % 8640 % 3600 % 60) // 1).split(".")[0] + " secondes"
        return depuis
        del depuis
        del debut

    except Exception, e:
        print("erreur temps twitch: "+ str(e))
        log("erreur temps twitch: "+ str(e))
        pass

def newchat():
    time.sleep(5)
    streaminfo()
    chatlt = 0
    while stop == 0:
        try:
            time.sleep(1)
            while pause == 0:
                if chatnb > chatlt:
                    send("[" + str(chatnb) + " viewers (+" + str(chatnb - chatlt) + ")]")
                elif chatnb < chatlt:
                    send("[" + str(chatnb) + " viewers (" + str(chatnb - chatlt) + ")]")
                else:
                    send("[" + str(chatnb) + " viewers (=)]")
                chatlt = chatnb
                for i in range(0, 300, 5):
                    time.sleep(5)
                    if stop != 0 or pause != 0:
                        break
        except Exception, e:
            print("Probleme dans \"newchat\"" + str(e))
            pass

def recurrence():
    while stop == 0:
        try:
            time.sleep(1)
            while pause == 0 and stop == 0:
                try:
                    send(recurrenceMessages[random.randint(0, len(recurrenceMessages)-1)].encode("utf8"))
                except Exception:
                    pass
                for i in range(0, 600, 20):
                    if pause == 0 and stop == 0:
                        channelInfo()
                        streaminfo()
                    if pause == 0 and stop == 0:
                        time.sleep(5)
                    else:
                        break
        except Exception, e:
            print("reccurence: " + str(e))
            pass

def send(Message):  # Envoit de messages dans le Channel
    log("Le bot envoie : " + Message)
    if "/" in Message.split(" ")[0]:
        s.send("PRIVMSG " + CHANNEL + " :" + Message.encode("utf8") + "\r\n")  # envoie commande
        print("Commande : " + Message.encode("utf8"))
    else:
        s.send(u"PRIVMSG ".encode("utf8") + CHANNEL + u" :/me _ sckELM \ud83d\udc1d : ".encode("utf8") + Message.encode("utf8") + u" \ud83d\udc1d \r\n".encode("utf8"))  # envoie message (MrDestructoid)
        print("Envoyé : " + Message.encode("utf8"))

# Variables pour fonctions
jsoninfo = open("info.json", "r")
infojson = json.load(jsoninfo)
jsoninfo.close()
del jsoninfo
CustMess = open("Messages custom.json")
CustMess = json.load(CustMess)
quotes = infojson[u'quotes']
recurrenceMessages = infojson[u'reccurence']
user = ''
sel = -20
grains = 0
pause = False
stop = False
chatnb = 0
users = []
modos = []
streamstate = []
channelstate = []
followers = []
raffle = False
raffleusr = [None]
roulette = False

try:
    lcd_i2c.main()
except Exception:
    pass
connection()
threading.Thread(target=recurrence).start()
threading.Thread(target=newchat).start()
threading.Thread(target=API).start()
threading.Thread(target=newfollow).start()
channelInfo()
try:
    while 1:
        text = ""
        user = ""
        try:
            recu = s.recv(2040)
        except Exception:
            print('Reboot serveurs twitch')
            log("Reboot serveurs twitch")
            pause = True
            s.close
            time.sleep(5)
            connection()
            pause = False
            pass

        if "PING" in recu:  # pong
            s.send("PONG :" + recu.split(":")[1] + "\r\n")
            stop = False
            pause = False
            log("PING de twitch")

        elif len(recu.split(":")) >= 3 and "PRIVMSG" in recu:  # séparation user/texte
            user = recu.split("!")[0]
            user = user.split(":")[1]
            text = recu.split("PRIVMSG "+CHANNEL+" :")[1].split("\r\n")[0]
            print(user + " : " + text)  #console
            log(user + " : " + text)    #log

        else:
            log("message impossible a interpreter : \r\n"+recu)
            print("Recu :"+recu)

                ###______Commandes______###

        try:
            send(CustMess[text.split(" ")[0]])
        except KeyError:
            pass

        if "!quote" in text:
            if len(text.split(" ")) > 0:
                quote = text.split(" ")[-1]
            else:
                quote = text.split("quote")[-1]
            if "s" in quote:
                send(u"Voici les quotes, pour en citer une, merci d'indiquer son numero : \"" + "\", \"".join(quotes)+"\"")
                pass
            else:
                if "quote" in quote:
                    send(quotes[random.randint(0, len(quotes)-1)])
                    pass
                else:
                    try:
                        quote = int(quote)
                        send(quotes[quote-1])
                    except ValueError, e:
                        send("Veuillez entrer une valeur numerique (1, 2, 3, etc...) et non le contenu de la quote. Pour connaitre les quotes connues, tapez !quotes")
                        print(e)
                        pass
                    except IndexError, e:
                        send("Quote inconnue, tapez !quotes pour connaitre les quotes connues")
                        print(e)
                        pass

        if "salut" in text and NICK in text:
            send("sckHLT ations camarade !")

        if ((" vas " in text or " vas-" in text) and "comment" in text) and NICK in text:
            send(u"Je vais très bien, merci... mais c'est de la triche: je suis un bot...")

        if "blg" in text or "BLG" in text or "beluga" in text or "Beluga" in text or "béluga" in text or "Béluga" in text:
            send("sckBLG sckBLG sckBLG")

        if ("HLT" in text.split(" ")[0] or "salut" in text.split(" ")[0]) and user != NICK:
            send("sckHLT @" + user)

        if "!to " in text and user in modos:
            print('to')
            if "!to" in text.split(" ")[0] and len(text.split(" ")) > 2:
                if len(text.split(" ")) == 3:
                    send("/timeout " + text.split(" ")[1] + " " + text.split(" ")[2])
                else:
                    send("/timeout " + text.split(" ")[1] + " " + text.split(" ")[2]+" ".join(text.split(" ")[3:]))


        if "!au revoir" in text and user in modos:
            print("au revoir")
            send(u"/me Sur demande de @" + user + u" votre bot bien aimé s'en vas... au revoir. sckHLT ;) ")
            wiz = 0
            pause = True
            try:
                lcd_i2c.Afficher("Pause du bot", str(sel))
            except Exception:
                pass
            while not "!bonjour" in text:
                text = ""
                recu = s.recv(2040)
                if len(recu.split(":")) >= 3:
                    user = recu.split("!")[0]
                    user = user.split(":")[1]
                    for i in range(2, len(recu.split(":")), 1):
                        text = text + recu.split(":")[i] + ":"
                        print(user + " : " + text)
                elif "PING" in recu:
                    rep = recu.split(":")[1]
                    s.send("PONG :" + rep + "\r\n")
            pause = False
            send(u"/me Votre bot préféré ( Kappa ) est de retour !!! Merci à @" +user + u" pour avoir aidé le phoenix à renaitre de ses cendres")

        if "!config" in text and len(text.split(" ")) < 2:
            send(u"Tu sais que c'est marqué dans la description de la chaine ? Bon aller, vus que je suis gentil: ")
            send(u"MONITOR : BenQ XL2411Z (144 Hz ! OMG!!!), HEADSET : HYPER X CLOUD II, MOUSE : STEELSERIES Rival (la 1ere), MOUSEPAD : STEELSERIES Qck Heavy (lol j'ai le même Kappa ), KEYBOARD : STEELSERIES APEX M800, MB : ASUS H81-PLUS, CPU : INTEL i5-4690, GPU : MSI GTX 970 4GB, HDD : SEAGATE Barracuda 1 To, SDD : SEAGATE 250 Go, RAM : 2 x 4 Go CORSAIR Vengeance, PSU : CORSAIR 550W.")

        if "!pseudo" in text and len(text.split(" ")) < 2:
            send(u"Il était une fois, dans une lointaine contrée naz.. eu non.. en alsace, un jeune CM1 prénomé Bryan. Lors d'une journée d'orage, il jouait avec ses amis. Il jouais au foot. L'orage n'etait pas habituel (ciel violet, pluie fine et tout le tralala). ...")
            send(u"... Avec ses amis, ils s'amusaient à dire \"les elements se dechainent, les elements se déchainent\", ensuite, en classe, ils continuaient avec les elements, leur maîtresse dit \"oui bien l'element, il vas se calmer\". Depuis, element,est resté et s'est transformé en @elemzje. \"zje\" étant là uniquement, je cite, \"pour faire chier les gens\".")

        if "!refresh" in text.split(" ")[0]:
            refreshjson()

        if "!addquote" in text.split(" ")[0] and len(text.split(" ")) > 1 and user in modos:
            quote = ""
            quote = text.split("!addquote ")[1]
            quotes.append(quote.decode('utf8'))
            savejson()
            send("Quote enregistrée comme quote n°" + str(len(quotes)))
            log("Quote n°" + str(len(quotes)) + " Quote : " + quote)
            print("New quote (n°" + str(len(quotes)) + ") = " + quote)

        if "!tauhazard" in text.split(" ")[0]:
            if len(users) == 0:
                pass
            else:
                channelInfo()
                send("Tirage au sort d'un personne à timeout parmis les " + str(chatnb) + " personnes presentes dans le chat...")
                to = users[random.randint(0, len(users))].encode('utf8')
                send(to + u" a été tiré au sort pour un to de 100 secondes. Un dernier mot ? tu as 10 secondes...")
                time.sleep(10)
                send("/timeout " + to + u" 100 Desolé... cette commande est censé ne pas etre connue... je ne sais pas qui a hacké mon bot...")
                send("Au plaisir @" + to)

        if "!followcount" in text.split(" ")[0]:
            send(str(followers[u"_total"])+" followers... ca fait beaucoup...")

        if "!fc" in text.split(" ")[0]:
            # send("42")
            if len(text.split(" ")) > 1:
                user = text.split(" ")[1].split("@")[0]
            r = requests.get("https://api.twitch.tv/kraken/users/"+user+"/follows/channels/"+CHANNEL.split('#')[1]+"?client_id="+CLIENTID).json()
            if u'status' in r:
                if r[u"status"] == 404:
                    send("Heu... 42 !!! "+str(r[u"message"]))
                else:
                    send("Erreur inconue : " + str(r[u'status'])+str(r[u'message']))
            else:
                TimeTwitchDate = None
                temp = TimeTwitch(r[u"created_at"], True)
                if r[u"notifications"]:
                    send(u"@"+user+u" follow la chaine depuis le "+TimeTwitchDate+u", <3 soit "+temp+u". <3 En plus tu a activé les notification <3 <3 <3 , merci à toi <3")
                else:
                    send(u"@"+user+u" follow la chaine depuis le "+TimeTwitchDate+u", <3 soit "+temp+u". <3")
                del temp
                del TimeTwitchDate
            del r

        if "!uptime" in text.split(" ")[0]:
            if streamstate[u'stream'] == None:
                send("Stream OFF.. et il n'y a pas de downtime Kappa")
            else:
                send("Stream up depuis " + TimeTwitch(streamstate["stream"]["created_at"].encode("utf8")))

#        for i in [" cheat ", " hack ", " vac "]:
#            if i in text:
#                send("/timeout "+ user+" 1 Appologie du hack (timeout visant a supprimer le message menant a des debats inutiles et sans fin) ")

        if "!addcmd" in text.split(" ")[0] and (user in modos or user == elemzje) and len(text.split(" ")) > 3:
            CustMess[text.split(" ")[1]] = " ".join(text.split(" ")[2:])
            savejson()

        if "!newraffle" in text.split(" ")[0] and not raffle and (user in modos or user == 'elemzje'):
            raffleusr = []
            raffle = True
            send(u"Début de la raffle, tapez \"!raffle\" dans le chat pour participer")

        if "!raffle" == text.split(" ")[0] and raffle and not user in raffleusr:
            raffleusr.append(user)

        if "!raffleend" in text.split(" ")[0] and raffle and (user in modos or user == 'elemzje'):
            raffle = False
            send(u"Fin de la raffle, il y a "+str(len(raffleusr))+u" participants.")

        if "!raffledraw" in text.split(" ")[0] and not raffle and (user in modos or user == 'elemzje') and len(raffleusr) > 0:
            send(u"Tirage au sort d'une personne parmis les "+str(len(raffleusr))+u" participants")
            raffledraw = raffleusr[random.randint(0, len(raffleusr)-1)]
            send(raffledraw + u" à l'honneur d'avoir été tiré au sort, bravo à toi ;)")

        if "!roulette" in text.split(' ')[0]:
            if ("francais" in text.split('!roulette')[1] or "français" in text.split('!roulette')[1]) and not roulette:
                send(u"Départ de la roulette francaise (parce-qu'on joue avec un LFP586) vous devez d'abord remplir le barillet, tapez !barillet remplir (attention, si vous le faites plusieurs fois, il y aura plusieurs balles...), ensuite, tapez !roulette pour tirer (ne vous inquétez pas, vous avez un GILAYY, ça coupe juste un peu le souflle...). Si un coup part, vous devez reremplir le barillet. Faites \"!roulette stop\" pour ranger cette arme..")
                send(u"Ce jeu est aussi parfois appelé \"test de confiance du GIGN\"")
                barillet = [False, False, False, False, False, False, 0]
                roulette = True
            elif "remplir" in text.split("!roulette")[1] and roulette:
                temp = random.randint(0, 5)
                continuer = True
                while continuer:
                    if not barillet[temp]:
                        barillet[temp] = True
                        send(u"Une balle à été placé dans une chambre aleatoire du barillet")
                        continuer = False
                    elif barillet[:6] == [True, True, True, True, True, True]:
                        send("Le barillet est plein")
                        continuer = False
                    else:
                        temp = random.randint(0, 5)
                print(barillet)
            elif "stop" in text.split("!roulette")[1] and roulette:
                roulette = False
                del barillet
                send(u"Bon... on arette de jouer.. on risquerai de blesser quelqu'un...")
            elif roulette:
                if barillet[barillet[6]]:
                    send(u"PAN")
                    barillet[barillet[6]] = False
                    send(u"/timeout "+user+u" "+str(random.randint(10, 45))+u" Ourf.. ce tir a fait mal, il vas vous falloir du temps pour reprendre votre souffle...")
                else:
                    send(u"Click")
                barillet[6] += 1
                if barillet[6] > 5:
                    barillet[6] = 0

        if "!command" in text.split(" ")[0]:
            temp = u"Voici les commandes possibles: "
            for i in CustMess:
                temp += i + " "
            send(temp)

except KeyboardInterrupt:
    stop = True
    pause = True
    send("/disconnect")
    savejson
    print("En attente de la fin des threads...")
    for i in range(0, 5):
        time.sleep(1)
        print(".")
    log("Extinction du Bot: KeyboardInterrupt")
    try:
        lcd_i2c.Afficher("KeyboardInterrupt", "fin")
    except Exception:
        pass

except ZeroDivisionError, e:
    print(str(e))
    log("/!\\ Crash : " + str(e) + "/!\\ \n\r /!\\ /!\\ /!\\ /!\\ /!\\ /!\\ /!\\ /!\\ /!\\ /!\\ ")
    send("/disconnect")
    savejson()
    log(str(e))
    try:
        lcd_i2c.Afficher("Bug:" + str(e))
    except Exception:
        pass
    stop = True
    pause = True

finally:
    stop = True
    pause = True
    log("Fin de l'execution/fin du log \r\n \n")
    logfile.close
