# ========================================================================
# Copyright © 2015 Alessandro Spallina
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
APIURL = "/api/miner_new/YOUR_ADDRESS_HERE"

# if number of active workers drop less than this number bot will notify you.
# so if you have 3 rigs, WNUM should set to 3!
WNUM = 3

# every X minutes bot will check that WNUM workers are up on ethermine
# i suggest to set this to 30 minutes
WCHECKINGMINUTES = 30

# this list contains user_id of user that are allowed to get response from the bot
ALLOWEDUSERID = [0000000, 1111111]

# log filename
LOGPATH = "eth.log"

# ========================================================================


logging.basicConfig(
    filename=LOGPATH,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def checkWorkers(bot, job):
    conn = http.client.HTTPSConnection("ethermine.org")
    conn.request("GET", APIURL)
    res = conn.getresponse()
    toSend = ""
    if res.status == 200:
        buf = json.loads(res.read().decode("utf-8"))
        s = buf['minerStats']
        activeWorkers = s['activeWorkers']
        if activeWorkers < WNUM:
            toSend = "WARNING: Seems like some of your workers are offline ({}/{})".format(
                activeWorkers, WNUM)
            for usr in ALLOWEDUSERID:
                bot.send_message(usr, text=toSend)
    else:
        toSend = "Unable to reach Ethermine: {}".format(res.reason)
        for usr in ALLOWEDUSERID:
            bot.send_message(usr, text=toSend)


def status(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        conn = http.client.HTTPSConnection("ethermine.org")
        conn.request("GET", APIURL)
        res = conn.getresponse()
        toSend = ""
        if res.status == 200:
            buf = json.loads(res.read().decode("utf-8"))
            aus = buf['minerStats']
            toSend = "Addr: {}\nHash: {}\nreportedHash: {}\nnWorkers: {}\nShares (v/s/i): {}/{}/{}".format(
                buf['address'], buf['hashRate'], buf['reportedHashRate'], aus['activeWorkers'], aus['validShares'], aus['staleShares'], aus['invalidShares'])
        else:
            toSend = "Unable to reach Ethermine: {}".format(res.reason)
        update.message.reply_text(toSend)
        conn.close()
    else:
        logger.info("{} tried to contact me (comm: {})".format(
            update.message.from_user, update.message.text))


def workers(bot, update):
    if update.message.chat_id in ALLOWEDUSERID:
        conn = http.client.HTTPSConnection("ethermine.org")
        conn.request("GET", APIURL)
        res = conn.getresponse()
        toSend = ""
        if res.status == 200:
            buf = json.loads(res.read().decode("utf-8"))
            w = buf['workers']
            for iterator in w:
                buf = w[iterator]
                toSend += "Worker {}\nHash: {}\nreportedHash: {}\nShares (v/s/i): {}/{}/{}\nLastShare: {}\n\n".format(
                    buf['worker'], buf['hashrate'], buf['reportedHashRate'], buf['validShares'], buf['staleShares'], buf['invalidShares'], time.strftime("%d/%m/%y %H:%M", time.localtime(buf['workerLastSubmitTime'])))
        else:
            toSend = "Unable to reach Ethermine: {}".format(res.reason)
        update.message.reply_text(toSend)
        conn.close()
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
    updater = Updater(TELEGRAMTOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("workers", workers))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ping", ping))

    dp.job_queue.run_repeating(
        checkWorkers, (WCHECKINGMINUTES * 60))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
