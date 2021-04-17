import logging

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


def show_logs(_: object, context: CallbackContext) -> None:
    """Sends bot logs to the bot maker at his will."""
    context.bot.send_chat_action(chat_id=476269395, action='upload_document')
    with open("files/logs.log", 'r') as log_f2:
        context.bot.send_document(chat_id=476269395, document=log_f2, filename='logs.txt')
