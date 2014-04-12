import re
from random_line import random_line_from_file

from oyoyo import helpers

history = {}
MAXHISTORY = 10

def get_nick(fullnick):
    return fullnick.split("!",1)[0]

def echo(client, nick, message):
    if message.lower() == "ping":
        helpers.msg(client, nick, "pong")

def whoami(client, nick, message):
    if message.lower() == "whoami":
        helpers.msg(client, nick, "you are %s, I think." % nick)

def uppercase(client, nick, chan, cmd, args):
    if cmd.lower() == "upper" and len(args) > 0:
        helpers.msg(client, chan, args.upper())

def regex(client, nick, chan, message):
    matches = re.match("^s/(.*)/(.*)/(i?)$",message)
    if matches:
        for nick,item in reversed(history[chan]):
            flags = 0
            for flag in matches.group(3):
                flag = flag.lower()
                if flag == "i":
                    flags = flags | re.I

            (replaced,subs) = re.subn(matches.group(1),matches.group(2),item,flags)
            if subs > 0:
                helpers.msg(client,chan,"<%s> %s" % (get_nick(nick),replaced))
                break
    else:
        print "not a regex, pushing to history"
        if chan not in history:
            history[chan] = []
        history[chan].append( (nick,message) )
        if len(history[chan]) > MAXHISTORY:
            history[chan].pop(0)

def hackers_cmd(client, nick, chan, cmd, args):
    if cmd.lower() == "hackers":
        line = random_line_from_file("hackers.txt")
        helpers.msg(client,chan,line)

def hackers_pub(client, nick, chan, message):
    if "hackers" in message.lower():
        line = random_line_from_file("hackers.txt")
        helpers.msg(client, chan, line)

