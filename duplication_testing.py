def check_mentions():
    try:
        with open('lst_checked_tweet.txt','r') as fp:
            start_id = int(fp.read())
    except FileNotFoundError:
        start_id=1        
    while True:
        try:
            if start_id<100:
                s_id=None
            else:
                s_id = start_id
            tweets = client.search_recent_tweets('"@feelsonsolana"', expansions=['author_id'], since_id = s_id)
            if tweets.meta['result_count']:
                for tweet in tweets.data:
                    if (tweet.id > start_id) and (start_id>10) and (1806231034264195073 != tweet.author_id):
                        process_mention(tweet.id,tweet.author_id)
                start_id = int(tweets[3]['newest_id'])
                with open('lst_checked_tweet.txt','w') as fp:
                    fp.write(str(start_id))
            else:
                print('no tweets found')
        except KeyboardInterrupt:
            break 
        except Exception as e:
            try:
                print(str(e))
            except KeyboardInterrupt:
                break
        sleep(60)
