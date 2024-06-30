import praw,requests,csv,os,asyncio
from time import sleep
from telegram import Update,Bot

chat_id = '-1002172782595'
telegram_bot_token = '6920822174:AAF9FSA0FyZCU46D_766y4KjIlbtFq3FpEo'
sheet_url = 'https://docs.google.com/spreadsheets/d/10MdKO1OYbDrDdrPGRHALjKFlL1lFr0YsjI_4uITzHuk/edit?gid=1058675105#gid=1058675105'
#in minutes
wait_timer = 360 # 6 hours
# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id='XT8Ogk7-MGknh4vCy3JxMg',
    client_secret='K4YUIDRQ77jrgFFMrwDkBZAgyGjqqQ',
    user_agent='windows:Sub Scraper:v0.9.6 (by u/Boefie16)'
)

# Function to check if a Reddit user exists
def check_user_existence(username='MariaHollow'):
        try:
            user = reddit.redditor(username)
            if getattr(user, 'is_suspended', False):
                return False
            if not user.id:
                return False
        except Exception as e:
            if "received 404 HTTP response" not in str(e):
                print(f'error occured while trying to check {username} error: {e}')
            else:
                return False
        else:
            user_results = list(reddit.subreddit("all").search(f"author:{username}", limit=1, params={'include_over_18': 'true'}))
            if user_results:
                return True
            if user.id:
                return True
async def send_tg_msg(chat_id,text):
    bot = Bot(token=telegram_bot_token)
    response = await bot.send_message(chat_id=chat_id, text = text)
    sleep(1)

def get_user_names(sheet_url):
    url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    res = requests.get(url_1)
    usernames = []
    with open('file.csv','w+',encoding='utf-8', newline='')as f:
        f.write(res.text)
        f.seek(0)
        f.readline()
        for cols in csv.reader(f,delimiter=','):
            if cols[4]:
                usernames.append(cols[4])
    os.remove('file.csv')
    return usernames


if __name__ == '__main__':
    while True:
        usernames = get_user_names(sheet_url)
        banned_users = []
        for U in usernames:
            if not check_user_existence(U):
                banned_users.append(U)
        
        if banned_users:
            banned_users = [x for x in banned_users if len(x)>0]
            msg_string = f"({len(banned_users)}) Banned Reddit Accounts:\n\n"
            msg_string += '\n'.join(banned_users)
            asyncio.run(send_tg_msg(chat_id,msg_string))
        else:
            asyncio.run(send_tg_msg(chat_id,"(0) Banned Reddit Accounts"))
        sleep(wait_timer*60)
