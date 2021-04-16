import logging
import os

from telegram.ext import (Updater, InlineQueryHandler, CallbackQueryHandler, CommandHandler,
                          ChosenInlineResultHandler, Filters)

try:
    with open(".env", 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
except FileNotFoundError:
    pass

from tg.inline import inline_tweets, edit_msg
from tg.commands import command_start, command_help, show_logs
from tg.chosen_inline import chosen_result
from tg.error_handler import error_handler

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
    dp.add_handler(CommandHandler(command='logs', filters=Filters.user(username='Hoppingturtles'), callback=show_logs))

    dp.add_error_handler(error_handler)
    # for heroku-
    print(int(os.environ.get('PORT')))
    updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', 8443)), url_path=token,
                          webhook_url=f"https://tweets-on-telegram-bot.herokuapp.com/{token}")
    updater.idle()


if __name__ == '__main__':
    logging.info("Process started...")
    heroku_pass = os.getenv('heroku_pass')
    with open('./.netrc', 'w') as f:
        heroku_creds = "machine api.heroku.com\n" \
                       "   login ilovebhagwan@gmail.com\n" \
                       f"   password {heroku_pass}\n" \
                       "machine git.heroku.com\n" \
                       "   login ilovebhagwan@gmail.com\n" \
                       f"   password {heroku_pass}\n"
        f.write(heroku_creds)
    main()
