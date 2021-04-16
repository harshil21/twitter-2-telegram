import logging

from telegram.ext import CallbackContext


def error_handler(_: object, context: CallbackContext) -> None:
    """Log the serious error and shoot a Telegram message to the sensei."""
    error = str(context.error)
    if 'old' in error:  # Mostly ignore query timed out errors
        logging.error(msg=error)
        return

    logging.error(msg="Gone wrong. ", exc_info=context.error)
    context.bot.send_message(chat_id=476269395, text="Bad thing happened to me!! Click /logs")
