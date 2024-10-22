import gspread
import tweepy
from time import sleep
import logging
from datetime import datetime


def get_client():
    consumer_key="1tIrZ5FBreACW9Y5Ax2jWykNn"
    consumer_key_secret= "PJZDRQXWbssdRMTuQVaXDNGCQZ8XCD9nWXC9WiXtP3oGnVn7mx"
    bt ="AAAAAAAAAAAAAAAAAAAAAFzxngEAAAAAdtyuetd%2BQb5k3avSMeKfB1CmnYo%3DpSu7huf9Jpljv98FSjHvs0iqakYto2Qp4O7Tj9U2qZhMfx7hEq" 
    access_token="1261053514542977031-KQYPFj3xasUhu6zo3RZdLKqZEHfzoH"
    access_token_secret="mIL5dW5j3eETU1WqlDks1xpC0M8tK0QoWHWiUqU2qqGQn"
    client = tweepy.Client(bt,consumer_key,consumer_key_secret,access_token,access_token_secret)
    return client


def add_to_google_sheet(tweets):
    gc = gspread.service_account(filename='googlekey.json')
    sh = gc.open('TwitterUpdates')
    ws1 = sh.worksheet('Sheet2')

    current_date = datetime.now().strftime('%Y-%m-%d')

    total_rows_before = len(ws1.get_all_values())

    try:
        with open('last_update_date.txt', 'r') as f:
            last_update_date = f.read().strip()
    except FileNotFoundError:
        last_update_date = None

    # Check if the day has changed
    if last_update_date != current_date:
        # Add a new row with the date if the day has changed
        ws1.append_row([f'New Tweets on {current_date}'])
        # Update the last update date in the file
        with open('last_update_date.txt', 'w') as f:
            f.write(current_date)


        ws1.format(f"A{total_rows_before+1}:A{total_rows_before+1}", { 'backgroundColor': {
            'red':0.0,
            'green':1.0,
            'blue':0.0}})
    
    # Prepare the data to be appended
    data = [[tweet.text] for tweet in tweets]
    # Append multiple rows at once
    ws1.append_rows(data)
    logging.info('successfully appended tweets')

def get_tweets(query, since_id):
    client = get_client()
    tweets = client.search_recent_tweets(
        query=query,
        since_id=since_id,
        max_results=100,
        user_auth=True
    )
    return tweets

def make_query():
    client = get_client()
    response = client.get_list_members(
        1839100192332853439,
        max_results=30,
        user_auth=True
    )
    usernames = [x.username for x in response.data]
    query = '(from:' + ')OR(from:'.join(usernames) + ")"
    q1 = ''
    for i in query.split(')OR('):
        if len(q1 + i) < 495:
            q1 += i + ')OR('
    q1 = q1[:-4]
    return '(' + q1 + ')' + ' -is:reply -is:retweet'

def main():
    query = make_query()
##    print(query)
##    sleep(100)
    try:
        with open('last_checked_id.txt', 'r') as f:
            start_id = int(f.read().strip())
    except FileNotFoundError:
        start_id = 1

    while True:
        try:
            s_id = None if start_id < 100 else start_id
            tweets = get_tweets(query, s_id)
            if tweets and tweets.meta['result_count']:
                tweet_list = tweets.data
                if tweet_list:
                    tweet_list.sort(key=lambda x: x.id)
                    add_to_google_sheet(tweet_list)
                    start_id = int(tweet_list[-1].id)
                    with open('last_checked_id.txt', 'w') as f:
                        f.write(str(start_id))
            else:
                logging.info('no new tweets found')
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(str(e))
        sleep(210)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info('Script Started')
    main()
    logging.info('Script Stopped')
#end code
