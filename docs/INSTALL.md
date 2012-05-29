Install file for mRPG
========
Copyright 2012 [Greg](https://github.com/newtoz) & [Richard](https://github.com/richard4339)  
Licensed under the Creative Commons BY-NC-SA license.

Software needed for mRPG
--------
* Python (http://www.python.org)
* Twisted (http://twistedmatrix.com)
* passlib (https://code.google.com/p/passlib/)

How To Install
--------
1. Ensure you have the prerequisite software
2. Run ```python scripts\install.py```
3. Edit your new config.cfg
4. Run the script itself ```python mrpg.py```

Example Configuration File
--------
````python
[IRC]
server = irc.mozor.net
port = 6667
channel = #idlerpg
nickname = IdleBot
nickserv_password = abc123
nickserv_email = mrpg@mozor.net

[BOT]
timespan = 10.0
min_time = 30
penalty_constant = 1.1
use_private_message = 1
event_randomness = 1

[MOV]
movespan = 120
world_radius = 300
walking_speed = 5
````

Example Configuration Explanation
--------

### [IRC] ###
* **server** _string_  
	A qualified server name for the bot to connect to
* **port** _integer_  
	Port number for the server specified above. This will almost always be 6667.
* **channel** _string_ 
	The channel name for the bot to connect into on startup
* **nickname** _string_ 
	The nickname for the bot to attempt to use
* **nickserv_password** _string_  
	mRPG supports attempting to identify with NickServ provided Nickserv used the ```/msg NickServ Identify PASSWORD``` syntax.
* **nickserv_email** _string_ 
	mRPG supports registering with NickServ. This is the email address he will pass through the registration command

### [BOT] ###
* **timespan** _float_ 
	mRPG is multithreaded and ANY commands sent to the bot are processed immediately. However, you don't need the bot recalculating everything every second. This is how often he actually recalculates the TTL.
* **min_time** _integer_  
	Minimum time between levels
* **penalty_constant** _float_  
	Constant to multiply the current TTL by for penalty actions
* **use_private_message** _integer [1/0]_  
	1 means the bot will use a private message to a user for a private message, 0 means he will use a notice instead.
* **event_randomness** _integer_  
	The odds that you will get an event to trigger on each loop. 1 == lowest chance, 100 or higher == guaranteed. Entering 0 will effectively disable events altogether.

### [MOV] ###
* **movespan** _float_
    How often the movement function runs.
* **world_radius** _float_
    The radius of the circular body the characters are inhabiting. Units are in km.
* **walking_speed** _float_
    How fast the characters move. Units are in km/h.