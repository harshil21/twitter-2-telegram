import logging
import subprocess

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import CallbackContext

from resources.strings import help_string, start_string

buttons = [[InlineKeyboardButton(text="Search tweet", switch_inline_query='')]]


def command_start(update: Update, _: CallbackContext) -> None:
    update.effective_chat.send_message(text=start_string, reply_markup=InlineKeyboardMarkup(buttons))
    logging.info(f"/start was used by {update.effective_user.name}")


def command_help(update: Update, _: CallbackContext) -> None:
    first_code = help_string.find('@username tweet')
    second_code = help_string[first_code + 9:].find('@username') + first_code + 9
    entities = [MessageEntity('code', offset=first_code, length=15), MessageEntity('code', second_code, 9)]
    update.effective_chat.send_message(text=help_string, entities=entities)
    logging.info(f"/help was used by {update.effective_user.name}")


def show_logs(update: Update, _: CallbackContext) -> None:
    """Sends bot logs to the bot maker at his will."""
    update.effective_chat.send_action(action='upload_document')  # Send chat action since there is a ~5 second wait

    command = 'heroku logs -a tweets-on-telegram-bot -s app -n 300'
    a = subprocess.Popen(command, shell=True, encoding='utf-8', stdout=subprocess.PIPE, errors='ignore')
    out, _ = a.communicate()

    with open('files/logs.txt', 'w') as log_f:
        log_f.write(out)
    with open("files/logs.txt", 'r') as log_f2:
        update.effective_chat.send_document(document=log_f2, filename='logs.txt')
