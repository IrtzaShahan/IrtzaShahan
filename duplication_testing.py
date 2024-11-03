from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# Define API credentials for both the bot and user account
API_ID = '24013882'
API_HASH = 'cd770a9021e2fa9510ba7a1564c3b81b'
BOT_TOKEN = '7778748580:AAHVrdjiPrRn3hA68KE5aLtodrh-3poj8hM'
QUOTEX_PARTNER_BOT = 'QuotexPartnerBot'
TARGET_GROUP_ID = -1002450268419

bot_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user_client = TelegramClient('user_session', API_ID, API_HASH)


async def create_unique_join_link():
    try:
        result = await bot_client(ExportChatInviteRequest(
            peer=TARGET_GROUP_ID,  # Replace with your group ID
            expire_date=None,  # Link will not expire
            usage_limit=1  # One-time use link
        ))
        return result.link
    except Exception as e:
        print(f"Error creating join link: {str(e)}")
        return None


async def start_clients():
    await user_client.start()
    print("Both bot and user clients started")




start_msg = """👋 Hi,
🌟 Welcome to the anasalivipbot 🤖 

📥 Please enter your Quotex Trader ID.
🔍 After we verify your details,  you’ll receive the VIP Group Channel link 🔗. 

 Let's Escape the Rat Race! 🚀💼."""
link_msg = """It appears that your account is not registered using my referral link. ❌

Sign up with the link below 👇
https://qxbroker.com/en/sign-up?lid=1054707

Sign Up using the above link & deposit Minimum 50$ to get entry in the VIP group.💰"""

@bot_client.on(events.NewMessage)
async def handler(event):
    if event.is_private:  # Ensure it's a private message
        user_id = event.sender_id
        message = event.message.message
        print(f"Received from user {user_id}: {message}")

        if message.startswith('/start'):
            await bot_client.send_message(user_id, start_msg)
            

        if not (message.isdigit() and len(message) == 8):
            await bot_client.send_message(user_id, "Trader ID should be an 8-digit number. Please try again.")
            return

        try:
            async with user_client.conversation(QUOTEX_PARTNER_BOT) as conv:
                await conv.send_message(message)
                response = await conv.get_response()

            if 'account closed' in response.message.lower():
                await bot_client.send_message(user_id, "You are in the waiting list & will be added soon.")
                return
            
            if 'turnover' in response.message.lower():
                # Create a unique join link for the user
                join_link = await create_unique_join_link()

                if join_link:
                    # Send the unique one-time join link to the user
                    await bot_client.send_message(user_id, f"Here is your one-time join link: {join_link}")
                else:
                    # Handle the case if there was an error creating the join link
                    await bot_client.send_message(user_id, "Sorry, there was an error creating your join link.")

            else:
                await bot_client.send_message(user_id, link_msg)
        except Exception as e:
            await bot_client.send_message(user_id, f"Error processing your request: {str(e)}")


# Start the bot and user clients
with bot_client, user_client:
    bot_client.loop.run_until_complete(start_clients())
    bot_client.run_until_disconnected()
