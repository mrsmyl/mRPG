#!/usr/bin/env python

# mRPG
# https://github.com/mozor/mRPG
#
# Copyright 2012 Greg (NeWtoz@mozor.net) & Richard (richard@mozor.net);
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task
from twisted.python import log
from twisted.enterprise import adbapi
import time, sys
import ConfigParser

# Global Variables
timespan = 10.0 # TODO This should be in the config file
min_time = 30 # TODO This should be in the config file
penalty_constant = 1.1 # TODO This should be in the config file
is_started = 0

class mrpg:
    def __init__(self, parent):
        self.parent = parent
        self.channel = parent.factory.channel
        self.l = task.LoopingCall(self.rpg)
        self.db = DBPool('mrpg.db')
        self.db.mrpg = self

    def start(self):
        self.msg("Starting mrpg")
        self.msg("Please standby")

        # Start the reactor task that repeatedly loops through actions
        self.l.start(timespan)
        global is_started
        is_started = 1
        self.msg("Initialization complete")

    def stop(self):
        self.msg("I think my loop needs to stop")
        self.l.stop()
        global is_started
        is_started = 0
        self.msg("It stopped")

    def msg(self, msg):
        self.parent.msg(self.channel, msg)

    def performPenalty(self, user, reason):
        if is_started == 1:
            #commented out due to the spam it creates in IRC and just make it print to console
            self.msg(user + " has earned a penalty for: " + reason)
            self.db.updateUserTimeMultiplier(user, penalty_constant)
            self.db.getSingleUser(user)

    def rpg(self):
        self.db.updateAllUsersTime(timespan * -1)

        self.db.levelUp()

        # self.db.getAllUsers()

        # self.db.shutdown("")


class DBPool:
    """
        Sqlite connection pool
    """
    def __init__(self, dbname):
        self.dbname = dbname
        self.__dbpool = adbapi.ConnectionPool('sqlite3', self.dbname, check_same_thread=False)

    def shutdown(self, callback_msg):
        """
            Shutdown function
            It's a required task to shutdown the database connection pool:
                garbage collector doesn't shutdown associated thread
        """
        self.__dbpool.close()

    def getSingleUser(self, user):
        query = "SELECT * FROM users WHERE username = ?"
        s = self.__dbpool.runQuery(query, (user,)).addCallback(self.showUser)

    def getAllUsers(self):
        query = "SELECT * FROM users WHERE online = 1"
        s = self.__dbpool.runQuery(query).addCallback(self.showUser)

    def showUser(self, output):
        for i in output:
            message = str(i[1]) + " will reach the next level in " + str(i[4]) + " seconds."
            self.mrpg.msg(message)
            print message

    def levelUp(self):
        query = "SELECT username, level, ttl FROM users WHERE ttl < 0 AND online = 1"
        s = self.__dbpool.runQuery(query).addCallback(self.showLevelUp)

    def showLevelUp(self, output):
        for i in output:
            user = str(i[0])
            level = int(i[1])

            new_level = level + 1
            ttl = min_time * new_level

            message = user + " has reached level " +str(new_level)
            self.mrpg.msg(message)
            message = user + " will reach the next level in " +str(ttl) + " seconds"
            self.mrpg.msg(message)
            self.levelUpUser(user, level)
            print user + " has reached level " +str(new_level)


    def getResults(self, output):
        return output

    def executeQuery(self, query, args):
        return self.__dbpool.runQuery(query, args)

    def levelUpUser(self, user, level):
        new_level = level + 1
        ttl = min_time * new_level
        return self.__dbpool.runQuery("UPDATE users SET ttl = ?, level = ? WHERE username = ?", (ttl, new_level, user, ))

    def updateUserTime(self, user, amount):
        return self.__dbpool.runOperation("UPDATE users SET ttl = ttl + ? WHERE username = ?", (amount, user,))

    def updateUserTimeMultiplier(self, user, amount):
        return self.__dbpool.runOperation("UPDATE users SET ttl = ROUND(ttl * ?,0) WHERE username = ?", (amount, user,))

    def updateAllUsersTime(self, amount):
        return self.__dbpool.runOperation("UPDATE users SET ttl = ttl + ? WHERE online = 1", (amount,))

    def register_user(self, reg_username, reg_password, reg_char_class):
        query = 'INSERT INTO `users` (id,username,password,level,ttl,char_class,hostname,online) VALUES (NULL,?,?,1,?,?,NULL,1)'
        return self.__dbpool.runQuery(query, (reg_username, reg_password, min_time, reg_char_class))


class Bot(irc.IRCClient):
    """A logging IRC bot."""

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.mrpg = mrpg(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        self.nickservIdentify()

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.mrpg.start()

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            # msg_out = "It isn't nice to whisper!  Play nice with the group."
            #self.notice(user, msg_out)
            #self.msg(self.factory.channel, msg)
            if msg.lower() == "register":
                self.notice(user, "To register: /msg mBot register <char name> <password>  <char class>")
            else:
                msg_split = msg.split(' ')
                #ASOLUTELY NO ERROR CORRECTION YET!!
                if msg_split[0] == "register":
                    reg_username = msg_split[1]
                    reg_password = msg_split[2]
                    reg_char_class = msg_split[3::1]
                    reg_char_class = ' '.join(reg_char_class)
                    self.db = DBPool('mrpg.db')
                    self.db.register_user(reg_username,reg_password,reg_char_class)
                    self.db.shutdown("")
                    self.notice(user, "Created new character " + reg_username)
        else:
            self.mrpg.performPenalty(user, "channel message")

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg_out = "%s: I am a log bot" % user
            self.msg(channel, msg_out)
            self.msg(channel, msg)
            if "shutdown" in msg:
                self.mrpg.stop()
            if "startup" in msg:
                self.mrpg.start()

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.mrpg.performPenalty(user, "Channel action")

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.mrpg.performPenalty(new_nick, "Nickname change")

        # TODO Issue #3 - Track user nickname change

    def nickservRegister(self):
        self.msg("nickserv", "register " + self.factory.nickserv_password + " " + self.factory.nickserv_email)

    def nickservIdentify(self):
        self.msg("nickserv", "identify " + self.factory.nickserv_password)
class BotFactory(protocol.ClientFactory):
    """A factory for Bots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')

        channel = config.get('IRC', 'channel')
        nickname = config.get('IRC', 'nickname')

        self.channel = config.get('IRC', 'channel')
        self.nickname = config.get('IRC', 'nickname')
        self.nickserv_password = config.get('IRC', 'nickserv_password')
        self.nickserv_email = config.get('IRC', 'nickserv_email')

    def buildProtocol(self, addr):
        p = Bot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    server = config.get('IRC', 'server')
    port = config.getint('IRC', 'port')

    # create factory protocol and application
    f = BotFactory()

    # connect factory to this host and port
    reactor.connectTCP(server, port, f)

    # run bot
    reactor.run()








# These two definitions will be used later for passwords.
# So ignore this for now

#def set_password(self, raw_password):
#    import random
#    algo = 'sha1'
#    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
#    hsh = get_hexdigest(algo, salt, raw_password)
#    self.password = '%s$%s$%s' % (algo, salt, hsh)

#def check_password(raw_password, enc_password):
#    """
#    Returns a boolean of whether the raw_password was correct. Handles
#    encryption formats behind the scenes.
#    """
#    algo, salt, hsh = enc_password.split('$')
#    return hsh == get_hexdigest(algo, salt, raw_password)

