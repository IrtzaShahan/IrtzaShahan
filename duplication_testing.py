import asyncio,json,os,logging,requests
from datetime import datetime, timedelta
from time import time
from telethon import TelegramClient, events, Button
from telethon.errors import rpcerrorlist
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Chat, Channel, ChannelParticipantsAdmins


word_meaning_dictionary = {'Marketplace':'市場;マーケットプレイス',
                           'Rond':'輪舞;Rond',
                           'ROND':'輪舞;ROND',
                           'ronds':'ロンズ;ronds',
                           'RONDS':'身動き;RONDS',
                           'mrond':'ムロンド;mrond',
                           'GENSOKISHI':'源生史;GENSOKISHI',
                           'Genso':'ジンソ;Genso',
                           'GENSO':'玄武岩;GENSO',
                           'gensokishi':'源⽣史;gensokishi',
                           'GensoKishi':'⽞武岸;GensoKishi',
                           'Gensokishi':'源生志;Gensokishi',
                           'CS':'セシウム;CS',
                           'MV':'マービー・エム;MV',
                           'mv':'品種;mv',
                           'MMV':'ミリ秒;MMV',
                           'mmv':'ミリ秒;mmv'
                           }

api_id = 27626586
api_hash = '90c8ff00f20929899e1cc2f16d63ffe1'
api_key = "a_Srrj954JR2Kp5RYULdKL3tCNy1sd5UoG6SDFlPRuAmeos7BJePiTJ5ESjSVQfEMWoo1ZPrnZdr5JlaIz"
with open('bot_token.txt','r') as fp:
    bot_token_hash = fp.read()


def generate_message_link(c_id, message_id):
    if str(c_id).startswith('-100'):
        chat_id_num = str(c_id)[4:]
    else:
        chat_id_num = str(c_id).lstrip('-')
    return f"https://t.me/c/{chat_id_num}/{message_id}"


with open('sets_configs.json','r') as fp:
    sets_config=json.load(fp)

client = TelegramClient('bot', api_id, api_hash)
client.start(bot_token=bot_token_hash)
me = client.get_me()

# set up logging
format_str = '%(asctime)s - %(levelname)s - %(message)s'
file_name = 'console.log'

logging.basicConfig(level=logging.INFO, format=format_str)

# Create a file handler
file_handler = logging.FileHandler(file_name)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(format_str))

# Add the console handler to the root logger
logging.getLogger().addHandler(file_handler)


admin_cache = {}
ADMIN_CACHE_EXPIRY = timedelta(hours=5)

async def get_admins(chat_id):
    # Check if the admin list is cached and still valid
    if chat_id in admin_cache:
        admins, timestamp = admin_cache[chat_id]
        if datetime.now() - timestamp < ADMIN_CACHE_EXPIRY:
            return admins

    entity = await client.get_entity(chat_id)

    if isinstance(entity, Channel):
        # Fetch the list of admins for a channel (supergroup)
        result = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsAdmins(),
            offset=0,
            limit=100,
            hash=0
        ))
        admins = [user.id for user in result.users]
    elif isinstance(entity, Chat):
        # Fetch the list of admins for a regular group
        full_chat = await client(GetFullChatRequest(chat_id))
        admins = [user.id for user in full_chat.full_chat.participants.participants if user.admin_rights]


    # Update the cache
    admin_cache[chat_id] = (admins, datetime.now())

    return admins

async def is_user_admin(chat_id, user_id):
    admins = await get_admins(chat_id)
    return user_id in admins


def translate_text(text, target_language, api_key,source_language):
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"

    headers = {"accept": "application/json", "content-type": "application/json", "Authorization": api_key}

    if source_language == "zh-Hant_TW":
        data = {"platform": "api", "to": target_language, "data": text}
    else:
        data = {"platform": "api", "from": source_language, "to": target_language, "data": text}

    response = requests.post(url, headers=headers, json=data)

    if 'result' in response.json():
        translated_text = response.json()['result']
        for word in word_meaning_dictionary:
            if word in text:
                translated_text = translated_text.replace(word_meaning_dictionary[word].split(';')[0],word_meaning_dictionary[word].split(';')[1])
        return translated_text
    else:
        logging.warning(response.text)
        return False

def update_sets(data):
    with open('sets_configs.json','w') as fp:
        json.dump(data,fp,indent=1)
    global sets_config
    with open('sets_configs.json','r') as fp:
        sets_config=json.load(fp)

def remove_set(project_name):
    if project_name not in sets_config:
        return f"Project '{project_name}' does not exist."

    # Remove the entire project
    del sets_config[project_name]

    # Update the JSON file
    update_sets(sets_config)
    return f"Project '{project_name}' removed successfully."

def remove_group(project_name, group_id):
    if project_name not in sets_config:
        return f"Project '{project_name}' does not exist."
    if group_id not in sets_config[project_name]["channels_list"]:
        return f"Group ID '{group_id}' not found in project '{project_name}'."

    # Remove group details from the project
    sets_config[project_name]["channels_list"].remove(group_id)
    del sets_config[project_name]["langs"][group_id]
    del sets_config[project_name]["flags"][group_id]

    # Update the JSON file
    update_sets(sets_config)
    return f"Group ID '{group_id}' removed from project '{project_name}' successfully."

def list_sets():
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


def find_object_with_key_value(data, key, value):
    for parent_key, parent_value in data.items():
        if key in parent_value and parent_value[key] == value:
            return parent_key, parent_value
    logging.warning(f"key,val '{key},{value}' not found")
    return 'None','None;None'

def find_set_id_for_group(group_id):
    for set_id, config in sets_config.items():
        if str(group_id) in config['channels_list']:
            return set_id
    logging.warning(f'group_id not found in any channels {group_id}')
    return None


def get_sender_link(sender):
    sender_name = ''
    if sender:
        if hasattr(sender,'first_name') and sender.first_name:
            sender_name =  sender.first_name+' '
        if hasattr(sender,'last_name') and sender.last_name:
            sender_name += sender.last_name
        if (not sender_name) and hasattr(sender,'username') and sender.username:
            sender_name = sender.username
        sender_link = f"[{sender_name}](https://t.me/{sender.username})"
    else:
        sender_link = ''
    return sender_link


message_counter = 0

@client.on(events.NewMessage(pattern='/set_button_data'))
async def set_button_data(event):
##    if event.sender_id != 6345455034:
##        await event.respond("You are not eligible for this action.", reply_to=event.message)
##        return

    txt = event.message.text

    format_correct = len(txt.split()) > 2

    if format_correct:
        li = txt.split(" ", 2)
        url = li[1]
        text = li[2]
        btn = {'txt': text, 'url': url}
        with open('btn.json', 'w') as fp:
            json.dump(btn, fp)
        await event.respond("Button text and URL successfully updated.", reply_to=event.message)
    else:
        await event.respond("Please send the command in correct format like this:\n\"command url button text\"\n\nFor example:\n/set_button_data www.youtube.com sample button text", reply_to=event.message)


@client.on(events.NewMessage(pattern='/set_project '))
async def new_project(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    command, project_name = text.split(maxsplit=1)
    data = sets_config
    if project_name in sets_config:
        await event.reply(f"project name '{project_name}' already exists. Please choose a unique one.")
    else:
        sets_config[project_name] = {
            "channels_list": [],
            "langs": {},
            "flags": {},
            "filters": {}
        }
        update_sets(sets_config)
        await event.reply(f"New Project named '{project_name}' added successfully.")

@client.on(events.NewMessage(pattern='/removeproject '))
async def remove_set_command(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    command, project_name = text.split(maxsplit=1)

    result = remove_set(project_name)
    await event.reply(result)

@client.on(events.NewMessage(pattern='/addgroup '))
async def add_group(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    command, details = text.split(maxsplit=1)
    try:
        project_name, group_id, group_language, flag, group_invite_link = [x.strip() for x in details.split(',')]
    except:
        await event.reply(f"command is not correctly used please use below format and don't forget to use the commas\n/addgroup <project_name>, <group_id>, <group_language>, <flag>, <group_invite_link>")
        return

    if project_name not in sets_config:
        await event.reply(f"Project '{project_name}' does not exist. Please create it first.")
    else:
        # Add group details to the project
        sets_config[project_name]["channels_list"].append(group_id)
        sets_config[project_name]["langs"][group_id] = group_language.strip()
        sets_config[project_name]["flags"][group_id] = f"[{flag}]({group_invite_link})"
        # Update the JSON file with the new group details
        update_sets(sets_config)
        await event.reply(f"Group added to project '{project_name}' successfully.")

@client.on(events.NewMessage(pattern='/removegroup '))
async def remove_group_command(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    text = event.message.text
    command, details = text.split(maxsplit=1)
    try:
        project_name, group_id = [x.strip() for x in details.split(',')]
    except:
        await event.reply(f"Command is not correctly used. Please use the format:\n/removegroup <project_name>, <group_id>")
        return

    result = remove_group(project_name, group_id)
    await event.reply(result)

@client.on(events.NewMessage(pattern='/listprojects'))
async def list_sets_command(event):
    c_id = event.chat_id
    user_id = event.sender_id

    # Check if the user is an admin or the specific user (279679219)
    if (not user_id == 5587063896) and (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    # Get the list of sets
    result = list_sets()
    await event.reply(result)


@client.on(events.NewMessage(pattern='/addfilter '))
async def add_filter(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    text = event.message.text.split(maxsplit=1)
    command, reply = text[1].split(maxsplit=1)
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]  # Remove quotes for phrases
    sets_config[set_id]['filters'][command.lower()] = reply
    update_sets(sets_config)
    await event.reply(f"filter for '{command}' added successfully.")

@client.on(events.NewMessage(pattern='/stopfilter '))
async def remove_filter(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    command = event.message.text.split(maxsplit=1)[1]
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]  # Remove quotes for phrases

    if command.lower() in sets_config[set_id]['filters']:
        del sets_config[set_id]['filters'][command.lower()]
        update_sets(sets_config)
        await event.reply(f"filter for '{command}' removed.")
    else:
        await event.reply("filter not found.")

@client.on(events.NewMessage(pattern='/stopall'))
async def remove_all_filters(event):
    c_id = event.chat_id
    user_id = event.sender_id
    if (not user_id == 279679219) and (not await is_user_admin(c_id, user_id)):
        await event.reply("You need to be an admin to use this command.")
        return

    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    sets_config[set_id]['filters'].clear()
    update_sets(sets_config)
    await event.reply("All filters removed.")

@client.on(events.NewMessage(pattern='/filters'))
async def list_filters(event):
    c_id =f"{event.chat_id}"
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    if sets_config[set_id]['filters']:
        commands_list = "\n".join([f" - {cmd}" for cmd in sets_config[set_id]['filters']])
        await event.reply(f"List of filters:\n{commands_list}")
    else:
        await event.reply("No filters set.")

@client.on(events.NewMessage(pattern='/id'))
async def id_handler(event):
    await event.reply(f"this channel/group id is: {event.chat_id}")

@client.on(events.MessageEdited)
async def edit_handler(message):
    if message.text and message.text.startswith('/') or message.out:
        return

    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
        langs = sets_config[set_id]['langs']
        flag = sets_config[set_id]['flags'][str(c_id)]
    else:
        logging.error('rcvd message out of any provided sets')
        return

    # Extract the flag emoji from flags[str(c_id)]
    flag_emoji = flag.split(']')[0][1:]

    # Generate the message link
    message_link = generate_message_link(c_id, message.id)

    # Construct the new flag link
    flag_link = f"[{flag_emoji}]({message_link})"

    try:
        n_l.remove(c_id)
    except Exception as e:
        logging.error("fatal error")
        logging.error(e)
        return
    await asyncio.sleep(35)
    with open('table.json','r') as fp:
        data = json.load(fp)

    if message.text:
        try:
            for out in n_l:
                try:
                    msg_id = data[f"{c_id};{message.id}"][out]
                except KeyError:
                    msg_id= None
                    logging.warning(f"failed to find original message being edited, {c_id};{message.id}:{out}")
                    continue

                completion = translate_text(message.text.strip(), langs[out], api_key,langs[c_id])

                try:
                    original_message = await client.get_messages(int(out), ids=msg_id)
                    original_text_line1 = original_message.text.split('\n')[0]
                    if not original_message:
                        sender = await message.get_sender()
                        sender_link = get_sender_link(sender)
                        original_text_line1 = f"{flag_link} {sender_link}\n"
                except:
                    sender = await message.get_sender()
                    sender_link = get_sender_link(sender)
                    original_text_line1 = f"{flag_link} {sender_link}\n"


                await client.edit_message(int(out), msg_id, f"{original_text_line1}\n{completion.strip()}",link_preview=False)
        except rpcerrorlist.MessageNotModifiedError:
            logging.info("edited message is same as original")
            return
        except Exception as e:
            logging.error(e)
        else:
            logging.info('A msg edited succesfully')


@client.on(events.MessageDeleted)
async def deleted_message_listener(message):
    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
    else:
        logging.error('rcvd message out of any provided sets')
        return

    try:
        n_l.remove(c_id)
    except Exception as e:
        logging.error("fatal error")
        logging.error(e)
        return

    await asyncio.sleep(10)
    with open('table.json','r') as fp:
        data = json.load(fp)

    for out in n_l:
        try:
            data[f"{c_id};{message.deleted_id}"]
        except:
            return
        try:
            msg_id = data[f"{c_id};{message.deleted_id}"][out]
        except KeyError:
            msg_id= None
            logging.warning(f"failed to find original message being edited, {c_id};{message.deleted_id}:{out}")
            continue
        await client.delete_messages(int(out),msg_id)


@client.on(events.ChatAction)
async def pin_msg_handler(message):
    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
    else:
        logging.error('rcvd message out of any provided sets')
        return

    await asyncio.sleep(120)

    if message.action_message and message.action_message.reply_to:
        with open('table.json','r') as fp:
            data = json.load(fp)
        n_l.remove(c_id)

        for out in n_l:
            try:
                msg_id = data[f"{c_id};{message.action_message.reply_to.reply_to_msg_id}"][out]
                if not msg_id:
                    logging.error(f"message to be pinned not found, {c_id};{message.action_message.reply_to.reply_to_msg_id};{out}")
                    continue
            except:
                logging.error(f"message to be pinned not found, {c_id};{message.action_message.reply_to.reply_to_msg_id};{out}")
                continue

            await client.pin_message(int(out),msg_id)


@client.on(events.NewMessage(incoming=True))
async def handler(message):

    global message_counter


    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
        langs = sets_config[set_id]['langs']
        flag = sets_config[set_id]['flags'][str(c_id)]
        filters = sets_config[set_id]['filters']
    else:
        logging.error('rcvd message out of any provided sets')
        return
    # Extract the flag emoji from flags[str(c_id)]
    flag_emoji = flag.split(']')[0][1:]

    # Generate the message link
    message_link = generate_message_link(c_id, message.id)

    # Construct the new flag link
    flag_link = f"[{flag_emoji}]({message_link})"

    if message.text:
        text = message.text.lower()
        for command in filters:
            if command in text:
                await message.reply(filters[command],link_preview =False)
                return
        if message.text.startswith('/'):
            return


    try:
        n_l.remove(c_id)
        msg_key,msg_val = f"{c_id};{message.id}",{}
    except Exception as e:
        logging.error("fatal error")
        logging.error(e)
        return

    with open('table.json','r') as fp:
        data = json.load(fp)

    sender = await message.get_sender()
    sender_link = get_sender_link(sender)

    if message.text:
        try:
            message_counter += 1
            with open('btn.json', 'r') as fp:
                btn = json.load(fp)
            button = [Button.url(btn['txt'], btn['url'])]

            for out in n_l:
                if message.reply_to:
                    try:
                        reply_id = data[f"{c_id};{message.reply_to.reply_to_msg_id}"][out]
                    except KeyError:
                        key, obj = find_object_with_key_value(data,c_id,message.reply_to.reply_to_msg_id)
                        if out in key:
                            reply_id = int(key.split(';')[-1])
                        elif 'None' in key:
                            reply_id = None
                        else:
                            try:
                                reply_id = obj[out]
                            except:
                                reply_id= None
                else:
                    reply_id= None

                out_channel= await client.get_input_entity(int(out))
                completion = translate_text(message.text.strip(), langs[out], api_key,langs[str(c_id)])

                if not completion:
                    logging.error(f"Translation failed for following message: {message.text.strip()}\n")
                    return

                try:
                    if message.media:
                        if hasattr(message.media,'webpage'):
                            if message.text[:4].lower() == 'http' and len(message.text.split())==1:
                                r = await client.send_message(out_channel,f"{flag_link} {sender_link}\n{message.text.strip()}",link_preview=False,reply_to =reply_id,buttons=[button])
                                msg_val[out] = r.id
                            else:
                                r = await client.send_message(out_channel,f"{flag_link} {sender_link}\n{completion.strip()}",reply_to =reply_id,buttons=[button])
                                msg_val[out] = r.id
                        else:
                            r = await client.send_file(out_channel,message.media,caption=f"{flag_link} {sender_link}\n{completion.strip()}",reply_to =reply_id,buttons=[button])
                            msg_val[out] = r.id
                    else:
                        r = await client.send_message(out_channel,f"{flag_link} {sender_link}\n{completion.strip()}",link_preview=False,reply_to =reply_id,buttons=[button])
                        msg_val[out] = r.id
                except Exception as e:
                    logging.error(f"out_id:{out}, in_id:{c_id}, Error:{e}")

        except Exception as e:
            logging.error(e)
        else:
            logging.info('A msg forwarded succesfully')
            with open('table.json','r') as fp:
                data = json.load(fp)
            data[msg_key] = msg_val
            with open('table.json','w') as fp:
                json.dump(data,fp,indent=1)
    else:
        try:
            message_counter += 1
            with open('btn.json', 'r') as fp:
                btn = json.load(fp)
            button = [Button.url(btn['txt'], btn['url'])]
            for out in n_l:
                if message.reply_to:
                    try:
                        reply_id = data[f"{c_id};{message.reply_to.reply_to_msg_id}"][out]
                    except KeyError:
                        key, obj = find_object_with_key_value(data,c_id,message.reply_to.reply_to_msg_id)
                        if out in key:
                            reply_id = int(key.split(';')[-1])
                        elif 'None' in key:
                            reply_id = None
                        else:
                            try:
                                reply_id = obj[out]
                            except:
                                reply_id= None
                else:
                    reply_id= None

                out_channel= await client.get_input_entity(int(out))
                r = await client.send_file(out_channel,message.media,caption=f"{flag_link} {sender_link}",buttons=[button])

                msg_val[out] = r.id
        except Exception as e:
            logging.error(e)
        else:
            logging.info('A msg forwarded succesfully')
            with open('table.json','r') as fp:
                data = json.load(fp)
            data[msg_key] = msg_val
            with open('table.json','w') as fp:
                json.dump(data,fp,indent=1)


logging.info(f'\nBot {me.username} is started and will try to forward all rcvd signals from source groups to destination group, please make sure to leave this window open(do not close it)\n')

client.run_until_disconnected()
