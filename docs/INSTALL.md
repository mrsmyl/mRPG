Install file for mRPG
========
Copyright 2012 [Greg](https://github.com/newtoz) & [Richard](https://github.com/richard4339)  
Licensed under the Creative Commons BY-NC-SA license. 

Software needed for mRPG
--------
* Python (http://www.python.org)
* Twisted (http://twistedmatrix.com)
* passlib (https://code.google.com/p/passlib/)

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
use_private_message = Y
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
* **use_private_message** _string [Y/N]_  
	Y means the bot will use a private message to a user for a private message, N means he will use a notice instead.