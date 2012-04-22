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
from twisted.enterprise.adbapi import ConnectionPool
from twisted.internet.defer import DeferredList

# system imports
import time, sys
import ConfigParser

timespan = 10.0

def printResult(result):
	for r in result:
		print(r[1])

class mrpg:
	def __init__(self, parent):
		self.parent = parent
		self.channel = parent.factory.channel
		self.l = task.LoopingCall(self.rpg)

	def start(self):
		self.msg("Starting mrpg")
		self.msg("Please standby")

		# Start the reactor task that repeatedly loops through actions
		self.l.start(timespan) # call every 10 seconds for now

		self.msg("Initialization complete")

	def stop(self):
		self.msg("I think my loop needs to stop")
		self.l.stop()
		self.msg("It stopped")

	def msg(self, msg):
		self.parent.msg(self.channel, msg)

	def performPenalty(self, user, reason):
		self.msg(user + " has earned a penalty for: " + reason)

	def rpg(self):
		self.msg("This is the looping call that will do stuff")
		self.db = DBPool('mrpg.db')
		self.db.update_user_time('richard',timespan * -1)
		self.db.shutdown("")

class User:
	def __init__(self, username, char_class, password):
		self.username = username
		self.char_class = char_class
		self.password = password
	def render(self):
		msg = "Mr '%s %s' is connected under '%s'" % (self.password, 
														 self.char_class,
														 self.username,)
		return msg
class DBPool:
	"""
		Sqlite connection pool
	"""
	def __init__(self, dbname):
		self.dbname = dbname
		self.__dbpool = ConnectionPool('sqlite3', self.dbname, check_same_thread=False)

	def shutdown(self, callback_msg):
		"""
			Shutdown function
			It's a required task to shutdown the database connection pool:
				garbage collector doesn't shutdown associated thread
		"""
		self.__dbpool.close()
		
	def build_user(self, dbentries):
		"""
			Build user from dbentries
		"""
		username, char_class, password = dbentries[0]
		return User(username, char_class, password)
	def get_user_user(self, username):
		"""
			Build associated user object
		"""
		query = 'SELECT username, char_class, password from `users` where username=?'
		return self.__dbpool.runQuery(query, (username,)).addCallback(
												  self.build_user)
	def update_user_time(self, username, time):
		time = str(time)
		query = 'UPDATE `users` SET tonextlevel = tonextlevel + ' + time + ' where username=?'
		return self.__dbpool.runQuery(query, (username,))

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
			msg_out = "It isn't nice to whisper!  Play nice with the group."
			self.notice(user, msg_out)
			self.msg(self.factory.channel, msg)
			return

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