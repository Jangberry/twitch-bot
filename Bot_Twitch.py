#-*- coding: utf-8 -*-
import socket
import sys
import time
import threading
import random
import urllib
import json
import importlib
import lcd_i2c
from info import CHANNEL, PASS, NICK

global lol
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
            infos = urllib.urlopen("https://tmi.twitch.tv/group/user/" + CHANNEL.split("#")[1] + "/chatters")
            infos = json.loads(infos.read())
            users = infos["chatters"]["viewers"]
            # print(str(users))
            modos = infos["chatters"]["moderators"] + infos["chatters"]["global_mods"] + infos["chatters"]["staff"] + infos["chatters"]["admins"]
            # print(str(modos))
            chatnb = infos["chatter_count"]
            if len(infos["chatters"]["staff"])>0:
                send("OMG !!! There is someone from the twitch's staff ?!? Welcome @"+infos["chatters"]["staff"][0])
    
        except Exception, e:
            print("channelInfo : " + str(e))
            pass
    
    
def newchat():
        try:
            global chatnb
            global dejavu
            chatlt = 0
            while stop == 0:
                while pause == 0:
                    if chatnb != chatlt:
                        if chatnb > chatlt:
                            send("[" + str(chatnb) + " viewers (+" + str(chatnb - chatlt) + ")]")
                        elif chatnb < chatlt:
                            send("[" + str(chatnb) + " viewers (" + str(chatnb - chatlt) + ")]")
                    chatlt = chatnb
                    if len(users) > 0:
                        nouveaux = []
                        for i in range(0, len(users)-1):
                            if users[i] not in dejavu:
                                dejavu.append(users[i].decode("utf8"))
                                nouveaux.append(users[i])
                            else:
                                sleep(0.001)
                        print(str(nouveaux))
                        if len(nouveaux) > 0:
                            send("Bienvenue à "+str(nouveaux).split("[")[-1].split("]")[0]+", nouveau(x) sur le chat. Si le stream vous plait, n'hesitez pas a follow la chaine")
                            for i in range(0, len(nouveaux)-1):
                                savejson()
                    for i in range(0, 300, 5):
                        time.sleep(5)
                        if stop != 0 or pause != 0:
                            break
            exit()
        except Exception, e:
            print("Probleme dans \"newchat\"" + str(e))
            pass
    
    
def recurrence():
        try:
            while stop == 0:
                time.sleep(1)
                while pause == 0 and stop == 0:
                    send(recurrenceMessages[random.randint(0, len(recurrenceMessages)-1)].encode("utf-8"))
                    for i in range(0, 1300, 10):
                        if pause == 1 or stop == 1:
                            break
                        else:    
                            try:
                                channelInfo()
                            except TypeError:
                                pass
                        if pause == 1 or stop == 1:
                            break
                        time.sleep(4)
                        if pause == 1 or stop == 1:
                            break
                        time.sleep(4)
            exit()
        except Exception, e:
            print("reccurence: " + str(e))
            exit()
    
def send(Message):  # Envoit de messages dans le Channel
        log("Le bot envoie : " + Message)
        if "/" in Message.split(" ")[0]:
            s.send("PRIVMSG " + CHANNEL + " :" + Message + "\r\n")  # envoie commande
            print("Commande : " + Message)
        else:
            s.send("PRIVMSG " + CHANNEL + " :/me _ MrDestructoid : " + Message + "\r\n")  # envoie message
            print("Envoyé : " + Message)

if 1:
     # Variables pour fonctions
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

    lcd_i2c.main()
    logfile = open("log.txt", "a")
    logfile.write(time.ctime() + " $ " + "Nouvelle connexion \r\n")
    crashlog = open("crash.txt", "r")
    print(crashlog.read())
    crashlog.close
    connection()
    threading.Thread(target=recurrence).start()
    threading.Thread(target=newchat).start()
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
                    quotesstr = ""
                    for i in range(0, len(quotes) - 1):
                        quotesstr = quotesstr + " " + str(i)+ " :\"" + quotes[i].encode("utf8") + "\""
                    send("Voici les quotes, pour en citer une, merci d'indiquer son numero : " + quotesstr)
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
    
            if " c " in text and not ("ctrl" in text or "ctl" in text or "contr" in text) and sel < 20:
                if sel < 1:
                    send("On n'écrit pas \"c\" quand on parle français... on écrit \"c\'est\", \"ces\", \"ses\" ou encore \"sait\" @" + user)
                else:
                    send("*\"c'est\" ou \"ces\" @" + user)
    
            if " pa " in text and sel < 20:
                if sel < 1:
                    send("On met un \"s\" à la fin de \"pas\" @" + user)
                else:
                    send("*pas @" + user)
    
            if " t " in text and sel < 20:
                if sel < 1:
                    send(
                        "On n'écrit pas \"t\" quand on parle francais... on écrit \"t'es\", \"thé\" ou \"tes\" @" + user)
                else:
                    send("*\"t'es\" ou \"tes\" @" + user)

            if " g " in text and sel < 20:
                if sel < 1:
                    send(
                        "On dis pas \"g\" quand on parle francais, on ecrit \"j'ai\" @" + user)
                else:
                    send("*j'ai @" + user)

            if " chai pas " in text and sel < 20:
                if sel < 1:
                    send(
                        "Le savais-tu: souvent, on n'utilise pas le meme language à l'ecrit et a l'oral. C'est pour ca que je t'encourage à érire \"je ne sais pas\" au lieu de \"chai pas\" (en plus ca fait un peu plus eduqué) @" + user)
                else:
                    send("*je ne sais pas @" + user)
    
            if " etai " in text and sel < 20:
                if sel < 1:
                    send("À l'imparfait, le verbe \"être\" se conjugue \"étais\" à la premiere et à la seconde personne du singulier et \"etait\" à la troisieme personne. Apres si tu voulais mettre une personne du pluriel, t'es mal barré, car meme en phonetique ca ne s'ecrit pas comme ca... Sinon, son participe passé s'ecrit \"été\", comme la saison, mais je ne viendrai pas te faire chier si tu oublie les accents ;) @" + user)
                else:
                    send("*étais ou était @" + user)
    
            if " bi1 " in text and sel < 20:
                if sel < 1:
                    send("Serieux ? Le langage sms c'est pour les claviers T9... pas azerty, et sauf information contraire, tu ne regarde pas le stream sur un 3310 @" + user)
                else:
                    send("*bien @" + user)
    
            if " tro " in text and sel < 20:
                if sel < 1:
                    send("Il y a un \"p\" à la fin de \"trop\". @" + user)
                else:
                    send("*trop @" + user)
    
            if " g etai " in text:
                send("BON DIEU ! Rassure-moi, tu fait expres ? @" + user +" ca me ferai mal au cœur de savoir que quelqu'un aie une telle ignorance de l'existance du beschrelle")
    
            if " ct " in text and sel < 20:
                if sel < 1:
                    send("Mouaif... j'ai vus mieux en terme d'orthographe... tu sais ce n'est pas si long de taper \"c'était\" en toutes lettre, ca t'entraines même à la dyctalographie... tres utile de nos temps, crois-moi @" + user)
                else:
                    send("*c'était @" + user)
    
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
    
            if "!tauhazard" in text:
                if len(users) == 0:
                    pass
                else:
                    channelInfo()
                    send("Tirage au sort d'un personne à timeout parmis les " + str(chatnb) + " personnes presentes dans le chat...")
                    to = users[random.randint(0, len(users) - 1)]
                    send(to + " a été tiré au sort pour un to de 100 secondes. Un dernier mot ? tu as 10 secondes...")
                    time.sleep(10)
                    send("/timeout " + to + " 100")
                    send("Au plaisir @" + to)
    
    except KeyboardInterrupt:
        stop = True
        pause = True
        send("/disconnect")
        print("En attente de la fin des threads...")
        for i in range(0, 5):
            time.sleep(1)
            print('.')
        log("Extinction du Bot: KeyboardInterrupt \r\n")
        lcd_i2c.Afficher("KeyboardInterrupt", "fin")
    
    except DivisionByZero:
        pass

    except Exception, e:
        print(str(e))
        log(time.ctime() + " $ " + "Crash : " + str(e))
        send("Ce robot a crash... Merci d'en informer son créateur... J'AI ENVIE D'ETRE UN BOT SANS BUG !!! Erreur : " + str(e))
        send("/disconnect")
        crashlog = open("crash.txt", "a")
        crashlog.write(time.strftime("%c") + " : " + str(e))
        crashlog.close
        log(str(e))
        lcd_i2c.Afficher("Bug:" + str(e))
        stop = True
        pause = True
        arret = True

    finally:
        global lol
        stop = True
        pause = True
        log("Fin de l'execution/fin du log \r\n \n")
        logfile.close
        if arret:
            exit()
        else:
            lol = 1