import openai
import logging
import telegram
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Initialize the OpenAI API client with your API key
openai.api_key = "YOUR_OPENAI_API_KEY"
model_id = "gpt-3.5-turbo"

# Initialize the logger
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for user conversations
user_conversations = {}


async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    nftstring = update.message.text

    substring = re.sub(r"^\W*\w+\W*", "", nftstring)
    print(substring)

    # Append the user's message to the conversation
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    user_conversations[user_id].append(f"User: {substring}")

    system_intel = "You are the Bot, a product of the team and here to answer questions as needed."
    prompt = "\n".join(user_conversations[user_id])

    # Use GPT-3.5-turbo for chat completion
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": prompt},
        ],
    )

    bot_response = response["choices"][0]["message"]["content"]
    user_conversations[user_id].append(f"Bot: {bot_response}")

    await update.message.reply_text(bot_response)


def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("ai", ai))

app.run_polling()
