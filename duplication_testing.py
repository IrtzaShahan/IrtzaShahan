def main():
    query = '((from:Deitaone) OR (from:FirstSquawk)) -is:retweet -is:reply'
    try:
        with open('since_tweet.txt', 'r') as fp:
            stored_since = fp.read().strip()
    except FileNotFoundError:
        stored_since = ""
        
    if stored_since:
        tweets = client.search_recent_tweets(query, since_id=stored_since, expansions='author_id')
    else:
        start_time = (datetime.utcnow() - timedelta(minutes=30)).isoformat("T") + "Z"
        tweets = client.search_recent_tweets(query, start_time=start_time, expansions='author_id')
        
    if tweets.meta['result_count']:
        new_since_id = tweets.meta['newest_id']
        with open('since_tweet.txt', 'w') as fp:
            fp.write(new_since_id)
        for tweet in tweets.data:
            try:
                handle(tweet)
                time.sleep(randint(50, 100))
            except Exception as exc:
                print(exc)
        time.sleep(randint(150, 300))
    else:
        print("No new tweets; sleeping...")
        time.sleep(randint(100, 300))

while True:
    if allowed_hours():
        try:
            client = get_client()
            main()
        except Exception as e:
            print(e)
            asyncio.run(send_error(text=str(e)))
    else:
        # Outside allowed hours, clear since_tweet file so next allowed period uses 30 min window.
        with open('since_tweet.txt', 'w') as fp:
            fp.write("")
        print("Outside allowed hours. Waiting...")
        time.sleep(600)
