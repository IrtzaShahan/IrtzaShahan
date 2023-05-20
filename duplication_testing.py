import requests,csv
import tweepy,json
from time import sleep
from random import randint
from html import unescape
import openai

openai_key='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'

def get_tweepy_client():
    consumer_key = 'YgXTZIKZbqAJaGGtJ2CIX63eo'
    consumer_secret = 'jql3FzfeIufph5abCuG72hRf1vXa1H5wVkpA7336KzTPhIzchb'
    access_token = '1655668870340812813-6jiZq1SyPjdfkdc79ZczCDXha94K2f'
    access_token_secret = 'AxmVHAHwLHWsyzCz7IC8sxgrLFXRyAHSNX9IjV8i6XLni'
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAFxhnQEAAAAA0ka0WObWvkQuv8O%2B76K2JSTErdc%3D3uUQZTEfDjBSA2yxFhzFy8zU3mALNc2Y1DAAU1e8YZzUlZvu6l'
    auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    api = tweepy.API(auth)
    # Create a client using the given credentials
    client = tweepy.Client(consumer_key=consumer_key, consumer_secret= consumer_secret, access_token=access_token, access_token_secret= access_token_secret,bearer_token=bearer_token)
    return client,api

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
    reply_string = generate_response(f'Explain this tweet: "{message}", in simple language in a tweet less than 300 characters long.') 
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
    openai.api_key = openai_key
    
    model_engine = "text-davinci-003"

    start_tweet_id = None
    client,api = get_tweepy_client()
    bot = client.get_me().data
    print(f'bot starting on {bot.username} twitter account')

    while True:
        try:
            tweets = client.search_recent_tweets(f'@{bot.username} -is:retweet',since_id=start_tweet_id,expansions='author_id,referenced_tweets.id',tweet_fields='entities,referenced_tweets',user_auth=True,max_results=20)

            if not tweets.meta['result_count']:
                print('no tweets found')
                sleep(randint(25,45))
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
        sleep(randint(25,40))
