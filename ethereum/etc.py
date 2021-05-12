# ========================================================================
# Copyright © 2017 Alessandro Spallina
#
# Github: https://github.com/AlessandroSpallina
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# ========================================================================

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import logging
import http.client
import json
import time

# ==================== NOTABLE VARIABLES =================================

# telegram token returned by BotFather
TELEGRAMTOKEN = "YOUR_BOT_TOKEN_HERE"

# get this url from ethermine -> json api section
APIURL = "/miner/YOUR_ADDRESS_HERE/dashboard/"

# api host
APIHOST = "api-etc.ethermine.org"

# if number of active workers drop less than this number bot will notify you.
# so if you have 3 rigs, WNUM should set to 3!
WNUM = 3

# every X minutes bot will check that WNUM workers are up on ethermine
# i suggest to set this to 30 minutes
WCHECKINGMINUTES = 30

# bot won't request pool, if previous information had been fetched in X minutes before
TTL = 3

# this list contains user_id of user that are allowed to get response from the bot
ALLOWEDUSERID = [0000000, 1111111]

# log filename
LOGPATH = "etc.log"

# ========================================================================


logging.basicConfig(
    filename=LOGPATH,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

class DashboardException(Exception):
    pass


lastUpdate = int(time.time()) - TTL * 60
cachedDashboard = {}

def getDashboard():
    global lastUpdate
    global cachedDashboard

    if int(time.time()) - lastUpdate < TTL * 60:
        logger.info("Using cache from " + time.strftime("%d/%m/%y %H:%M", time.localtime(lastUpdate)))
        return cachedDashboard

    logger.info("Fetching dashboard. Last cache from " + time.strftime("%d/%m/%y %H:%M", time.localtime(lastUpdate)))

    conn = http.client.HTTPSConnection(APIHOST)
    conn.request("GET", APIURL)
    res = conn.getresponse()

    if res.status != 200:
        raise DashboardException("Unable to reach Ethermine: {}".format(res.reason)) 
    
    body = res.read().decode("utf-8")

    db = json.loads(body)
    cachedDashboard = db['data']
    lastUpdate = int(time.time())
    conn.close()

    return cachedDashboard

def checkWorkers(bot, job):
    logger.info("checking workers")
    toSend = ""
    try:
        s = getDashboard()['currentStatistics']
        logger.info(s)
        if s['activeWorkers'] < WNUM:
            toSend = "WARNING: Seems like some of your workers are offline ({}/{})".format(
                s['activeWorkers'], WNUM)
            for usr in ALLOWEDUSERID:
                bot.send_message(usr, text=toSend)
    except DashboardException as err:
        toSend = err
        for usr in ALLOWEDUSERID:
            bot.send_message(usr, text=toSend)


def status(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        toSend = ""
        try:
            aus = getDashboard()['currentStatistics']
            toSend = "Hashrate: {} MH/s\nReportedHashrate: {} MH/s\nnWorkers: {}\nShares (v/s/i): {}/{}/{}\nUnpaid: {} ETC\nUnconfirmed: {} ETC".format(
                aus['currentHashrate'] * 100 // 1000000 / 100, aus['reportedHashrate'] * 100 // 1000000 / 100, aus['activeWorkers'], aus['validShares'], aus['staleShares'], aus['invalidShares'], aus['unpaid'] / 10**18, aus['unconfirmed'] / 10**18)      
        except DashboardException as err:
            toSend = err
        update.message.reply_text(toSend)
    else:
        logger.info("{} tried to contact me (comm: {})".format(
            update.message.from_user, update.message.text))


def workers(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        toSend = ""
        try:
            ws = getDashboard()['workers']
            for w in ws:
                toSend += "Worker {}\nCurrentHashrate: {} MH/s\nReportedHashrate: {} MH/s\nShares (v/s/i): {}/{}/{}\nLastSeen: {}\n\n".format(
                    w['worker'], w['currentHashrate'] * 100 // 1000000 / 100, w['reportedHashrate'] * 100 // 1000000 / 100, w['validShares'], w['staleShares'], w['invalidShares'], time.strftime("%d/%m/%y %H:%M", time.localtime(w['lastSeen'])))
        except DashboardException as err:
            toSend = err
        update.message.reply_text(toSend)
    else:
        logger.info("{} tried to contact me (comm: {})".format(
            update.message.from_user, update.message.text))


def help(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        toSend = "Command List\n/status - general info\n/workers - list workers\n/help - print this :D\nNOTE: this bot automatically checks for workers crash!"
        update.message.reply_text(toSend)
    else:
        logger.info("{} tried to contact me (comm: {})".format(
            update.message.from_user, update.message.text))


def ping(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        update.message.reply_text("pong")
    else:
        logger.info("{} tried to contact me (comm: {})".format(
            update.message.from_user, update.message.text))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(TELEGRAMTOKEN, use_context=False)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("workers", workers))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("ping", ping))

    dp.job_queue.run_repeating(
        checkWorkers, (WCHECKINGMINUTES * 60))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
