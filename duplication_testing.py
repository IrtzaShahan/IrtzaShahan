def check_mentions():
    try:
        with open('lst_checked_tweet.txt', 'r') as fp:
            start_id = int(fp.read())
    except FileNotFoundError:
        start_id = 1

    while True:
        try:
            s_id = None if start_id < 100 else start_id
            tweets = client.search_recent_tweets(
                '"@feelsonsolana"',
                expansions=['author_id', 'referenced_tweets.id'],
                since_id=s_id,
                tweet_fields=['author_id', 'referenced_tweets'],
                user_fields=['username', 'profile_image_url']
            )
            if tweets.meta['result_count']:
                users_dict = {u.id: u for u in tweets.includes.get('users', [])}
                tweets_dict = {t.id: t for t in tweets.includes.get('tweets', [])}
                for tweet in tweets.data:
                    if tweet.id > start_id and start_id > 10 and tweet.author_id != 1806231034264195073:
                        process_mention(tweet, tweets_dict, users_dict)
                start_id = int(tweets.meta['newest_id'])
                with open('lst_checked_tweet.txt', 'w') as fp:
                    fp.write(str(start_id))
            else:
                print('no tweets found')
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(str(e))
        sleep(60)
