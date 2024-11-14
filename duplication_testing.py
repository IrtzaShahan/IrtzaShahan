import asyncio
import json
import logging
import os
import requests
from datetime import datetime, timedelta
from time import time
from telethon import TelegramClient, events, Button
from telethon.errors import rpcerrorlist
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Chat, Channel, ChannelParticipantsAdmins

# =================== Configuration ===================

API_ID = <your_api_id>
API_HASH = '<your_api_hash>'
BOT_TOKEN = '<your_bot_token>'
TRANSLATION_API_KEY = '<your_translation_api_key>'
OWNER_USER_ID = <your_user_id>  # Replace with your Telegram user ID

# Load the sets configuration
with open('sets_configs.json', 'r') as fp:
    sets_config = json.load(fp)

# Word meaning dictionary for specific translations
word_meaning_dictionary = {
    'Marketplace': '市場;マーケットプレイス',
    # ... (rest of your dictionary)
}

# =================== Initialize Client ===================

client = TelegramClient('bot', API_ID, API_HASH)
client.start(bot_token=BOT_TOKEN)
me = client.get_me()

# =================== Setup Logging ===================

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'console.log'

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger().addHandler(file_handler)

# =================== Helper Functions ===================

admin_cache = {}
ADMIN_CACHE_EXPIRY = timedelta(hours=5)

async def get_admins(chat_id):
    """Retrieve the list of admins for a chat, using a cache to minimize API calls."""
    if chat_id in admin_cache:
        admins, timestamp = admin_cache[chat_id]
        if datetime.now() - timestamp < ADMIN_CACHE_EXPIRY:
            return admins

    entity = await client.get_entity(chat_id)

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
        admins = [
            user.id for user in full_chat.full_chat.participants.participants
            if getattr(user, 'admin_rights', None)
        ]
    else:
        admins = []

    admin_cache[chat_id] = (admins, datetime.now())
    return admins

async def is_user_admin(chat_id, user_id):
    """Check if a user is an admin of the chat."""
    admins = await get_admins(chat_id)
    return user_id in admins

def translate_text(text, target_language, source_language):
    """Translate text using the external translation API."""
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": TRANSLATION_API_KEY
    }
    data = {
        "platform": "api",
        "from": source_language if source_language != "zh-Hant_TW" else None,
        "to": target_language,
        "data": text
    }
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()

    if 'result' in response_json:
        translated_text = response_json['result']
        for word, translation in word_meaning_dictionary.items():
            if word in text:
                original, replacement = translation.split(';')
                translated_text = translated_text.replace(original, replacement)
        return translated_text
    else:
        logging.warning(f"Translation API error: {response.text}")
        return None

def update_sets():
    """Update the sets configuration file."""
    with open('sets_configs.json', 'w') as fp:
        json.dump(sets_config, fp, indent=2)

def remove_set(project_name):
    """Remove a project (set) from the configuration."""
    if project_name in sets_config:
        del sets_config[project_name]
        update_sets()
        return f"Project '{project_name}' removed successfully."
    else:
        return f"Project '{project_name}' does not exist."

def remove_group(project_name, group_id):
    """Remove a group from a project."""
    project = sets_config.get(project_name)
    if project and group_id in project["channels_list"]:
        project["channels_list"].remove(group_id)
        project["langs"].pop(group_id, None)
        project["flags"].pop(group_id, None)
        update_sets()
        return f"Group ID '{group_id}' removed from project '{project_name}' successfully."
    else:
        return f"Group ID '{group_id}' not found in project '{project_name}'."

def list_sets():
    """List all projects and their groups."""
    if not sets_config:
        return "No projects found."
    result = ["Projects and Groups:"]
    for project_name, project_details in sets_config.items():
        result.append(f"Project: {project_name}")
        if not project_details["channels_list"]:
            result.append("  No groups added.")
        else:
            for group_id in project_details["channels_list"]:
                group_lang = project_details["langs"].get(group_id, "N/A")
                group_flag = project_details["flags"].get(group_id, "N/A")
                result.append(f"  Group ID: {group_id}, Language: {group_lang}, Flag: {group_flag}")
        result.append("")  # Empty line for spacing
    return "\n".join(result).strip()

def find_set_id_for_group(group_id):
    """Find the project (set) ID that a group belongs to."""
    for set_id, config in sets_config.items():
        if str(group_id) in config['channels_list']:
            return set_id
    logging.warning(f"Group ID '{group_id}' not found in any project.")
    return None

def get_sender_link(sender):
    """Construct a hyperlink to the sender's Telegram profile."""
    sender_name = ' '.join(filter(None, [sender.first_name, sender.last_name])).strip()
    sender_username = sender.username or ''
    if sender_name:
        return f"[{sender_name}](https://t.me/{sender_username})"
    elif sender_username:
        return f"[{sender_username}](https://t.me/{sender_username})"
    else:
        return "[Unknown](https://t.me/)"

# =================== Command Handlers ===================

@client.on(events.NewMessage(pattern='/set_button_data'))
async def set_button_data(event):
    """Set the button text and URL for messages."""
    try:
        _, url, text = event.message.text.split(' ', 2)
        btn = {'txt': text.strip(), 'url': url.strip()}
        with open('btn.json', 'w') as fp:
            json.dump(btn, fp)
        await event.respond("Button text and URL successfully updated.", reply_to=event.message)
    except ValueError:
        await event.respond(
            "Incorrect format. Use:\n"
            "/set_button_data <url> <button text>\n"
            "Example:\n"
            "/set_button_data www.example.com Click Here",
            reply_to=event.message
        )

@client.on(events.NewMessage(pattern='/set_project '))
async def new_project(event):
    """Create a new project (set)."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    try:
        _, project_name = event.message.text.split(' ', 1)
        if project_name in sets_config:
            await event.reply(f"Project '{project_name}' already exists.")
        else:
            sets_config[project_name] = {
                "channels_list": [],
                "langs": {},
                "flags": {},
                "filters": {}
            }
            update_sets()
            await event.reply(f"New project '{project_name}' added successfully.")
    except ValueError:
        await event.reply("Please provide a project name.")

@client.on(events.NewMessage(pattern='/removeproject '))
async def remove_set_command(event):
    """Remove an existing project (set)."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    try:
        _, project_name = event.message.text.split(' ', 1)
        result = remove_set(project_name)
        await event.reply(result)
    except ValueError:
        await event.reply("Please provide a project name.")

@client.on(events.NewMessage(pattern='/addgroup '))
async def add_group(event):
    """Add a group to a project."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    try:
        _, details = event.message.text.split(' ', 1)
        project_name, group_id, group_language, flag, group_invite_link = map(str.strip, details.split(','))
        project = sets_config.get(project_name)
        if not project:
            await event.reply(f"Project '{project_name}' does not exist.")
            return
        project["channels_list"].append(group_id)
        project["langs"][group_id] = group_language
        project["flags"][group_id] = f"[{flag}]({group_invite_link})"
        update_sets()
        await event.reply(f"Group added to project '{project_name}' successfully.")
    except ValueError:
        await event.reply(
            "Incorrect format. Use:\n"
            "/addgroup <project_name>, <group_id>, <group_language>, <flag>, <group_invite_link>"
        )

@client.on(events.NewMessage(pattern='/removegroup '))
async def remove_group_command(event):
    """Remove a group from a project."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    try:
        _, details = event.message.text.split(' ', 1)
        project_name, group_id = map(str.strip, details.split(','))
        result = remove_group(project_name, group_id)
        await event.reply(result)
    except ValueError:
        await event.reply(
            "Incorrect format. Use:\n"
            "/removegroup <project_name>, <group_id>"
        )

@client.on(events.NewMessage(pattern='/listprojects'))
async def list_sets_command(event):
    """List all projects and their groups."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    result = list_sets()
    await event.reply(result)

@client.on(events.NewMessage(pattern='/addfilter '))
async def add_filter(event):
    """Add a filter to the current project's filters."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        await event.reply("This group is not associated with any project.")
        return

    try:
        _, text = event.message.text.split(' ', 1)
        command, reply = text.strip().split(' ', 1)
        command = command.strip('"').lower()
        sets_config[set_id]['filters'][command] = reply.strip()
        update_sets()
        await event.reply(f"Filter '{command}' added successfully.")
    except ValueError:
        await event.reply("Incorrect format. Use:\n/addfilter <keyword> <reply>")

@client.on(events.NewMessage(pattern='/stopfilter '))
async def remove_filter(event):
    """Remove a filter from the current project's filters."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        await event.reply("This group is not associated with any project.")
        return

    try:
        _, command = event.message.text.split(' ', 1)
        command = command.strip('"').lower()
        if command in sets_config[set_id]['filters']:
            del sets_config[set_id]['filters'][command]
            update_sets()
            await event.reply(f"Filter '{command}' removed.")
        else:
            await event.reply("Filter not found.")
    except ValueError:
        await event.reply("Please provide the filter keyword to remove.")

@client.on(events.NewMessage(pattern='/stopall'))
async def remove_all_filters(event):
    """Remove all filters from the current project."""
    c_id = event.chat_id
    user_id = event.sender_id
    if not await is_user_admin(c_id, user_id):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        await event.reply("This group is not associated with any project.")
        return

    sets_config[set_id]['filters'].clear()
    update_sets()
    await event.reply("All filters removed.")

@client.on(events.NewMessage(pattern='/filters'))
async def list_filters(event):
    """List all filters for the current project."""
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        await event.reply("This group is not associated with any project.")
        return

    filters = sets_config[set_id]['filters']
    if filters:
        commands_list = "\n".join([f" - {cmd}" for cmd in filters])
        await event.reply(f"List of filters:\n{commands_list}")
    else:
        await event.reply("No filters set.")

@client.on(events.NewMessage(pattern='/id'))
async def id_handler(event):
    """Return the ID of the current chat."""
    await event.reply(f"This chat ID is: {event.chat_id}")

# =================== Event Handlers ===================

@client.on(events.MessageEdited)
async def edit_handler(event):
    """Handle message edits by propagating the changes."""
    if event.text and event.text.startswith('/') or event.out:
        return

    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        return

    n_l = sets_config[set_id]['channels_list'][:]
    langs = sets_config[set_id]['langs']
    flags = sets_config[set_id]['flags']
    n_l.remove(c_id)

    await asyncio.sleep(1)  # Small delay to batch multiple edits

    with open('table.json', 'r') as fp:
        data = json.load(fp)

    original_message_id = f"{c_id};{event.id}"
    if event.text:
        translated_texts = {}
        for out in n_l:
            msg_id = data.get(original_message_id, {}).get(out)
            if not msg_id:
                continue

            completion = translate_text(event.text.strip(), langs[out], langs[c_id])
            if not completion:
                continue

            sender = await event.get_sender()
            sender_link = get_sender_link(sender)
            header = f"{flags[str(c_id)]} {sender_link}"

            try:
                await client.edit_message(
                    int(out),
                    msg_id,
                    f"{header}\n{completion.strip()}",
                    link_preview=False
                )
            except rpcerrorlist.MessageNotModifiedError:
                continue
            except Exception as e:
                logging.error(f"Error editing message: {e}")

@client.on(events.MessageDeleted)
async def deleted_message_listener(event):
    """Handle message deletions by deleting the corresponding messages."""
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        return

    n_l = sets_config[set_id]['channels_list'][:]
    n_l.remove(c_id)

    with open('table.json', 'r') as fp:
        data = json.load(fp)

    for deleted_id in event.deleted_ids:
        original_message_id = f"{c_id};{deleted_id}"
        for out in n_l:
            msg_id = data.get(original_message_id, {}).get(out)
            if msg_id:
                await client.delete_messages(int(out), msg_id)

@client.on(events.ChatAction)
async def pin_msg_handler(event):
    """Handle message pins by pinning the corresponding messages."""
    if not event.is_channel:
        return

    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        return

    n_l = sets_config[set_id]['channels_list'][:]
    n_l.remove(c_id)

    if event.action_message and event.action_message.reply_to:
        with open('table.json', 'r') as fp:
            data = json.load(fp)
        original_message_id = f"{c_id};{event.action_message.reply_to.reply_to_msg_id}"

        for out in n_l:
            msg_id = data.get(original_message_id, {}).get(out)
            if msg_id:
                await client.pin_message(int(out), msg_id)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Main handler for incoming messages."""
    c_id = str(event.chat_id)
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        return

    n_l = sets_config[set_id]['channels_list'][:]
    langs = sets_config[set_id]['langs']
    flags = sets_config[set_id]['flags']
    filters = sets_config[set_id]['filters']
    n_l.remove(c_id)

    # Handle filters
    if event.text:
        text_lower = event.text.lower()
        for keyword, response in filters.items():
            if keyword in text_lower:
                await event.reply(response, link_preview=False)
                return
        if event.text.startswith('/'):
            return

    with open('table.json', 'r') as fp:
        data = json.load(fp)

    sender = await event.get_sender()
    sender_link = get_sender_link(sender)
    header = f"{flags[c_id]} {sender_link}"

    msg_key = f"{c_id};{event.id}"
    msg_val = {}

    # Load button configuration if available
    if os.path.exists('btn.json'):
        with open('btn.json', 'r') as fp:
            btn = json.load(fp)
        button = [Button.url(btn['txt'], btn['url'])]
    else:
        button = []

    for out in n_l:
        try:
            out_channel = await client.get_input_entity(int(out))
            reply_id = None
            if event.reply_to:
                original_reply_key = f"{c_id};{event.reply_to.reply_to_msg_id}"
                reply_id = data.get(original_reply_key, {}).get(out)

            if event.text:
                completion = translate_text(event.text.strip(), langs[out], langs[c_id])
                if not completion:
                    continue
                if event.media and hasattr(event.media, 'webpage'):
                    await client.send_message(
                        out_channel,
                        f"{header}\n{event.text.strip()}",
                        link_preview=False,
                        reply_to=reply_id,
                        buttons=button
                    )
                elif event.media:
                    await client.send_file(
                        out_channel,
                        event.media,
                        caption=f"{header}\n{completion.strip()}",
                        reply_to=reply_id,
                        buttons=button
                    )
                else:
                    await client.send_message(
                        out_channel,
                        f"{header}\n{completion.strip()}",
                        link_preview=False,
                        reply_to=reply_id,
                        buttons=button
                    )
            else:
                await client.send_file(
                    out_channel,
                    event.media,
                    caption=header,
                    reply_to=reply_id,
                    buttons=button
                )

            # Record the message ID mapping
            sent_message = await client.get_messages(out_channel, limit=1)
            msg_val[out] = sent_message[0].id
        except Exception as e:
            logging.error(f"Error forwarding message to {out}: {e}")

    # Update the message mapping
    if msg_val:
        data[msg_key] = msg_val
        with open('table.json', 'w') as fp:
            json.dump(data, fp, indent=2)

# =================== Start the Bot ===================

logging.info(f"Bot @{me.username} started successfully.")
client.run_until_disconnected()
