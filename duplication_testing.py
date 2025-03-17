def main():
    try:
        with open('since_tweet.txt','r')as fp:
            start_tweet_id = fp.read()
    except FileNotFoundError:
        start_tweet_id = None

    tweets = client.search_recent_tweets(f'((from:Deitaone) OR (from:FirstSquawk)) -is:retweet -is:reply',since_id=start_tweet_id,expansions='author_id')
    if not tweets.meta['result_count']:
        print('no new tweet')
        sleep(randint(100,300))
        return
    start_tweet_id = tweets.meta['newest_id']
    with open('since_tweet.txt','w') as fp:
        fp.write(start_tweet_id)
    for tweet in tweets.data:
        try:
            handle(tweet)
            sleep(randint(50,100))
        except Exception as exc:
            import traceback
            traceback.print_exc()
            print(exc)
    sleep(randint(150,300))


    while True:
        try:
            client=get_client()
            main()
        except Exception as e:
            print(e)
            asyncio.run(send_error(text=str(e)))
            sleep(randint(150,300))
