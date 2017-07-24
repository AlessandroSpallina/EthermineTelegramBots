# EthermineTelegramBots
A collection of Telegram bots that allow you to check the status of your mining rigs
___
### Intro
A few days ago i was searching for a telegram bot which __notify__ me about my workers'
crash and able to return info about general stats and specifically stats of workers
under __Ethermine Mining Pool__. My research was a failure because a lot of ethermine
telegram bots are not up at time of writing and other bots are available only
under paid subscription, moreover i was unable to find a simple telegram bot source
code that satisfy my requirements.
So i wrote a python basic telegram bot which parse ethermine json in order to
check for worker and accept command from __allowed only telegram users or group__.

### What's inside the repo
Right now, only bot for __ethereum__ mining side of ethermine pool is available, but
in the future i'm planning to port the script of the bot for __ethereum classic__
(etc.ethermine.org) and for __zcash__ side of ethermine.
So, inside this repository you will find a very simple python script that is
able to accept commands:
* _help_ - print help
* _status_ - print general info about all total hashrate and other trivials
* _workers_ - print specifically workers infos

This bot _check periodically for number of workers that should reach the pool_ and
if this drop less than setted number the bot will advice the list of allowed users!
Note that this code is __Free Software__ and free to modify and you can made everything
you want; this source is _for people who want to host their own bot_, just set the
option and put this code on a vps or in a raspberry or where you want and it's done!
(so is not the source code of a bot that allow multiple miners to use the same bot
for the service, i prefer to host my own bot and maybe also you too!)

### Dependencies & Script Execution
The only thing you should do before runnign this python script is install [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot).
Should be fine the command (obviously you should have python3 already installed):
```
pip3 install python-telegram-bot
```
and then just enter in ethereum directory, so
```
python3 eth.py &
```

### TODO
Telegram bot of Ethermine:
* ETH -> done
* ETC
* ZEC
__feel free to open issue and propose and contribute!__

##### Donate
Tip Jar for broken student
eth, etc, erc20/23 token -> 0x9eadbcF8Da788944Fc4da034bFa0d550eDC0bdad
