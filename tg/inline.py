import logging
from typing import List, Tuple

from telegram import InlineQueryResultArticle as InlineArticle, InputTextMessageContent as InpTxtMsg, Update, \
    InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto, InputMediaPhoto as InpMediaPic, \
    InlineQueryResultVideo
from telegram.ext import CallbackContext

from api.twitter_api import TwitterParser


def inline_tweets(update: Update, _: CallbackContext) -> None:
    """Handle the inline query."""
    results = []
    query = update.inline_query.query.split()
    parser = TwitterParser()

    if len(query) >= 1 and query[0].startswith('@'):  # User searches for a specific tweet from a specific user
        profile_query = f"{' '.join(query[1:])} from:{query[0][1:]}"

    elif len(query) >= 1 and not query[0].startswith('@'):  # User just searches for a random tweet from no one specific
        joined = ' '.join(query)
        profile_query = f'"{joined}" OR {joined} -filter:retweets'  # Get original tweet instead of RT's

    else:  # Get trending results
        trends = parser.get('trends/place.json', payload={'id': 1})
        profile_query = f"{parser.get_random_trend(trends)} -filter:retweets"

    payload = {'q': profile_query, 'count': 30, 'result_type': 'mixed', 'lang': 'en'}

    tweets = parser.get("search/tweets.json", payload=payload)
    for tweet in tweets['statuses']:
        tweet_info = parser.parse_tweet(tweet)
        inline_result = add_inlinequery(tweet_info)
        results.append(inline_result)

    update.inline_query.answer(results, cache_time=300, auto_pagination=True)


def add_inlinequery(tweet_data: dict):
    """Adds an appropriate InlineQueryResult* for each type of tweet."""
    if 'video_url' in tweet_data:  # Video -
        tweet_data['mime_type'] = 'video/mp4' if 'application/x' in tweet_data['mime_type'] else tweet_data['mime_type']
        return InlineQueryResultVideo(**tweet_data)

    if 'images' not in tweet_data:  # Article -
        return InlineArticle(**{
            'input_message_content': InpTxtMsg(tweet_data.pop('caption'), entities=tweet_data.pop('caption_entities'),
                                               disable_web_page_preview=True),
            **tweet_data})

    # Photo -
    images = tweet_data.pop('images')
    tweet_data['thumb_url'] = images[0]['photo_url']  # Keep thumb photo same as actual photo (instead of user dp)

    if len(images) > 1:  # Display buttons if more than 1 image is found
        buttons = [[InlineKeyboardButton(text='Next Photo', callback_data=f"{tweet_data['tweet_id']}_next_1")]]
        tweet_data['reply_markup'] = InlineKeyboardMarkup(buttons)

    data = {**images[0], **tweet_data}
    return InlineQueryResultPhoto(**data)


def edit_msg(update: Update, _: CallbackContext):
    tweet_id, page_op, page = update.callback_query.data.split('_')
    page = int(page)

    parser = TwitterParser()
    parser.tweet_info = parser.get('statuses/show.json', payload={'id': tweet_id})
    new_page, buttons = new_img(page, page_op, tweet_id, len(parser.tweet_info['extended_entities']['media']))

    parser.parse_text(parser.tweet_info)
    image_url = parser.parse_images(parser.tweet_info['extended_entities']['media'], img_no=new_page - 1)

    update.callback_query.edit_message_media(media=InpMediaPic(media=image_url, caption=parser.tweet_info['caption'],
                                                               caption_entities=parser.tweet_info['caption_entities']),
                                             reply_markup=InlineKeyboardMarkup(buttons))
    update.callback_query.answer()
    logging.info(f"{page_op} clicked for {tweet_id} to move to {new_page} from {page}.")


def new_img(page: int, page_op: str, tweet_id: str, max_imgs: int) -> Tuple[int, List[List[InlineKeyboardButton]]]:
    """Calculates and builds buttons for the images of a tweet."""
    new_page_no = page
    if page_op == 'next' and page < max_imgs:
        new_page_no += 1
    elif page_op == 'prev' and page > 1:
        new_page_no -= 1

    if new_page_no == 1:
        buttons = [[InlineKeyboardButton(text='Next Photo', callback_data=f'{tweet_id}_next_{new_page_no}')]]
    elif new_page_no == max_imgs:
        buttons = [[InlineKeyboardButton(text='Prev Photo', callback_data=f'{tweet_id}_prev_{new_page_no}')]]
    else:
        buttons = [[InlineKeyboardButton(text='Prev Photo', callback_data=f'{tweet_id}_prev_{new_page_no}'),
                    InlineKeyboardButton(text='Next Photo', callback_data=f'{tweet_id}_next_{new_page_no}')]]

    return new_page_no, buttons
