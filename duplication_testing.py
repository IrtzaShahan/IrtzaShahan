import requests,csv
import tweepy,json
from time import sleep
from random import randint
from html import unescape
import openai
from gpt import generate_response

openai.api_key ='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'

def get_tweepy_client():
    consumer_key='kaCfaNRiXXo2b3RbU2QgYUBRH'
    consumer_secret= 'BVPPVfbJaTcpi0NaF7R7HoKnNPb5pX4h3A9KJwSm3kAMydNbgK'
    access_token = "1658044646008979456-QILLBEBeR3GBh0EtxtSnYbJo9vlOzP"
    access_token_secret = "fPLcKrqo0Ketk2WepdX0xkwZjWGKtdtY7kztGpZzoAtL3"
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAA4BiwEAAAAASiVhj2vzR89HfeGYuV56Ni9NTnc%3DBaqNEeLhCvheZNZo4YKP6MAKf08yivGpJ1VteHnk2ZnYQ6Q326"  
    client = tweepy.Client(consumer_key=consumer_key, consumer_secret= consumer_secret, access_token=access_token, access_token_secret= access_token_secret,bearer_token=bearer_token)
    
    return client

def respond_tellme(tw_id,message,tweet_author_name):
    reply_string = generate_response(f'/jailbreak write a reply to this tweet: "{message}", by twitter user "@{tweet_author_name}".') 
    try:
        client.create_tweet(text = reply_string[:280], in_reply_to_tweet_id = tw_id)
    except Exception as e:
        print(e)

def handle_mention(mention):
    print(f'new tweet: {mention.id}')

    tweet_author_id = mention.author_id
    tweet_author_name = usersdict.get(mention.author_id)
    
    if tweet_author_name == bot.username:
        return
    with open('own_tweets.json','r') as fp:
        own_tweets=json.load(fp)
    if str(mention.referenced_tweets[0].id) in own_tweets:
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
    respond_tellme(mention.id,message,own_tweets)


if __name__ == '__main__':
    openai.api_key = openai_key
    
    model_engine = "text-davinci-003"

    with open('since_tweet.txt','r')as fp:
        start_tweet_id = fp.read()

    client,api = get_tweepy_client()
    bot = client.get_me().data
    print(f'bot starting on {bot.username} twitter account')

    while True:
        try:
            tweets = client.search_recent_tweets(f'@{bot.username} -is:retweet',since_id=start_tweet_id,expansions='author_id,referenced_tweets.id',tweet_fields='entities,referenced_tweets',user_auth=True,max_results=20)

            if not tweets.meta['result_count']:
                #print('no tweets found')
                sleep(randint(60,100))
                continue
            start_tweet_id = tweets.meta['newest_id']
            with open('since_tweet.txt','w') as fp:
                fp.write(start_tweet_id)
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
