import logging
import os

from telegram.ext import Updater, InlineQueryHandler, CallbackQueryHandler, CommandHandler, ChosenInlineResultHandler

with open(".env", 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        os.environ[key] = value

from tg.inline import inline_tweets, edit_msg
from tg.commands import command_start, command_help
from tg.chosen_inline import chosen_result

logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fh = logging.FileHandler('files/logs.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def main() -> None:
    token = os.getenv('token')
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(ChosenInlineResultHandler(callback=chosen_result))
    dp.add_handler(InlineQueryHandler(inline_tweets, run_async=True))
    dp.add_handler(CallbackQueryHandler(callback=edit_msg, pattern='\d', run_async=True))
    dp.add_handler(CommandHandler(command='start', callback=command_start))
    dp.add_handler(CommandHandler(command='help', callback=command_help))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.info(f"Process started...")
    main()