#!/usr/bin/env python

# mRPG
# https://github.com/mozor/mRPG
#
# Copyright 2012 Greg (NeWtoz@mozor.net) & Richard (richard@mozor.net);
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task
from twisted.python import log
from twisted.enterprise import adbapi
# from twisted.internet.defer import DeferredList

# system imports
import time, sys
import ConfigParser

timespan = 10.0
min_time = 30
is_started = 0

def printResult(result):
	for r in result:
		print(r[1])

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
			#self.msg(user + " has earned a penalty for: " + reason)
			print "Penalty"

	def rpg(self):
		#commented out due to the spam it creates in IRC and just make it print to console
                print "10 second loop"
		#self.msg("This is the looping call that will do stuff")
		
		
		# self.db.register_user("richard", "abc123", "Captain Awesome")
		# self.db.register_user("newtoz", "abc123", "Super Sleuth")
		# self.db.register_user("george", "abc123", "not a george")
		# self.db.register_user("moo", "abc123", "cow")
		self.db.updateAllUsersTime(timespan * -1)
		
		# s = self.db.executeQuery("SELECT ttl FROM users WHERE username = ?", ("richard",))
		# s = s.addCallback(self.db.getResults)
		# print s
		
		self.db.levelUp()
		
		self.db.getUser()
		
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

	def getUser(self):
		query = "SELECT * FROM users"
		s = self.__dbpool.runQuery(query).addCallback(self.showUser)
	
	def showUser(self, output):
		for i in output:
			message = str(i[1]) + " will reach the next level in " + str(i[4]) + " seconds."
			# self.mrpg.msg(message)
			print message

	def levelUp(self):
		query = "SELECT username, level, ttl FROM users WHERE ttl < 0"
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
		return self.__dbpool.runQuery("UPDATE users SET ttl = ttl + ? WHERE username = ?", (amount, user,))

	def updateAllUsersTime(self, amount):
		return self.__dbpool.runQuery("UPDATE users SET ttl = ttl + ?", (amount,))

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
		"""This will get called when the bot sees someone do an action."""
		user = user.split('!', 1)[0]

	# irc callbacks

	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		old_nick = prefix.split('!')[0]
		new_nick = params[0]


	# For fun, override the method that determines how a nickname is changed on
	# collisions. The default method appends an underscore.
	def alterCollidedNick(self, nickname):
		"""
		Generate an altered version of a nickname that caused a collision in an
		effort to create an unused related name for subsequent registration.
		"""
		return nickname + '^'

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
		
		# self.db = DBPool('mrpg.db')
		
		# DeferredList seems more adapted than chained callbacks in this sort of cases
		# ret_render = lambda user: user.render()
		# deferreds = [self.db.get_user_user(username).addCallback(ret_render)
		# 						for username in ('richard','newtoz')]

		# dlist = DeferredList(deferreds)
		# dlist.addCallback(printResult)
		# We ask our pool to shutdown all the initialized connections
		# dlist.addCallback(self.db.shutdown)





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

