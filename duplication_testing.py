import requests,csv
import tweepy,json
from time import sleep
from random import randint
from html import unescape

def get_tweepy_client():
    consumer_key = 'B8zKZZFwJFsds2Wtt4lpicFCJ'
    consumer_secret = 'e0w02cSyrkmmCzzqwHYuIgymORFEd5cQvSFHMIOROUzZo8LGlh'
    access_token = '1658970062550880256-QJ7WMPCx6V0KDhmMiLrM0P9AyO7D8u'
    access_token_secret = 'lPMaCorpg4ST2gz8Nz8hTH2rPjpm38mDgN6usvb2ecnbb'
    client = tweepy.Client(None,consumer_key=consumer_key, consumer_secret= consumer_secret, access_token=access_token, access_token_secret= access_token_secret)
    consumer_key = '4j8NohX4nwX6lBvs1PnkXOpxP'
    consumer_secret = '4aUScB6lGep3PPhjrBipjMV4cjMQUnxYrjj5ZPeh9S3LMNKBVy'
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAO2QngEAAAAAYNGaIqCQuUVBPKKJZ3PrQ12aScg%3DSOcwAJSYArlooMWSJ4V7LBH9yYNyoifkZV4ttiJqJgRO15CxL4'     
    access_token = "1658970062550880256-QcaH6CiYUclzoAkYOEQUqt44jC96sE"
    access_token_secret = "K55Pk4bmDvWCPSa1kQLTgrMzbBlAwOdrp09PaC469X66X"
    client2 = tweepy.Client(consumer_key=consumer_key, consumer_secret= consumer_secret, access_token=access_token, access_token_secret= access_token_secret,bearer_token=bearer_token)
    
    return client,client2

def generate_response(prompt):
    completions = openai.Completion.create(        
        engine=model_engine,
        prompt=prompt,
        max_tokens=90, # Set maximum number of tokens to 286
        n=1,
        stop=None,
        temperature=0.75,
        )
    message = completions.choices[0].text
    return message

def respond_tellme(tw_id,message):
    reply_string = generate_response(f'Reply to this tweet: "{message}", as simple language in a tweet less than 300 characters long.') 
    client.create_tweet(text = reply_string[:280], in_reply_to_tweet_id = tw_id)

def handle_mention(mention):
    print(f'new tweet: {mention.id}')

    tweet_author_id = mention.author_id
    tweet_author_name = usersdict.get(mention.author_id)
    
    if tweet_author_name == bot.username:
        return

    text = tweets_dict[mention.referenced_tweets[0].id]
    text = unescape(text)
    tl = text.lower()
    
    tweet_words = text.split()
    tweet_words = [x.strip() for x in tweet_words]

    for word in tweet_words[:]:
        if 'urls' in mention.entities:
            for url in mention.entities['urls']:
                if (url['url'].lower() == word.lower()) or (mention.text.lower().index(word.lower())==url['start']):
                    tweet_words.remove(word)
#                     tweet_words = list(map(lambda x: x.replace(word,url['expanded_url'] ), tweet_words))

    for word in tweet_words[:]:
        if ('@' in word) or ('http' in word) or (len(word) < 1):
            tweet_words.remove(word)
    message = ' '.join(tweet_words)    
    message = message.strip()
    respond_tellme(mention.id,message)


if __name__ == '__main__':
#     openai.api_key = openai_key
    
    model_engine = "text-davinci-003"

    start_tweet_id = '1656768804150550529'
    readclient,client2 = get_tweepy_client()
    bot = client2.get_me().data
    print(f'bot starting on {bot.username} twitter account')

    while True:
        try:
            tweets = readclient.search_recent_tweets(f'@{bot.username} -is:retweet',since_id=start_tweet_id,expansions='author_id,referenced_tweets.id',tweet_fields='entities,referenced_tweets',user_auth=True)
            if not tweets.meta['result_count']:
                print('no tweets found')
                sleep(randint(60,100))
                continue
            start_tweet_id = tweets.meta['newest_id']
            usersdict = {x.id:x.username for x in tweets.includes['users']}
            tweets_dict = {x.id:x.text for x in tweets.includes['tweets']}
            for tweet in tweets.data:
                if  tweet.author_id != bot.id:
                    try:
                        handle_mention(tweet)
                        sleep(randint(3,10))
                    except Exception as exc:
                        import traceback
                        traceback.print_exc()
                        print(exc)
        except Exception as e:
            print(e)
        sleep(randint(60,100))
