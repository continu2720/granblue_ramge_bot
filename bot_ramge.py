# -*- coding: utf-8 -*-

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import datetime
import json
import requests
import urllib.request
import configure
import os
import sys
import re

def papago_translate(text):
    client_id = configure.papago_client_id
    client_secret = configure.papago_secret

    encText = urllib.parse.quote(text)
    data = "source=ja&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    
    if(rescode==200):
        response_body = response.read()
        translated = response_body.decode('utf-8')
        translated = json.loads(translated)
        return(translated['message']['result']['translatedText'])

    else:
        return("Error Code:" + rescode)

def line_message(text):
    
    text = papago_translate(text)

    print(str(datetime.date.today()))
    print(text+'\n')
    try:
        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = configure.line_token
        response = requests.post(TARGET_URL,
                headers={'Authorization': 'Bearer ' + TOKEN},
                data={'message': text})

    except Exception as ex:
        print(ex)

def authorize():
    consumer_key = configure.consumer_key
    consumer_secret = configure.consumer_secret

    access_token = configure.access_token
    access_token_secret = configure.access_token_secret

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    return auth

def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    else:
        return True 

class TwitterListener(StreamListener):

    def on_status(self, status):
        if from_creator(status):
            try:
                line_message(status.text)
                return True
            except BaseException as e:
                print("Error on_data %s" % str(e))
            return True
        return True

    def on_error(self,status):
        if status_code == 420:
            print("Limit Exceed")
            return False
        print("ERROR >>" + str(status))


if __name__=="__main__":
    auth = authorize()
    
    listener = TwitterListener()
    stream = Stream(auth, listener)

    stream.filter(follow=["1549889018"])



