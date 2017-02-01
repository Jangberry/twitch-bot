#-*- coding: utf-8 -*-
import socket
import sys
import time
import threading
import random
from info import CHANNEL, PASS, NICK
import lcd_i2c

s = socket.socket()

#Variables pour fonctions
FichierQuotes = open("quotes.txt", "r")
wiz = 0
sel = -20
grains = 0
pause = False
stop = False
recurrenceMessages = ["Vous pouvez suivre @elemzje sur twitter: https://twitter.com/Elemzje", "Vous pouvez a tout moment ajouter le smurf d'@elemzje: lmjye sur Uplay."]

def connection():  #Connection au serveur + channel
    print("connecting...")
    s.connect(("irc.chat.twitch.tv", 6667))
    print("identifing with nickname: "+NICK)
    s.send("PASS " + PASS + "\r\n")
    s.send("NICK " + NICK + "\r\n")
    print("joining channel " + CHANNEL)
    s.send("JOIN " + CHANNEL + "\r\n")
    print("Connected")

def recurrence():
    while stop == 0:
        time.sleep(1)
        while pause == 0 and stop == 0:
            send(recurrenceMessages[random.randint(0, len(recurrenceMessages)-1)])
            for i in range(0, 1000, 5):
                time.sleep(5)
                if pause == 1 or stop == 1:
                    break

def send(Message):   #Envoit de messages dans le Channel
    log.write(time.ctime() + " $ " + "Le bot envoie : " + Message)
    if "/" in Message.split(" ")[0]:
        s.send("PRIVMSG " + CHANNEL + " :" + Message + "\r\n")     #envoie commande
        print("Commande : " + Message)
    else:
        s.send("PRIVMSG " + CHANNEL + " :/me _ MrDestructoid : " + Message + "\r\n") #envoie message
        print("Envoyé : " + Message)

lcd_i2c.main()
lcd_i2c.Afficher("Connection...")
crashlog = open("crash.txt", "r")
print(crashlog.read())
crashlog.close
connection()
send("/me Le bot de l'enfer est de retour, cachez vous !!!")
threading.Thread(target=recurrence).start()
crashlog = open("crash.txt", "w")
crashlog.write("Wipe au restart, le : "+time.strftime("%c"))
crashlog.close
log = open("log.txt", "a")

try:
 while 1:

    text = ""
    user = ""
    recu = s.recv(2040)
    if len(recu.split(":")) >= 3:      #séparation user/texte
        user = recu.split("!")[0]
        user = user.split(":")[1]
        for i in range(2, len(recu.split(":")), 1):
            text = text + recu.split(":")[i] + ":"
        print(user+" : "+text)      #log
        log.write(time.ctime() + " $ " + user + " : " + text)
    elif "PING" in recu:        #pong
        rep = recu.split(":")[1]
        s.send("PONG :" + rep + "\r\n")
        print("Ping")

            ###______Commandes______###


    if "!quote" in text:
        if len(text.split(" "))>0:
            quote = text.split(" ")[-1]
        else:
            quote = text.split("quote")[1]
        if "s" in quote:
            pass
        else:
            quote = quote.split("\r")[0]
            if "quote" in quote:
             send("veuillez indiquer quelle quote vous voullez")
             pass
            else:
             quote = str(int(quote))
             quotes = FichierQuotes.read()
             quotes = quotes.split("#~"+quote)[0]
             quote = quotes.split("~#")[-1]
             send(quote)

    if user == "lawry25" and lawry == True:
    	send(Kappa)
    	if "stop kappa" in text:
    		lawry = False
    if "reKappa" in text:
    	lawry = True

    if " c " in text and not ("ctrl" in text or "ctl" in text or "contr" in text) and sel < 20:
        if sel < 1:
        	send("On n'écrit pas \"c\" quand on parle français... on écrit \"c\'est\", \"ces\", \"ses\" ou encore \"sait\" @"+user)
        else:
            send("*\"c'est\" ou \"ces\" @" + user)

    if " pa " in text and sel < 20:
    	if sel < 1:
    		send("On met un \"s\" à la fin de \"pas\" @"+user)
    	else:
    		send("*pas @" + user)

    if " t " in text and sel <20:
        if sel < 1:
        	send("On n'écrit pas \"t\" quand on parle francais... on écrit \"t'es\", \"thé\" ou \"tes\" @"+user)
        else:
            send("*\"t'es\" ou \"tes\" @"+user)

    if " g " in text and sel < 20:
        if sel < 1:
            send("On dis pas \"g\" quand on parle francais, on ecrit \"j'ai\" @"+user)
        else:
            send("*j'ai @" + user)
        
    if ("blg" or "BLG" or "beluga" or "Beluga" or "béluga" or "Béluga") in text:
        send("sckBLG sckBLG sckBLG")

    if ("HLT" in text or "salut" in text) and user != "mistercraft38":
        send("sckHLT @" + user)
        
    if "!to " in text and user == "mistercraft38":
        if "!to" in text.split(" ")[0] and len(text.split(" ")) == 3:
            send("/timeout " + text.split(" ")[1] + " " + text.split(" ")[2])

    if user == "wizebot" and wiz == 0:
        send("bonjour @wizebot je viens en paix, pour ne pas t'assister. Je serai present ici pour te faire souffrir.")
        wiz = 1

    if "!twitter" in text and len(text.split(" ")) < 2:
        send("Bon... nightbot vas te donner le twitter d'@elemzje , donc le mien c'est @ mistercraft385 ;)")

    if "!au revoir" in text and (user == "mistercraft38" or "elemzje" or "lawry25"):
        print("au revoir")
        send("/me Sur demande de @" + user + " votre bot bien aimé s'en vas... au revoir. sckHLT ;) ")
        wiz = 0
        pause = True
        while not "!bonjour" in text:
            text = ""
            recu = s.recv(2040)
            if len(recu.split(":")) >= 3:
                user = recu.split("!")[0]
                user = user.split(":")[1]
                for i in range(2, len(recu.split(":")), 1):
                    text = text + recu.split(":")[i] + ":"
                    print(user+" : "+text)
            elif "PING" in recu:
                rep = recu.split(":")[1]
                s.send("PONG :" + rep + "\r\n")
        pause = False
        send("/me Votre bot préféré ( Kappa ) est de retour !!! Merci à @"+user+" pour avoir aidé le phoenix à renaitre de ses cendres")
        
    if "!config" in text and len(text.split(" ")) < 2:
        send("Tu sais que c'est marqué dans la description de la chaine ? Bon aller, vus que je suis gentil: ")
        send("MONITOR : BenQ XL2411Z (144 Hz ! OMG!!!), HEADSET : HYPER X CLOUD II, MOUSE : STEELSERIES Rival (la 1ere), MOUSEPAD : STEELSERIES Qck Heavy (lol j'ai le même Kappa ), KEYBOARD : STEELSERIES APEX M800, MB : ASUS H81-PLUS, CPU : INTEL i5-4690, GPU : MSI GTX 970 4GB (j'ai autant de vram mais bon... j'ai une 750Ti...), HDD : SEAGATE Barracuda 1 To, SDD : SEAGATE 250 Go (riche...), RAM : 2 x 4 Go CORSAIR Vengeance, PSU : CORSAIR 550W.")
    
    if "!pseudo" in text and len(text.split(" ")) < 2:
        send("il était une fois, dans une lointaine contrée naz.. eu non.. il  était une fois, en alsace, un jeune CM1 prénomé Bryan (brillant... LOL). Lors d'une journée d'orage, il jouait avec ses amis. Cependant, avec ses amis, il jouais au foot. L'orage n'etait pas habituel (ciel violet, pluie fine et tout le tralala). ...")
        send("... Avec ses amis, ils s'amusaient à dire \"les elements se dechainent, les elements se déchainent\", ensuite, en classe, ils continuaient avec les elements, leur maîtresse dit \"oui bien l'element, il vas se calmer\". Depuis, element,est resté et s'est transformé en @elemzje. \"zje\" étant là uniquement, je cite, \"pour faire chier les gens\".")

    if ("!saler" or "!sale" or "!salé") in text:
        sel = sel+50
        grains = grains+50
        send("Le niveau de PJSalt est reglé à " + str(sel))
        if grains > 1000:
        	grains = grains - 50

    if "!sel" in text:
        send("Le niveau de PJSalt actuel est de " + str(sel))

    if ("!sucre" or "!sucré" or "!sucrer") in text:
        sel = sel-50
        grains = grains+50
        send("Le niveau de PJSalt est reglé à "+ str(sel))
        if grains > 1000:
            	grains = grains - 50

    if (" con " or " merde " or " chiant ") in text:
        sel = sel + 1
        if "Kappa" in text or "<3" in text:
        	sel = sel-6
        	grains = grains-5
        elif "mistercraft" in text:
        	sel = sel + 10
        grains = grains +1
        print(str(sel))
        if grains > 1000:
        	send("c'est le grain de sel de @" + user + " qui fait déborder le vase... sel reinitialisé à 20")
        	sel = 20
		
    if (" amour " or " aime " or "<3" or "Kappa") in text:
        sel = sel - len(text.split("Kappa"))
        sel = sel - len(text.split("<3"))
        sel = sel - 2
        print(str(sel))
        grains = grains + 2
        if grains > 1000:
        	send("c'est le grain de sucre de @" + user + " qui fait déborder le vase... sel reinitialisé à -20")
        	sel = -20
        	
    if "!refresh" in text.split(" ")[0]:
    	FichierQuotes.close
    	FichierQuotes = open("quotes.txt", "r")

    if "!addquote" in text.split(" ")[0] and len(text.split(" ")) > 2:
        quote = ""
        for i in range(1, len(text.split(" "))-1):
            quote = quote+str(text.split(" ")[i])+" "
        last = FichierQuotes.read()
        last = last.split("#~")[-1]
        last = int(last.split("\n")[0])
        FichierQuotes.close
        FichierQuotes = open("quotes.txt", "a")
        quote = quote.split("\r\n")[0]
        FichierQuotes.write("~#"+quote+"#~"+str(last+1)+"\n")
        FichierQuotes.close
        send("Quote enregistrée comme quote n°"+str(last+1))
        log.write(time.ctime() + " $ Quote n°"+str(last+1)+" Quote : "+quote)
        print("New quote = "+quote)
        FichierQuotes = open("quotes.txt", "r")


except KeyboardInterrupt:
    stop = True
    pause = True
    send("Votre bot bot préféré s'en vas sur demande imperative de son maitre suprême... Le bot reviendra potentiellement bientôt ;) sckHLT")
    send("/disconnect")
    print("En attente de la fin du thread recurrence...")
    log.write(time.ctime() + " $ Extinction du Bot: KeyboardInterrupt")
    exit()

except Exception, e:
    print(str(e))
    log.write(time.ctime() + " $ Crash : " + e)
    crashlog = open("crash.txt", "a")
    crashlog.write(time.strftime("%c")+" : "+e)
    crashlog.close
    send("Ce robot a crash... Merci d'en informer son créateur... J'AI ENVIE D'ETRE UN BOT SANS BUG !!! Mais je reste quand même, ne vous inquietez pas ;) ")
    pass

finally:
    log.close
    lcd_byte(0x01, LCD_CMD)