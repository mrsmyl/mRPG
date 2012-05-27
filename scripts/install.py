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

    # Create Events Table
    c.execute('''CREATE TABLE events
                (id INTEGER PRIMARY KEY, event_name TEXT, event_type TEXT, event_modifier NUMERIC)''')

    conn.commit()

    # Insert Our Events
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('discovered Mozor','calamity',1.1)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('ate a poisonous fruit', 'calamity', 1.2)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('fell in love with zach','terrible calamity',1.9)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('saw the light (which unfortunately ended up being a train)','terrible calamity',1.6)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('discovered Mozor', 'godsend', 0.9)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('found a $10 bill', 'godsend', 0.9)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('had the internet fail', 'really horrible calamity', 1.9)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('discovered the one true love of Pyotr: Ikea', 'weird thing', 1.1)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('discovered their ex had stolen all their stuff and turned out to be a monster', 'surprisingly common occurrence', 1.1)''')
    c.execute('''INSERT INTO events (event_name, event_type, event_modifier) VALUES
                ('went to https://github.com/mozor/mRPG/issues/new and reported bugs', 'really good idea yet seldom done thing', 0.5)''')

    conn.commit()

    # Create Meta Table
    c.execute('''CREATE TABLE mrpg_meta
                (name TEXT PRIMARY KEY, value TEXT)''')

    conn.commit()

    # Insert Version
    c.execute('''INSERT INTO mrpg_meta VALUES('VERSION','0.1')''')

    conn.commit()

    # We can also close the cursor if we are done with it
    c.close()

    print("The database has been created.")

if os.path.isfile(config):
	print("The config file has already been created.")
else:
	shutil.copy2("docs/example.cfg", config)
	print("Please modify config.cfg before running for the first time.")
