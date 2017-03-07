#-*- coding: utf-8 -*-
import socket
import sys
import time
import threading
import random
import requests
import json
import importlib
import lcd_i2c
from info import *

s = socket.socket()

def connection():  # Connection au serveur + channel
        lcd_i2c.Afficher("Connexion...")
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
        lcd_i2c.Afficher("Connected", sel)
    
    
def log(LOG):
        try:
            logfile.write(time.ctime() + " $ " + LOG + " \r\n")
        except UnboundLocalError:
            pass
        except Exception, e:
            print('e')
            lcd_i2c.Afficher("Reprise log")
            logfile.close
            logfile = open("log.txt", "w")
            logfile.write(time.ctime() + " $ Reprise du log: " + LOG +" \r\n")
    
def savejson():
        global infojson
        jsoninfo = open("info.json", "w")
        jsoninfo.write(json.dumps(infojson))
        jsoninfo.close
        jsoninfo = open("info.json", "r")
        infojson = json.load(jsoninfo)
        jsoninfo.close()
    
def refreshjson():
        global infojson
        global quotes
        global recurrenceMessages
        global dejavu
        jsoninfo = open("info.json", "r")
        infojson = json.load(jsoninfo)
        jsoninfo.close()
        quotes = infojson[u'quotes']
        recurrenceMessages = infojson[u'reccurence']
        dejavu = infojson[u'dejavu']
    
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
            if len(infos[u"chatters"][u"staff"])>0:
                send("OMG !!! There is someone from the twitch's staff ?!? Welcome @"+infos[u"chatters"][u"staff"][0])
    
        except Exception, e:
            print("channelInfo : " + str(e))
            pass

def streaminfo():
    global streamstate
    global channelstate
    try:
        streamstate = requests.get("https://api.twitch.tv/kraken/streams/"+CHANNEL.split("#")[1]+CLIENTID)
        channelstate = requests.get("https://api.twitch.tv/kraken/channels/"+CHANNEL.split("#")[1]+CLIENTID)
    except Exception, e:
        print("Stream info :"+str(e))
        pass

def uptime():
    up = streamstate["stream"]["created_at"]        #2017-03-06T12:01:50Z
    
    return up

def newstreaminfo():
    streamlast = None
    while stop == 0:
        time.sleep(5)
        streaminfo()
        while pause == 0:
            if streamstate["stream"] != None and streamON == 0:
                streamON = True
                send("Stream on sur le jeu "+streamstate["stream"]["game"]+" avec le titre "+channelstate["stream"]["channel"]["status"])
            if streamstate["stream"] == None and streamON:
                streamON = False
                send("Fin de ce stream, merci a tous pour votre compagnie, et à la prochaine ;) n'hesitez à follow la chaine si le contenu vous plait :) Pour rester informé et etre au courant d'un prochain stream, allez suivre @elemzje sur twitter : https://twitter.com/Elemzje")
            if streamON:
                if streamlast["game"] != streamstate["stream"]["game"]:
                    send("Nouveau jeu : "+streamstate["stream"]["game"])
                
            streamlast = streamstate["stream"]
            while streamlast == streamstate["stream"] and pause == 0 and stop == 0:
                time.sleep(5)

def newchat():
        #try:
            global chatnb
            global dejavu
            chatlt = 0
            while stop == 0:
                time.sleep(1)
                while pause == 0:
                    if chatnb != chatlt:
                        if chatnb > chatlt:
                            send("[" + str(chatnb) + " viewers (+" + str(chatnb - chatlt) + ")]")
                        elif chatnb < chatlt:
                            send("[" + str(chatnb) + " viewers (" + str(chatnb - chatlt) + ")]")
                        else:
                            send("[" + str(chatnb)+" viewers (=)]")
                    chatlt = chatnb
                    tempnew = []
                    if len(users) != 0:
                      for i in users:
                        if not i.encode("utf8") in dejavu:
                            dejavu.append(i.decode("utf8"))
                            tempnew.append(i)
                            send("/w "+i+" Bienvenue sur le stream d'elemzje. N'hesite pas à follow la chaine si ça te plait :) Sache aussi que ce compte est à la fois un bot et un humain ;) Je suis ouvert a toutes modifications sur le bot, propose moi ce qui te passes par la tete ;)")
                            time.sleep(0.3)
                    if len(tempnew) > 0:
                        send("Bienvenue à "+", ".join(tempnew)+", nouveau(x) sur le chat.")
                        savejson
                    for i in range(0, 300, 5):
                        time.sleep(5)
                        if stop != 0 or pause != 0:
                            break
        #except Exception, e:
        #    print("Probleme dans \"newchat\"" + str(e))
        #    pass

def recurrence():
        try:
            while stop == 0:
                time.sleep(1)
                while pause == 0 and stop == 0:
                    send(recurrenceMessages[random.randint(0, len(recurrenceMessages)-1)].encode("utf-8"))
                    for i in range(0, 300, 5):
                        time.sleep(3)
                        if pause == 0 or stop == 0:
                            channelInfo()
                            streaminfo()
                        else:
                            break
                print("reccurence en pause")
            print("fin de reccurence")
        except Exception, e:
            print("reccurence: " + str(e))
            pass
    
def send(Message):  # Envoit de messages dans le Channel
        log("Le bot envoie : " + Message)
        if "/" in Message.split(" ")[0]:
            s.send("PRIVMSG " + CHANNEL + " :" + Message + "\r\n")  # envoie commande
            print("Commande : " + Message)
        else:
            s.send("PRIVMSG " + CHANNEL + " :/me _ MrDestructoid : " + Message + "\r\n")  # envoie message
            print("Envoyé : " + Message)

if 1:
    #Variables pour fonctions
    jsoninfo = open("info.json", "r")
    infojson = json.load(jsoninfo)
    jsoninfo.close()
    del jsoninfo
    quotes = infojson[u'quotes']
    recurrenceMessages = infojson[u'reccurence']
    dejavu = infojson[u'dejavu']
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

    lcd_i2c.main()
    logfile = open("log.txt", "a")
    logfile.write(time.ctime() + " $ " + "Nouvelle connexion \r\n")
    crashlog = open("crash.txt", "r")
    print(crashlog.read())
    crashlog.close
    connection()
    threading.Thread(target=recurrence).start()
    threading.Thread(target=newchat).start()
    threading.Thread(target=newstreaminfo).start()
    crashlog = open("crash.txt", "w")
    crashlog.write("Wipe au restart, le : " + time.strftime("%c"))
    crashlog.close
    channelInfo()

    arret = False
    try:
        while 1:
    
            text = ""
            user = ""
            recu = s.recv(2040)
            log(recu)
    
            if "PING" in recu:  # pong
                rep = recu.split(":")[1]
                s.send("PONG :" + rep + "\r\n")
                stop = False
                pause = False
    
            elif len(recu.split(":")) >= 3 and "PRIVMSG" in recu:  # séparation user/texte
                user = recu.split("!")[0]
                user = user.split(":")[1]
                text = recu.split("PRIVMSG "+CHANNEL+" :")[1].split("\r\n")[0]
                print(user + " : " + text)  # log
        
            elif "RECONNECT" in recu:
                1/0
            else:
                print("Recu :"+recu)
    
                ###______Commandes______###
    
            if "!quote" in text:
                if len(text.split(" ")) > 0:
                    quote = text.split(" ")[-1]
                else:
                    quote = text.split("quote")[-1]
                if "s" in quote:
                    send("Voici les quotes, pour en citer une, merci d'indiquer son numero : " + "\", \"".join(quotes))
                    pass
                else:
                    quote = quote.split("\r")[0]
                    if "quote" in quote:
                        send("veuillez indiquer quelle quote vous voullez")
                        pass
                    else:
                        try:
                            quote = int(quote)
                            send(quotes[quote].encode("utf8"))
                        except ValueError, e:
                            send("Veuillez entrer une valeur numerique (1, 2, 3, etc...) et non le contenu de la quote. Pour connaitre les quotes connues, tapez !quotes")
                            print(e)
                            pass
                        except IndexError, e:
                            send(
                            "Quote inconnue, tapez !quotes pour connaitre les quotes connues")
                            print(e)
                            pass
    
            if user == "lawry25" and lawry == True:
                send(Kappa)
                lcd_i2c.Afficher("Kappa  " + str(sel), "Vive mistercraft")
                if "stop kappa" in text:
                    lawry = False
            if "reKappa" in text:
                lawry = True
    
            if "salut" in text and "@mistercraft38" in text:
                send("sckHLT ations camarade !")
    
            if ((" vas " in text or " vas-" in text) and "comment" in text) and "@mistercraft38" in text:
                send("Je vais tres bien, merci... mais c'est de la triche: je suis un bot...")
    
#            if " c " in text and not ("ctrl" in text or "ctl" in text or "contr" in text or " c e" in text) and sel < 20:
#                if sel < 1:
#                    send("Evite d'ecrire \"c\"... Ce serait plus agreable que tu ecrives \"c\'est\", \"ces\", \"ses\" ou encore \"sait\" @" + user)
#                else:
#                    send("*\"c'est\" ou \"ces\" @" + user)
    
#            if " pa " in text and sel < 20:
#                if sel < 1:
#                    send("Met un \"s\" à la fin de \"pas\" STP @" + user+" c'est plus agréable ;)")
#                else:
#                    send("*pas @" + user)
    
#            if " t " in text and sel < 20 and not " t e" in text:
#                if sel < 1:
#                    send("Peux-tu ecrire \"t'es\", \"thé\" ( Kappa ) ou \"tes\" ? Ce serait plus agreable @" + user)
#                else:
#                    send("*\"t'es\" ou \"tes\" @" + user)

#            if " g " in text and sel < 20:
#                if sel < 1:
#                    send("Peux-tu ecrie \"j'ai\" en pleines lettres, c'est plsu joli :) @" + user)
#                else:
#                    send("*j'ai @" + user)

#            if " chai pa" in text and sel < 20:
#                if sel < 1:
#                    send("Je t'encourage à érire \"je ne sais pas\" ou \"je sais pas\" au lieu de \"chai pas\", en plus d'etre plus joli, ca fait mine d'etre plus eduqué @" + user)
#                else:
#                    send("*je ne sais pas @" + user)
    
#            if " etai " in text and sel < 20:
#                if sel < 1:
#                    send("Peux-tu rajouter le \"s\" ou le \"t\" à la fin de \"étai\" ? ( petit rappel au cas où:  Le \"s\" c'est pour la premiere et deuxieme personne du singulier (je/tu) et le \"t\" pour la troisieme personne (il/elle/on)) @" + user)
#                else:
#                    send("*étais ou était @" + user)
    
#            if " bi1 " in text and sel < 20:
#                if sel < 1:
#                    send("Franchement ? Prend l'habitude d'ecrire correctement... \"bi1\" c'est optimisé pour les claviers T9, pas azerty, et sauf erreur, le 3310 n'est pas compatible avec twitch... Desolé pour la violence, mais ça m'insupporte... @" + user)
#                else:
#                    send("*bien @" + user)
   
#            if " tro " in text and sel < 20:
#                if sel < 1:
#                    send("Il y a un \"p\" à la fin de \"trop\". @" + user)
#                else:
#                    send("*trop @" + user)
    
#            if " g etai " in text:
#                send("BON DIEU ! Rassure-moi, tu fait expres ? @" + user +" ca me ferai mal au cœur de savoir que quelqu'un aie une telle ignorance de l'existance du beschrelle")
#    
#            if " ct " in text and sel < 20:
#                if sel < 1:
#                    send("Tu peux t'appliquer s'il te plait ? C'est pas non plus super long d'ecrire \"c'était\" en toutes lettres, et c'est beaucoup plus agreable pour les personnes qui te lisent... Cependant, si tu ecrivais sur un clavier T9, je te pardonnerais... mais bon, Twitch n'existe pas sur 3310... @" + user)
#                else:
#                    send("*c'était @" + user)
    
            if ("blg" or "BLG" or "beluga" or "Beluga" or "béluga" or "Béluga") in text:
                send("sckBLG sckBLG sckBLG")
    
            if ("HLT" in text or "salut" in text) and user != "mistercraft38":
                send("sckHLT @" + user)
    
            if "!to " in text and user in modos:
                print('to')
                if "!to" in text.split(" ")[0] and len(text.split(" ")) > 2:
                    send("/timeout " + text.split(" ")
                         [1] + " " + text.split(" ")[2])
    
            if user == "wizebot" and wiz == 0:
                send("bonjour @wizebot je viens en paix, pour ne pas t'assister. Je serai present ici pour te faire souffrir.")
                wiz = 1
    
            if "!team" in text.split(" ")[0]:
                send("Elemzje fait partis de la team des 9L (9Lives), une team de full sckBGT")
    
            if "!twitter" in text and len(text.split(" ")) < 2:
                send("Bon... nightbot vas te donner le twitter d'@elemzje , donc le mien c'est @ mistercraft385 ;)")
    
            if "!au revoir" in text and (user == "mistercraft38" or "elemzje" or "lawry25"):
                print("au revoir")
                send("/me Sur demande de @" + user +
                     " votre bot bien aimé s'en vas... au revoir. sckHLT ;) ")
                wiz = 0
                pause = True
                lcd_i2c.Afficher("Pause du bot", str(sel))
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
                send("/me Votre bot préféré ( Kappa ) est de retour !!! Merci à @" +
                     user + " pour avoir aidé le phoenix à renaitre de ses cendres")
    
            if "!config" in text and len(text.split(" ")) < 2:
                send("Tu sais que c'est marqué dans la description de la chaine ? Bon aller, vus que je suis gentil: ")
                send("MONITOR : BenQ XL2411Z (144 Hz ! OMG!!!), HEADSET : HYPER X CLOUD II, MOUSE : STEELSERIES Rival (la 1ere), MOUSEPAD : STEELSERIES Qck Heavy (lol j'ai le même Kappa ), KEYBOARD : STEELSERIES APEX M800, MB : ASUS H81-PLUS, CPU : INTEL i5-4690, GPU : MSI GTX 970 4GB (j'ai 2x moins de vram mais bon... j'ai une 750Ti...), HDD : SEAGATE Barracuda 1 To, SDD : SEAGATE 250 Go (riche...), RAM : 2 x 4 Go CORSAIR Vengeance, PSU : CORSAIR 550W.")
    
            if "!pseudo" in text and len(text.split(" ")) < 2:
                send("il était une fois, dans une lointaine contrée naz.. eu non.. il  était une fois, en alsace, un jeune CM1 prénomé Bryan (brillant... LOL). Lors d'une journée d'orage, il jouait avec ses amis. Il jouais au foot. L'orage n'etait pas habituel (ciel violet, pluie fine et tout le tralala). ...")
                send("... Avec ses amis, ils s'amusaient à dire \"les elements se dechainent, les elements se déchainent\", ensuite, en classe, ils continuaient avec les elements, leur maîtresse dit \"oui bien l'element, il vas se calmer\". Depuis, element,est resté et s'est transformé en @elemzje. \"zje\" étant là uniquement, je cite, \"pour faire chier les gens\".")
    
            if ("!saler" or "!sale" or "!salé") in text:
                sel = sel + 50
                grains = grains + 50
                send("Le niveau de PJSalt est reglé à " + str(sel))
                if grains > 1000:
                    grains = grains - 50
                lcd_i2c.AfficherLine("Sel: " + str(sel), "Vive mistercraft")
    
            if "!sel" in text:
                send("Le niveau de PJSalt actuel est de " + str(sel))
                lcd_i2c.AfficherLine("Sel: " + str(sel), "Vive mistercraft")
    
            if ("!sucre" or "!sucré" or "!sucrer") in text:
                sel = sel - 50
                grains = grains + 50
                send("Le niveau de PJSalt est reglé à " + str(sel))
                if grains > 1000:
                    grains = grains - 50
                lcd_i2c.AfficherLine("Sel: " + str(sel), "Vive mistercraft")
    
            if (" con " or " merde " or " chiant ") in text:
                sel = sel + 1
                if "Kappa" in text or "<3" in text:
                    sel = sel - 6
                    grains = grains - 5
                elif "mistercraft" in text:
                    sel = sel + 10
                grains = grains + 1
                print(str(sel))
                if grains > 1000:
                    send("c'est le grain de sel de @" + user +
                         " qui fait déborder le vase... sel reinitialisé à 20")
                    sel = 20
                lcd_i2c.AfficherLine("Sel: " + str(sel), "Vive mistercraft")
    
            if (" amour " or " aime " or "<3" or "Kappa") in text:
                sel = sel - len(text.split("Kappa"))
                sel = sel - len(text.split("<3"))
                sel = sel - 2
                print(str(sel))
                grains = grains + 2
                if grains > 1000:
                    send("c'est le grain de sucre de @" + user +
                         " qui fait déborder le vase... sel reinitialisé à -20")
                    sel = -20
                lcd_i2c.AfficherLine("Sel: " + str(sel), "Vive mistercraft")
    
            if "!refresh" in text.split(" ")[0]:
                refreshjson()
    
            if "!addquote" in text.split(" ")[0] and len(text.split(" ")) > 1:
                global quotes
                quote = ""
                quote = text.split("!addquote ")[1]
                quotes.append(quote.decode('utf8'))
                savejson()
                send("Quote enregistrée comme quote n°" + str(len(quotes)))
                log("Quote n°" + str(len(quotes)) + " Quote : " + quote)
                print("New quote (n°" + str(len(quotes)) + ") = " + quote)
                lcd_i2c.AfficherLine("New quote:" + quote[:6], quote[6:] + "...")
    
            if "!tauhazard" in text.split(" ")[0]:
                if len(users) == 0:
                    pass
                else:
                    channelInfo()
                    send("Tirage au sort d'un personne à timeout parmis les " + str(chatnb) + " personnes presentes dans le chat...")
                    to = len(users)
                    to = random.randint(0, to)
                    to = users[to]
                    send(to + " a été tiré au sort pour un to de 100 secondes. Un dernier mot ? tu as 10 secondes...")
                    time.sleep(10)
                    send("/timeout " + to + " 100")
                    send("Au plaisir @" + to)

            if "!git" in text.split(" ")[0]:
                send("Voici le lien du git-hub du code du bot, ce dernier est mis a jour environ une a deux fois par semaine, suivant ce que je peux lui apporter: https://github.com/Mistercraft38/twitch-bot")
    
    except KeyboardInterrupt:
        stop = True
        pause = True
        send("/disconnect")
        savejson
        print("En attente de la fin des threads...")
        for i in range(0, 5):
            time.sleep(1)
            print('.')
        log("Extinction du Bot: KeyboardInterrupt \r\n")
        lcd_i2c.Afficher("KeyboardInterrupt", "fin")
        
    except ZeroDivisionError:
        savejson
        stop = True
        pause = True
        pass

    except Exception, e:
        print(str(e))
        log(time.ctime() + " $ " + "Crash : " + str(e))
        send("Ce robot a crash... Merci d'en informer son créateur... J'AI ENVIE D'ETRE UN BOT SANS BUG !!! Erreur : " + str(e))
        send("/disconnect")
        savejson
        crashlog = open("crash.txt", "a")
        crashlog.write(time.strftime("%c") + " : " + str(e))
        crashlog.close
        log(str(e))
        lcd_i2c.Afficher("Bug:" + str(e))
        stop = True
        pause = True
        arret = True

    finally:
        stop = True
        pause = True
        log("Fin de l'execution/fin du log \r\n \n")
        logfile.close
