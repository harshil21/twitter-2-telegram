from random import choice
from typing import Tuple
from uuid import uuid4

import requests
import html
from telegram import MessageEntity

from resources.data_objects import auth_header
from resources.helpers import human_format, get_offset
from resources.strings import base, t_link


class TwitterParser:
    def __init__(self):
        self.tweet_info: dict = {}
        self.name: str = ''

    def parse_tweet(self, tweet: dict):
        self.tweet_info = {}
        self.parse_text(tweet)
        self.parse_user_info(tweet)
        if 'extended_entities' in tweet:  # Check if any media in tweet
            self.parse_video(tweet['extended_entities']['media'][0])
            self.parse_images(tweet['extended_entities']['media'])
        return self.tweet_info

    def parse_text(self, tweet: dict):
        reply_text = None
        entities = []

        likes, retweets = self.parse_tweet_metrics(tweet)
        link_to_tweet = f"❤ {likes} 🔁 {retweets}\nLink"

        full_tweet = html.unescape(tweet['full_text']).strip()  # Convert html incompatible chars like &amp; -> &
        text = full_tweet

        self.name = f"{tweet['user']['name']} - @{tweet['user']['screen_name']}{' ✅' if self.verified(tweet) else ':'}"
        self.tweet_info['description'] = full_tweet

        if 'retweeted_status' in tweet:  # Get full text from retweet, since original one is truncated to 140 chars
            text = f"🔁 @{tweet['retweeted_status']['full_text']}"

        if tweet['in_reply_to_screen_name'] is not None:  # If tweet is a reply to another person
            replied_username = tweet['in_reply_to_screen_name']
            reply_text = f"In reply to @{replied_username}"  # Build replied to string
            text = f"{reply_text}:\n\n{text.replace(f'@{replied_username} ', '')}"  # Remove reply username from org txt

        text = self.remove_link(text)
        caption = f"{self.name}\n\n{text}\n\n{link_to_tweet}"
        self.tweet_info['caption'] = caption

        bold_length = len(self.name.encode('utf-16-le')) // 2  # We want to make the name bold
        link_offset = get_offset(caption, len(caption) - 4)  # Make the 'Link'... a link.

        entities.extend([MessageEntity('bold', offset=0, length=bold_length),
                         MessageEntity('text_link', offset=link_offset, length=4, url=f"{t_link}/{tweet['id_str']}")])

        if reply_text is not None:  # Make 'replied to' text italic.
            start = caption.encode('utf-16-le').find('In reply to @'.encode('utf-16-le')) // 2
            entities.append(MessageEntity('italic', offset=start, length=len(reply_text)))

        self.tweet_info['caption_entities'] = entities

    def parse_user_info(self, user_info: dict):
        self.tweet_info['id'] = str(uuid4())  # For InlineQuery purposes
        self.tweet_info['tweet_id'] = user_info['id_str']  # For callback data purposes.
        self.tweet_info['title'] = self.name
        self.tweet_info['thumb_url'] = user_info['user']['profile_image_url']

    def parse_video(self, media_info: dict):
        if 'video_info' not in media_info:  # Return instantly if no video in tweet
            return

        variants = media_info['video_info']['variants']
        video = variants[0]
        if 'gif' not in media_info['type']:
            video = variants[1]
            self.tweet_info['video_duration'] = int(media_info['video_info']['duration_millis'] / 1000)  # Convert to s
        self.tweet_info['video_url'] = video['url']
        self.tweet_info['mime_type'] = video['content_type']
        self.tweet_info['thumb_url'] = media_info['media_url']

    def parse_images(self, media_info: dict, img_no: int = -1):
        if 'video_url' in self.tweet_info:
            return

        images = []
        for image in media_info:
            images.append({'photo_url': image['media_url']})
        self.tweet_info['images'] = images
        return images[img_no]['photo_url'] if img_no != -1 else None

    @staticmethod
    def get(endpoint: str, payload: dict) -> dict:
        default_payload = {'tweet_mode': 'extended', 'include_entities': True, **payload}
        r = requests.get(f"{base}/{endpoint}", headers=auth_header, params=default_payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise ConnectionError(r.status_code, r.content, r.url)

    @staticmethod
    def get_random_trend(trend_data: dict) -> str:
        return choice(trend_data[0]['trends'])['name']

    @staticmethod
    def parse_tweet_metrics(tweet: dict) -> Tuple[str, str]:
        return human_format(tweet['favorite_count']), human_format(tweet['retweet_count'])

    @staticmethod
    def verified(tweet: dict) -> bool:
        return tweet['user']['verified']

    @staticmethod
    def remove_link(text: str):
        link_pos = text.find('https://t.co/')
        return text[:link_pos] if link_pos != -1 else text
