#!/usr/bin/env python

# mRPG
# https://github.com/mozor/mRPG
#
# Copyright 2012 Greg (NeWtoz@mozor.net) & Richard (richard@mozor.net);
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.

import os.path
import os
import shutil
import sqlite3

path = os.getcwd()
print path
db = "mrpg.db"
config = "config.cfg"

if os.path.isfile(db):
	print("The database file has already been created.")
else:
	open(db, "w").close()
	print("The empty database file has been created.")
	
	conn = sqlite3.connect(db)
	
	c = conn.cursor()

	# Create Users Table
	c.execute('''CREATE TABLE users
	             (username TEXT PRIMARY KEY, char_name TEXT, password TEXT, char_class TEXT, hostname TEXT, level NUMERIC, ttl NUMERIC, online INT, registration_date TEXT DEFAULT CURRENT_TIMESTAMP, last_login TEXT DEFAULT CURRENT_TIMESTAMP)''')

	conn.commit()
	
	# Create Items Table
	c.execute('''CREATE TABLE items
	             (id INTEGER PRIMARY KEY, item_name TEXT, item_type TEXT)''')

	conn.commit()

	# Create Events Table
	c.execute('''CREATE TABLE events
	             (id INTEGER PRIMARY KEY, event_name TEXT, event_type TEXT)''')

	conn.commit()
	
	# We can also close the cursor if we are done with it
	c.close()
	
	print("The database has been created.")

if os.path.isfile(config):
	print("The config file has already been created.")
else:
	shutil.copy2("docs/example.cfg", config)
	print("Please modify config.cfg before running for the first time.")
