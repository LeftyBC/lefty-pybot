#!bin/python

from sys import stdin
from sys import exit

import logging

from ConfigParser import SafeConfigParser

from select import select

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

from cmd import Cmd

privmsg_handlers = []
channelmsg_handlers = []
command_handlers = []

config = None

# == commandline interface
class Cmdline(Cmd):
    def do_say(self, raw):
        (channel, message) = raw.split(" ",1)
        helpers.msg(cli,channel,message)

    def do_exit(self, message):
        print "Shutting down the bot."
        exit()

# == end commandline interface

# == irc bot interface
def connect_callback(cli):
    for CHANNEL in CHANNELS:
        helpers.join(cli, CHANNEL)

class BotLogic(DefaultCommandHandler):

    COMMAND_PREFIX = '!'
    # Handle messages
    def privmsg(self, nick, chan, msg):
        global privmsg_handlers
        print "Handling privmsg event: %s in %s said: %s" % (nick, chan, msg)
        if chan == NICK:
            # this is a private message
            print "Private message recieved: %s" % msg
            for handler in privmsg_handlers:
                try:
                    handler(self.client, nick, msg)
                except Exception as e:
                    print "Private message handler failed: %s" % (handler, e)
        else:
            if msg[0] == self.COMMAND_PREFIX:
                # this is a bot command
                print "Bot command recieved from %s in %s: %s" % (nick,chan,msg)

                cmd = ""
                args = ""
                try:
                    (cmd,args) = msg[1:].split(" ",1)
                except ValueError as e:
                    cmd = msg[1:]

                for handler in command_handlers:
                    try:
                        handler(self.client, nick, chan, cmd, args)
                    except Exception as e:
                        print "Command handler %s failed: %s" % (handler, e)
            else:
                # this is just a raw line
                print "Public message recieved from %s in %s: %s" % (nick,chan,msg)
                for handler in channelmsg_handlers:
                    try:
                        handler(self.client, nick, chan, msg)
                    except Exception as e:
                        print "Pubmsg handler %s failed: %s" % (handler, e)

# == end irc bot interface
def prompt():
    print "bot> ",


# == message handlers

def reload_handlers():
    global privmsg_handlers, channelmsg_handlers, command_handlers
    import handlers

    privmsg_handlers = []
    channelmsg_handlers = []
    command_handlers = []

    privmsg_handlers.append(handlers.echo)
    privmsg_handlers.append(handlers.whoami)

    command_handlers.append(handlers.uppercase)
    command_handlers.append(handlers.hackers_cmd)

    channelmsg_handlers.append(handlers.regex)
    channelmsg_handlers.append(handlers.hackers_pub)

# == end message handlers

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    CHANNELS = [ '#leftytest', '#leftytest2' ]

    reload_handlers()

    defaults = { 'server':'localhost',
                'port':6667,
                'nick':'UnnamedBot', }

    config = SafeConfigParser(defaults)
    config.read('irc.ini')

    IRCHOST=config.get('main','server')
    PORT=int(config.get('main','port'))
    NICK=config.get('main','nick')

    # == init handlers
    cli = IRCClient(BotLogic,
                    host=IRCHOST, port=PORT, nick=NICK,
                    connect_cb=connect_callback)

    cmdline = Cmdline()
    # == end init handlers

    # connect, let the bot loop
    conn = cli.connect()

    prompt()
    while True:
        # process any irc messages
        conn.next()

        # process any commandline messages
        timeout = 0.05
        rlist, _, _ = select([stdin], [], [], timeout)
        if rlist:
            userin = stdin.readline()
            if (userin != ""):
                try:
                    cmdline.onecmd(userin)
                except Exception as e:
                    print "Command [%s] failed: %s" % (userin.rstrip(),e)
                    prompt()
