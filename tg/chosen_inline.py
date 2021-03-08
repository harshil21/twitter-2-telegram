import logging

from telegram import Update
from telegram.ext import CallbackContext


def chosen_result(update: Update, _: CallbackContext) -> None:
    logging.info(f'Query was {update.chosen_inline_result.query}, by: {update.effective_user.name}')
