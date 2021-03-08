import os

start_string = "This bot gets you any tweet from Twitter on Telegram. Use me in inline mode to search for a tweet! " \
               "\n\nUse /help to know about the all the ways you can use the inline mode!"

help_string = "Ways in which you can use the inline mode:\n\n1. Just type out the text of the tweet! The results " \
              "obtained are a mix of both popular and recent tweets.\n\n2. In the format: @username tweet\nThis " \
              "will filter tweets from that user only.\n\n3. In the format: @username. This will get all recent " \
              "tweets of that user.\n\nLimitations:\nCurrently tweets can only be found if they are posted in the " \
              "last 7 days. This is due to Twitter's search API restriction.\n\nIf you'd like to extend that, you " \
              "can let the dev, me (@Hoppingturtles) know via PM. Given enough requests, I'll make the switch."

bearer_token = os.getenv('bearer_token')

base = "https://api.twitter.com/1.1"

t_link = "https://twitter.com/i/status"
