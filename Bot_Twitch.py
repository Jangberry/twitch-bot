#-*- coding: utf-8 -*-
#python27
import importlib
import json
import random
import socket
import sys
import threading
import time
import requests
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

s = socket.socket()

logfile = open("chat.log", "w")
logfile.write(time.ctime() + " $ " + "Nouvelle connexion \r\n")

def log(LOG):
    try:
        logfile.write(time.ctime() + u" $ " + LOG +u"\r\n")
    except Exception:
        pass

def connection():  # Connection au serveur + channel
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
            chatnb = infos[u"chatter_count"]
            if len(infos[u"chatters"][u"staff"]) > 0:
                send(u"OMG !!! There is someone from the twitch's staff ?!? Welcome @" +infos[u"chatters"][u"staff"][0].encode("utf8"))

        except Exception, e:
            print("channelInfo : " + str(e))
            pass

def streaminfo():
    global streamstate
    global channelstate
    global followers
    retry = True
    while retry:
      try:
        streamstate = requests.get("https://api.twitch.tv/kraken/streams/" + CHANNEL.split("#")[1] + CLIENTID).json()
        channelstate = requests.get("https://api.twitch.tv/kraken/channels/" + CHANNEL.split("#")[1] + CLIENTID).json()
        followers = requests.get("https://api.twitch.tv/kraken/channels/" + CHANNEL.split("#")[1] + "/follows" + CLIENTID).json()
        retry = False
      except Exception, e:
        print("Stream info :" + str(e))
        pass

def newstreaminfo():
    streamlast = None
    streamON = False
    while stop == 0:
        time.sleep(1)
        streaminfo()
        while pause == 0:
            if streamstate[u"stream"] != None and not streamON:
                streamON = True
                send(u"Stream on \ud83d\udcfa sur le jeu " + streamstate[u"stream"][u"game"] +u" avec le titre " + channelstate[u"stream"][u"channel"][u"status"])
            if streamstate[u"stream"] == None and streamON:
                streamON = False
                send(u"Fin de ce stream \ud83d\udcfa , merci a tous pour votre compagnie, et à la prochaine ;) n'hesitez à follow la chaine si le contenu vous plait, et que ca n'est pas deja fait :) Pour rester informé et etre au courant d'un prochain stream, allez suivre @elemzje sur twitter : https://twitter.com/Elemzje")
            if streamON:
                if streamlast[u"game"] != streamstate[u"stream"][u"game"]:
                        send(u"Nouveau jeu : \ud83c\udfae " + streamstate[u"stream"][u"game"])
          
            streamlast = streamstate[u"stream"]
            try:
                while streamlast == streamstate[u"stream"] and pause == 0 and stop == 0:
                        streaminfo()
                        time.sleep(4)
            except Exception, e:
                    streaminfo
                    pass

def newfollow():
        tempnew = []
        temp = ''
        time.sleep(5)
        streaminfo()
        follolast = followers[u'follows'][0]
        while not stop:
            time.sleep(1)
            while not pause:
                tempnew = []
                temp = ''
                for i in followers[u'follows']:
                        temp = i[u"user"][u"display_name"]
                        if i[u"notifications"]:
                            temp = temp + u" (qui a activé(e) les notifications, merci bien <3 ;) )"
                        tempnew.append(temp)
                if len(tempnew) > 0 and not len(tempnew) == 25:
                    if len(tempnew) == 1:
                        send(u"Bienvenue à @"+tempnew[0]+u". Merci pour ton follow et ton soutient, amuse-toi bien ;) <3")
                    else:
                        send(u" \ud83d\udc9a Bienvenue aux "+str(len(tempnew)).decode("utf8")+u" nouveaux follows: "+u" <3 ".join(tempnew)+u". Merci pour vos soutients \ud83d\udc9a , amusez vous bien ;)")
                followlast = followers[u'follows'][0]
                try:
                    while not pause and not stop and followlast[u'user'][u'display_name'] == followers[u'follows'][0][u'user'][u'display_name']:
                        time.sleep(4)
                        streaminfo
                except Exception:
                    pass
        

def newchat():
        try:
            time.sleep(5)
            streaminfo()
            chatlt = 0
            followlast = followers[u'follows'][0]
            while stop == 0:
                time.sleep(1)
                while pause == 0:
                    if chatnb > chatlt:
                        send("[" + str(chatnb) + " viewers (+" + str(chatnb - chatlt) + ")]")
                    elif chatnb < chatlt:
                        send("[" + str(chatnb) + " viewers (" + str(chatnb - chatlt) + ")]")
                    else:
                        send("[" + str(chatnb) + " viewers (=)]")
                    chatlt = chatnb
                    for i in range(0, 150, 5):
                        time.sleep(5)
                        if stop != 0 or pause != 0:
                            break
        except Exception, e:
            print("Probleme dans \"newchat\"" + str(e))
            pass

def recurrence():
        try:
            while stop == 0:
                time.sleep(1)
                while pause == 0 and stop == 0:
                    try:
                        send(recurrenceMessages[random.randint(0, len(recurrenceMessages)-1)].encode("utf8"))
                    except Exception:
                        pass
                    for i in range(0, 300, 20):
                        if pause == 0 and stop == 0:
                            channelInfo()
                            streaminfo()
                        else:
                            break
                        if pause == 0 and stop == 0:
                            time.sleep(5)
                        else:
                            break
                        if pause == 0 and stop == 0:
                            time.sleep(5)
                        else:
                            break
                        if pause == 0 and stop == 0:
                            time.sleep(5)
                        else:
                            break
        except Exception, e:
            print("reccurence: " + str(e))
            pass
    
def send(Message):  # Envoit de messages dans le Channel
        try:
                log("Le bot envoie : " + Message)
        except Exception, e:
                print(e)
                pass
        if "/" in Message.split(" ")[0]:
            s.send("PRIVMSG " + CHANNEL + " :" + Message.encode("utf8") + "\r\n")  # envoie commande
            print("Commande : " + Message.encode("utf8"))
        else:
            s.send(u"PRIVMSG ".encode("utf8") + CHANNEL.decode("ascii").encode("utf8") + u" :/me _ MrDestructoid \ud83d\udc1d : ".encode("utf8") + Message.encode("utf8") + u" \ud83d\udc1d \r\n".encode("utf8"))  # envoie message
            print("Envoyé : " + Message.encode("utf8"))

if 1:
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
    wiz = 0
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

    try:
        lcd_i2c.main()
    except Exception:
        pass
    connection()
    threading.Thread(target=recurrence).start()
    threading.Thread(target=newchat).start()
    threading.Thread(target=newstreaminfo).start()
    threading.Thread(target=newfollow).start()
    channelInfo()

    arret = False
    try:
        while 1:
    
            text = ""
            user = ""
            recu = s.recv(2040)
    
            if "PING" in recu:  # pong
                rep = recu.split(":")[1]
                s.send("PONG :" + rep + "\r\n")
                stop = False
                pause = False
                log("PING de twitch")
    
            elif len(recu.split(":")) >= 3 and "PRIVMSG" in recu:  # séparation user/texte
                user = recu.split("!")[0]
                user = user.split(":")[1]
                text = recu.split("PRIVMSG "+CHANNEL+" :")[1].split("\r\n")[0]
                print(user + " : " + text)  #console
                log(user + " : " + text)    #log
        
            elif "RECONNECT" in recu:
                1/0
            else:
                log("message impossible a interpreter : /r/n        "+recu)
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
                        send("veuillez indiquer quelle quote vous voullez")
                        pass
                    else:
                        try:
                            quote = int(quote)
                            send(quotes[quote+1])
                        except ValueError, e:
                            send("Veuillez entrer une valeur numerique (1, 2, 3, etc...) et non le contenu de la quote. Pour connaitre les quotes connues, tapez !quotes")
                            print(e)
                            pass
                        except IndexError, e:
                            send("Quote inconnue, tapez !quotes pour connaitre les quotes connues")
                            print(e)
                            pass
    
            if "salut" in text and "@mistercraft38" in text:
                send("sckHLT ations camarade !")
    
            if ((" vas " in text or " vas-" in text) and "comment" in text) and "@mistercraft38" in text:
                send("Je vais tres bien, merci... mais c'est de la triche: je suis un bot...")
    
            if ("blg" or "BLG" or "beluga" or "Beluga" or "béluga" or "Béluga") in text:
                send("sckBLG sckBLG sckBLG")
    
            if ("HLT" in text or "salut" in text) and user != "mistercraft38":
                send("sckHLT @" + user)
    
            if "!to " in text and user in modos:
                print('to')
                if "!to" in text.split(" ")[0] and len(text.split(" ")) > 2:
                    send("/timeout " + text.split(" ")[1] + " " + text.split(" ")[2])
    
            if user == "wizebot" and wiz == 0:
                send("bonjour @wizebot je viens en paix, pour ne pas t'assister. Je serai present ici pour te faire souffrir.")
                wiz = 1
    
            if "!team" in text.split(" ")[0]:
                send("Elemzje fait partis de la team des 9L (9Lives), une team de full sckBGT")
    
            if "!au revoir" in text and user in modos:
                print("au revoir")
                send("/me Sur demande de @" + user + " votre bot bien aimé s'en vas... au revoir. sckHLT ;) ")
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
                send("/me Votre bot préféré ( Kappa ) est de retour !!! Merci à @" +user + " pour avoir aidé le phoenix à renaitre de ses cendres")
    
            if "!config" in text and len(text.split(" ")) < 2:
                send("Tu sais que c'est marqué dans la description de la chaine ? Bon aller, vus que je suis gentil: ")
                send("MONITOR : BenQ XL2411Z (144 Hz ! OMG!!!), HEADSET : HYPER X CLOUD II, MOUSE : STEELSERIES Rival (la 1ere), MOUSEPAD : STEELSERIES Qck Heavy (lol j'ai le même Kappa ), KEYBOARD : STEELSERIES APEX M800, MB : ASUS H81-PLUS, CPU : INTEL i5-4690, GPU : MSI GTX 970 4GB (j'ai 2x moins de vram mais bon... j'ai une 750Ti...), HDD : SEAGATE Barracuda 1 To, SDD : SEAGATE 250 Go (riche...), RAM : 2 x 4 Go CORSAIR Vengeance, PSU : CORSAIR 550W.")
    
            if "!pseudo" in text and len(text.split(" ")) < 2:
                send("il était une fois, dans une lointaine contrée naz.. eu non.. il  était une fois, en alsace, un jeune CM1 prénomé Bryan (brillant... LOL). Lors d'une journée d'orage, il jouait avec ses amis. Il jouais au foot. L'orage n'etait pas habituel (ciel violet, pluie fine et tout le tralala). ...")
                send("... Avec ses amis, ils s'amusaient à dire \"les elements se dechainent, les elements se déchainent\", ensuite, en classe, ils continuaient avec les elements, leur maîtresse dit \"oui bien l'element, il vas se calmer\". Depuis, element,est resté et s'est transformé en @elemzje. \"zje\" étant là uniquement, je cite, \"pour faire chier les gens\".")

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
                    send(to + " a été tiré au sort pour un to de 100 secondes. Un dernier mot ? tu as 10 secondes...")
                    time.sleep(10)
                    send("/timeout " + to + " 100")
                    send("Au plaisir @" + to)

            if "!followcount" in text.split(" ")[0]:
                send(str(followers[u"_total"])+" followers... ca fait beaucoup...")

            if "!fc" in text.split(" ")[0]:
                # send("42")
                follow = requests.get("https://api.twitch.tv/kraken/users/"+user+"/follows/channels/"+CHANNEL.split('#')[1]+CLIENTID).json()
                followN = follow[u"notifications"]
                follow = follow[u"created_at"]
                Follow = []
                Follow.append(int(follow.split("-")[0]))
                Follow.append(int(follow.split("-")[1]))
                Follow.append(int(follow.split("-")[2].split("T")[0]))
                Follow.append(int(follow.split("T")[1].split(":")[0])+1)
                Follow.append(int(follow.split("T")[1].split(":")[1]))
                Follow.append(int(follow.split("T")[1].split(":")[2].split("Z")[0]))
                Follow.append(0)
                Follow.append(0)
                Follow.append(0)
                FollowTime = [time.strftime("%A %d %B %y à %H : %M : %S", Follow)]
                FollowTime.append(time.time()-time.mktime(Follow))
                temp = ""
                if FollowTime[1] > 31536000:
                    temp = temp + str(FollowTime[1]//31536000) +" an"
                    if FollowTime[1] > 63072000:
                        temp = temp + "s "
                    else:
                        temp = temp + " "
                if FollowTime[1]%31536000 > 86400:
                    temp = temp + str((FollowTime[1] % 31536000)//86400)+" jour"
                    if FollowTime[1]%31536000 > 172800:
                        temp = temp + "s "
                    else:
                        temp = temp + " "
                if FollowTime[1]%31536000%8640 > 3600:
                    temp = temp + str((FollowTime[1]%31536000%8640)//3600)+" heure"
                    if (FollowTime[1]%31536000%8640)//3600 > 7200:
                        temp = temp + "s "
                    else:
                        temp = temp + " "
                if FollowTime[1]%31536000%8640%3600 > 60:
                    temp = temp + str((FollowTime[1]%31536000%8640%3600)//60) +" minute"
                    if FollowTime[1]%31536000%8640%3600 > 120:
                        temp = temp + "s "
                    else:
                        temp = temp + " "
                temp = temp + str((FollowTime[1]%31536000%8640%3600%60)//1) + " secondes"
                FollowTime.append(temp)
                send("Tu follow la chaine depuis le "+FollowTime[0].decode("utf8")+", soit "+FollowTime[2]+". <3 Ou "+str(FollowTime[1])+" secondes... ")
                if followN:
                    send("En plus il a activé les notifications... merci beaucoup @"+user)
                del follow
                del followN
                del Follow
                del FollowTime
                del temp

            if "!epoch" in text.split(" ")[0]:
                send("L'epoch de linux: un epoch est une date de reference utilise par plusieurs languages de programmation (y compris le python, language de ce bot) qui permet d'obtenir une valeur en seconde depuis cette date, sachant que cette date peux changer d'un OS a un autre. Sur linux (OS sur lequel tourne le bot), l'epoch est le 1er janvier 1970 à 00:00 UTC. Plus d'infos https://fr.wikipedia.org/wiki/Epoch")

            if "!uptime" in text.split(" ")[0]:
              if streamstate[u'stream'] == None:
                send("Stream OFF.. et il n'y a pas de downtime Kappa")
              else:
                up = streamstate["stream"]["created_at"]
                uptime = []
                uptime.append(int(up.split("-")[0]))
                uptime.append(int(up.split("-")[1]))
                uptime.append(int(up.split("-")[2].split("T")[0]))
                uptime.append(int(up.split("T")[1].split(":")[0]) + 1)
                uptime.append(int(up.split("T")[1].split(":")[1]))
                uptime.append(int(up.split("T")[1].split(":")[2].split("Z")[0]))
                uptime.append(0)
                uptime.append(0)
                uptime.append(0)
                uptime = time.time() - time.mktime(uptime)
                up = ""
                if uptime % 31536000 > 86400:
                    up = up + str((uptime % 31536000) // 86400) + " jour"
                    if uptime % 31536000 > 172800:
                        up = up + "s "
                    else:
                        up = up + " "
                if uptime % 31536000 % 8640 > 3600:
                    up = up + str((uptime % 31536000 %8640) // 3600) + " heure"
                    if (uptime % 31536000 % 8640) // 3600 > 7200:
                        up = up + "s "
                    else:
                        up = up + " "
                if uptime % 31536000 % 8640 % 3600 > 60:
                    up = up + str((uptime % 31536000 % 8640 %3600) // 60) + " minute"
                    if uptime % 31536000 % 8640 % 3600 > 120:
                        up = up + "s "
                    else:
                        up = up + " "
                up = up + str((uptime % 31536000 % 8640 % 3600 % 60) // 1) + " secondes"
                send("Stream up depuis " + up)
                del up
                del uptime

            if "xbox" in text and "pc" in text:
                send("/timeout "+user+" 1 Ce debat n'a pas lieu ici... Kappa pc master race... en toute objectivité Kappa")
            
            if cmp(text.split(" "), ["cheat", "hack", "vac", "ricki", "shaiiko"])>1:
                send("/timeout "+ user+" 1 Appologie du hack (timeout visant a supprimer le message menant a des debats inutiles et sans fin) ")

            if "!addcmd" in text.split(" ")[0] and (user in modos or user == elemzje) and len(text.split(" ")) > 3:
                CustMess[text.split(" ")[1]] = " ".join(text.split(" ")[2:])
                savejson()

    except KeyboardInterrupt:
        stop = True
        pause = True
        send("Arret du bot")
        send("/disconnect")
        savejson
        print("En attente de la fin des threads...")
        for i in range(0, 8):
            time.sleep(0.5)
            print('.')
        log("Extinction du Bot: KeyboardInterrupt \r\n")
        try:
            lcd_i2c.Afficher("KeyboardInterrupt", "fin")
        except Exception:
            pass
        
    except ZeroDivisionError:
        savejson()
        stop = True
        pause = True
        pass

    except Exception, e:
        print(str(e))
        log(time.ctime() + " $ " + "Crash : " + str(e))
        send("Ce robot a crash... Merci d'en informer son créateur... J'AI ENVIE D'ETRE UN BOT SANS BUG !!! Erreur : " + str(e))
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