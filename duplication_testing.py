import asyncio
import json
import logging
import requests
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.errors import rpcerrorlist
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Chat, Channel, ChannelParticipantsAdmins

# Configuration constants
API_ID = 27626586
API_HASH = '90c8ff00f20929899e1cc2f16d63ffe1'
BOT_TOKEN = "6956671682:AAFupT71zTXr1ia025W4DND9I8vkNjfXNF0"
API_KEY = "a_Srrj954JR2Kp5RYULdKL3tCNy1sd5UoG6SDFlPRuAmeos7BJePiTJ5ESjSVQfEMWoo1ZPrnZdr5JlaIz"

# Word replacement dictionary
WORD_MEANING_DICTIONARY = {
    'Marketplace': '市場;マーケットプレイス',
    'Rond': '輪舞;Rond',
    'ROND': '輪舞;ROND',
    'ronds': 'ロンズ;ronds',
    'RONDS': '身動き;RONDS',
    'mrond': 'ムロンド;mrond',
    'GENSOKISHI': '源生史;GENSOKISHI',
    'Genso': 'ジンソ;Genso',
    'GENSO': '玄武岩;GENSO',
    'gensokishi': '源⽣史;gensokishi',
    'GensoKishi': '⽞武岸;GensoKishi',
    'Gensokishi': '源生志;Gensokishi',
    'CS': 'セシウム;CS',
    'MV': 'マービー・エム;MV',
    'mv': '品種;mv',
    'MMV': 'ミリ秒;MMV',
    'mmv': 'ミリ秒;mmv'
}

# Initialize the Telegram client
client = TelegramClient('bot', API_ID, API_HASH)
client.start(bot_token=BOT_TOKEN)
me = client.get_me()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('console.log'),
        logging.StreamHandler()
    ]
)

# Load configuration files
with open('sets_configs.json', 'r') as fp:
    sets_config = json.load(fp)

with open('btn.json', 'r') as fp:
    button_config = json.load(fp)

# Cache for admin lists
ADMIN_CACHE = {}
ADMIN_CACHE_EXPIRY = timedelta(hours=5)

# Global message counter
message_counter = 0


async def get_admins(chat_id):
    """
    Get the list of admin IDs for a given chat.
    """
    if chat_id in ADMIN_CACHE:
        admins, timestamp = ADMIN_CACHE[chat_id]
        if datetime.now() - timestamp < ADMIN_CACHE_EXPIRY:
            return admins

    entity = await client.get_entity(chat_id)
    admins = []

    if isinstance(entity, Channel):
        result = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsAdmins(),
            offset=0,
            limit=100,
            hash=0
        ))
        admins = [user.id for user in result.users]
    elif isinstance(entity, Chat):
        full_chat = await client(GetFullChatRequest(chat_id))
        admins = [user.id for user in full_chat.full_chat.participants.participants if user.admin_rights]

    ADMIN_CACHE[chat_id] = (admins, datetime.now())
    return admins


async def is_user_admin(chat_id, user_id):
    """
    Check if a user is an admin in a given chat.
    """
    admins = await get_admins(chat_id)
    return user_id in admins


def translate_text(text, target_language, api_key, source_language):
    """
    Translate text using an external API and perform word replacements.
    """
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    data = {
        "platform": "api",
        "from": source_language if source_language != "zh-Hant_TW" else None,
        "to": target_language,
        "data": text
    }
    response = requests.post(url, headers=headers, json=data).json()

    if 'result' in response:
        translated_text = response['result']
        for word, meanings in WORD_MEANING_DICTIONARY.items():
            if word in text:
                source_word, target_word = meanings.split(';')
                translated_text = translated_text.replace(source_word, target_word)
        return translated_text
    else:
        logging.warning(response)
        return False


def update_sets(data):
    """
    Update the sets configuration file.
    """
    with open('sets_configs.json', 'w') as fp:
        json.dump(data, fp, indent=1)
    global sets_config
    sets_config = data


def remove_set(project_name):
    """
    Remove a project from the sets configuration.
    """
    if project_name not in sets_config:
        return f"Project '{project_name}' does not exist."
    del sets_config[project_name]
    update_sets(sets_config)
    return f"Project '{project_name}' removed successfully."


def remove_group(project_name, group_id):
    """
    Remove a group from a project in the sets configuration.
    """
    if project_name not in sets_config:
        return f"Project '{project_name}' does not exist."
    if group_id not in sets_config[project_name]["channels_list"]:
        return f"Group ID '{group_id}' not found in project '{project_name}'."

    sets_config[project_name]["channels_list"].remove(group_id)
    del sets_config[project_name]["langs"][group_id]
    del sets_config[project_name]["flags"][group_id]
    update_sets(sets_config)
    return f"Group ID '{group_id}' removed from project '{project_name}' successfully."


def list_sets():
    """
    List all projects and their associated groups.
    """
    if not sets_config:
        return "No projects found."

    result = "Projects and Groups:\n"
    for project_name, project_details in sets_config.items():
        result += f"Project: {project_name}\n"
        if not project_details["channels_list"]:
            result += "  No groups added.\n"
        else:
            for group_id in project_details["channels_list"]:
                group_lang = project_details["langs"].get(group_id, "N/A")
                group_flag = project_details["flags"].get(group_id, "N/A")
                result += f"  Group ID: {group_id}, Language: {group_lang}, Flag: {group_flag}\n"
        result += "\n"
    return result.strip()


def find_set_id_for_group(group_id):
    """
    Find the project ID for a given group ID.
    """
    for set_id, config in sets_config.items():
        if str(group_id) in config['channels_list']:
            return set_id
    logging.warning(f'Group ID not found in any projects: {group_id}')
    return None


def get_sender_link(sender):
    """
    Generate a clickable link for the message sender.
    """
    sender_name = ''
    if sender:
        if hasattr(sender, 'first_name') and sender.first_name:
            sender_name = sender.first_name + ' '
        if hasattr(sender, 'last_name') and sender.last_name:
            sender_name += sender.last_name
        if not sender_name and hasattr(sender, 'username') and sender.username:
            sender_name = sender.username
        sender_link = f"[{sender_name.strip()}](https://t.me/{sender.username})"
    else:
        sender_link = ''
    return sender_link


def load_button_config():
    """
    Load the button configuration from file.
    """
    with open('btn.json', 'r') as fp:
        return json.load(fp)


def load_message_table():
    """
    Load the message ID mapping table from file.
    """
    try:
        with open('table.json', 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}


def save_message_table(data):
    """
    Save the message ID mapping table to file.
    """
    with open('table.json', 'w') as fp:
        json.dump(data, fp, indent=1)


@client.on(events.NewMessage(pattern='/set_button_data'))
async def set_button_data(event):
    """
    Handler for /set_button_data command.
    """
    txt = event.message.text
    parts = txt.split(maxsplit=2)

    if len(parts) != 3:
        await event.respond("Please use the format:\n/set_button_data <url> <button text>", reply_to=event.message)
        return

    _, url, text = parts
    btn = {'txt': text, 'url': url}
    with open('btn.json', 'w') as fp:
        json.dump(btn, fp)
    await event.respond("Button text and URL successfully updated.", reply_to=event.message)


@client.on(events.NewMessage(pattern='/set_project '))
async def new_project(event):
    """
    Handler for /set_project command.
    """
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    _, project_name = event.message.text.split(maxsplit=1)

    if project_name in sets_config:
        await event.reply(f"Project name '{project_name}' already exists. Please choose a unique one.")
    else:
        sets_config[project_name] = {
            "channels_list": [],
            "langs": {},
            "flags": {},
            "filters": {}
        }
        update_sets(sets_config)
        await event.reply(f"New project named '{project_name}' added successfully.")


@client.on(events.NewMessage(pattern='/removeproject '))
async def remove_set_command(event):
    """
    Handler for /removeproject command.
    """
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    _, project_name = event.message.text.split(maxsplit=1)
    result = remove_set(project_name)
    await event.reply(result)


@client.on(events.NewMessage(pattern='/addgroup '))
async def add_group(event):
    """
    Handler for /addgroup command.
    """
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    try:
        _, details = text.split(maxsplit=1)
        project_name, group_id, group_language, flag, group_invite_link = [x.strip() for x in details.split(',')]
    except ValueError:
        await event.reply("Please use the format:\n/addgroup <project_name>, <group_id>, <group_language>, <flag>, <group_invite_link>")
        return

    if project_name not in sets_config:
        await event.reply(f"Project '{project_name}' does not exist. Please create it first.")
    else:
        sets_config[project_name]["channels_list"].append(group_id)
        sets_config[project_name]["langs"][group_id] = group_language
        sets_config[project_name]["flags"][group_id] = f"[{flag}]({group_invite_link})"
        update_sets(sets_config)
        await event.reply(f"Group added to project '{project_name}' successfully.")


@client.on(events.NewMessage(pattern='/removegroup '))
async def remove_group_command(event):
    """
    Handler for /removegroup command.
    """
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    try:
        _, details = text.split(maxsplit=1)
        project_name, group_id = [x.strip() for x in details.split(',')]
    except ValueError:
        await event.reply("Please use the format:\n/removegroup <project_name>, <group_id>")
        return

    result = remove_group(project_name, group_id)
    await event.reply(result)


@client.on(events.NewMessage(pattern='/listprojects'))
async def list_sets_command(event):
    """
    Handler for /listprojects command.
    """
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    result = list_sets()
    await event.reply(result)


@client.on(events.NewMessage(pattern='/addfilter '))
async def add_filter(event):
    """
    Handler for /addfilter command.
    """
    c_id = str(event.chat_id)
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    try:
        _, command_and_reply = event.message.text.split(maxsplit=1)
        command, reply = command_and_reply.split(maxsplit=1)
        command = command.strip('"').lower()
        sets_config[set_id]['filters'][command] = reply
        update_sets(sets_config)
        await event.reply(f"Filter for '{command}' added successfully.")
    except ValueError:
        await event.reply("Please use the format:\n/addfilter <command> <reply>")


@client.on(events.NewMessage(pattern='/stopfilter '))
async def remove_filter(event):
    """
    Handler for /stopfilter command.
    """
    c_id = str(event.chat_id)
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    command = event.message.text.split(maxsplit=1)[1].strip('"').lower()
    if command in sets_config[set_id]['filters']:
        del sets_config[set_id]['filters'][command]
        update_sets(sets_config)
        await event.reply(f"Filter for '{command}' removed.")
    else:
        await event.reply("Filter not found.")


@client.on(events.NewMessage(pattern='/stopall'))
async def remove_all_filters(event):
    """
    Handler for /stopall command.
    """
    c_id = str(event.chat_id)
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    sets_config[set_id]['filters'].clear()
    update_sets(sets_config)
    await event.reply("All filters removed.")


@client.on(events.NewMessage(pattern='/filters'))
async def list_filters(event):
    """
    Handler for /filters command.
    """
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    filters = sets_config[set_id]['filters']
    if filters:
        commands_list = "\n".join([f" - {cmd}" for cmd in filters])
        await event.reply(f"List of filters:\n{commands_list}")
    else:
        await event.reply("No filters set.")


@client.on(events.NewMessage(pattern='/id'))
async def id_handler(event):
    """
    Handler for /id command.
    """
    await event.reply(f"This chat ID is: {event.chat_id}")


@client.on(events.MessageEdited)
async def edit_handler(event):
    """
    Handler for edited messages.
    """
    if event.text and event.text.startswith('/') or event.out:
        return

    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    n_l = sets_config[set_id]['channels_list'][:]
    langs = sets_config[set_id]['langs']
    flags = sets_config[set_id]['flags']

    try:
        n_l.remove(c_id)
    except ValueError:
        logging.error("Chat ID not found in project channels.")
        return

    await asyncio.sleep(35)
    data = load_message_table()

    if event.text:
        for out in n_l:
            msg_id = data.get(f"{c_id};{event.id}", {}).get(out)
            if not msg_id:
                logging.warning(f"Failed to find original message being edited: {c_id};{event.id}:{out}")
                continue

            translated_text = translate_text(event.text.strip(), langs[out], API_KEY, langs[c_id])
            if not translated_text:
                continue

            try:
                original_message = await client.get_messages(int(out), ids=msg_id)
                original_text_line1 = original_message.text.split('\n')[0] if original_message else ''
                if not original_text_line1:
                    sender = await event.get_sender()
                    sender_link = get_sender_link(sender)
                    original_text_line1 = f"{flags[c_id]} {sender_link}\n"
                await client.edit_message(
                    int(out),
                    msg_id,
                    f"{original_text_line1}\n{translated_text.strip()}",
                    link_preview=False
                )
            except rpcerrorlist.MessageNotModifiedError:
                logging.info("Edited message is the same as the original.")
            except Exception as e:
                logging.error(e)


@client.on(events.MessageDeleted)
async def deleted_message_listener(event):
    """
    Handler for deleted messages.
    """
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    n_l = sets_config[set_id]['channels_list'][:]
    try:
        n_l.remove(c_id)
    except ValueError:
        logging.error("Chat ID not found in project channels.")
        return

    await asyncio.sleep(10)
    data = load_message_table()

    for out in n_l:
        msg_id = data.get(f"{c_id};{event.deleted_id}", {}).get(out)
        if msg_id:
            await client.delete_messages(int(out), msg_id)


@client.on(events.ChatAction)
async def pin_msg_handler(event):
    """
    Handler for pinned messages.
    """
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    await asyncio.sleep(120)
    if event.action_message and event.action_message.reply_to:
        data = load_message_table()
        n_l = sets_config[set_id]['channels_list'][:]
        n_l.remove(c_id)

        for out in n_l:
            msg_id = data.get(f"{c_id};{event.action_message.reply_to.reply_to_msg_id}", {}).get(out)
            if msg_id:
                await client.pin_message(int(out), msg_id)


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """
    Main handler for incoming messages.
    """
    global message_counter

    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('Received message outside of any configured projects.')
        return

    n_l = sets_config[set_id]['channels_list'][:]
    langs = sets_config[set_id]['langs']
    flags = sets_config[set_id]['flags']
    filters = sets_config[set_id]['filters']

    if event.text:
        text_lower = event.text.lower()
        for command, reply in filters.items():
            if command in text_lower:
                await event.reply(reply, link_preview=False)
                return
        if event.text.startswith('/'):
            return

    try:
        n_l.remove(c_id)
        msg_key = f"{c_id};{event.id}"
        msg_val = {}
    except ValueError:
        logging.error("Chat ID not found in project channels.")
        return

    data = load_message_table()
    sender = await event.get_sender()
    sender_link = get_sender_link(sender)
    button = [Button.url(button_config['txt'], button_config['url'])]

    message_counter += 1

    for out in n_l:
        reply_id = None
        if event.reply_to:
            reply_key = f"{c_id};{event.reply_to.reply_to_msg_id}"
            reply_id = data.get(reply_key, {}).get(out)

        out_channel = await client.get_input_entity(int(out))

        if event.text:
            translated_text = translate_text(event.text.strip(), langs[out], API_KEY, langs[c_id])
            if not translated_text:
                logging.error(f"Translation failed for message: {event.text.strip()}")
                continue

            caption = f"{flags[c_id]} {sender_link}\n{translated_text.strip()}"
            try:
                if event.media:
                    r = await client.send_file(
                        out_channel,
                        event.media,
                        caption=caption,
                        reply_to=reply_id,
                        buttons=button
                    )
                else:
                    r = await client.send_message(
                        out_channel,
                        caption,
                        link_preview=False,
                        reply_to=reply_id,
                        buttons=button
                    )
                msg_val[out] = r.id
            except Exception as e:
                logging.error(f"Error sending message to {out}: {e}")
        else:
            try:
                r = await client.send_file(
                    out_channel,
                    event.media,
                    caption=f"{flags[c_id]} {sender_link}",
                    buttons=button
                )
                msg_val[out] = r.id
            except Exception as e:
                logging.error(f"Error sending media to {out}: {e}")

    data[msg_key] = msg_val
    save_message_table(data)
    logging.info('Message forwarded successfully.')


logging.info(f'Bot {me.username} started and is forwarding messages.')

client.run_until_disconnected()
