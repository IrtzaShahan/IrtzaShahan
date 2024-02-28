client = TelegramClient('bot', api_id, api_hash)

client.start(bot_token="6633748725:AAGIhDfz-dQ3UDSgM3u_qJ2Q_kiYScspHCE")
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

def translate_text(text, target_language, api_key,source_language):
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "a_Srrj954JR2Kp5RYULdKL3tCNy1sd5UoG6SDFlPRuAmeos7BJePiTJ5ESjSVQfEMWoo1ZPrnZdr5JlaIz"
    }

    data =  {
        "platform": "api",
        "from": source_language,
        "to": target_language,
        "data": text
    }

    response = requests.post(url, headers=headers, json=data)

    if 'result' in response.json():
        translated_text = response.json()['result']
        return translated_text
    else:
        logging.info(response.json())
        return False

def update_sets(sets_config):
    with open('sets_configs.json','w') as fp:
        json.dump(sets_config,fp,indent=1)


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
    return None

def get_entities(config):
    all_entities = []
    for set_name, set_details in config.items():
        entity_list = []
        channels_list = set_details["channels_list"]
        for channel in channels_list:
            try:
                input_par = int(channel)
            except ValueError:
                input_par = channel
            entity = client.get_input_entity(input_par)
            entity_list.append(entity)
        all_entities.extend(entity_list)
    return all_entities


entities = get_entities(sets_config)

@client.on(events.NewMessage(pattern='/filter'))
async def add_filter(event):
    c_id =f"{event.chat_id}"
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
    await event.respond(f"filter for '{command}' added successfully.")

@client.on(events.NewMessage(pattern='/stop '))
async def remove_filter(event):
    c_id =f"{event.chat_id}"
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    command = event.message.text.split(maxsplit=1)[1]
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]  # Remove quotes for phrases

    if command.lower() in filters:
        del sets_config[set_id]['filters'][command.lower()]
        update_sets(sets_config)
        await event.respond(f"filter for '{command}' removed.")
    else:
        await event.respond("filter not found.")

@client.on(events.NewMessage(pattern='/stopall'))
async def remove_all_filters(event):
    c_id =f"{event.chat_id}"
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    sets_config[set_id]['filters'].clear()
    update_sets(sets_config)
    await event.respond("All filters removed.")

@client.on(events.NewMessage(pattern='/filters'))
async def list_filters(event):
    c_id =f"{event.chat_id}"
    set_id = find_set_id_for_group(c_id)
    if not set_id:
        logging.error('rcvd message out of any provided sets')
        return

    if sets_config[set_id]['filters']:
        commands_list = "\n".join([f"{cmd}: {reply}" for cmd, reply in sets_config[set_id]['filters'].items()])
        await event.respond(f"filters:\n{commands_list}")
    else:
        await event.respond("No filters set.")

@client.on(events.NewMessage(pattern='/id'))
async def handler(event):
    await event.reply(f"this channel/group id is: {event.chat_id}")

@client.on(events.ChatAction(entities))
async def pin_msg_handler(message):
    if message.action_message and message.action_message.reply_to:
        with open('table.json','r') as fp:
            data = json.load(fp)
        n_l = channels_list[:]
        n_l.remove(f"-100{message.action_message.peer_id.channel_id}")
        for out in n_l:
            out_channel= await client.get_input_entity(int(out))
            await client.pin_message(out_channel,data[f"-100{message.action_message.peer_id.channel_id};{message.action_message.reply_to.reply_to_msg_id}"][out])


@client.on(events.NewMessage(entities,incoming=True))
async def handler(message):
    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
        langs = sets_config[set_id]['langs']
        flags = sets_config[set_id]['flags']
        filters = sets_config[set_id]['filters']
    else:
        logging.error('rcvd message out of any provided sets')
        return

    if message.text:
        text = message.text.lower()
        for command in filters:
            if command in text:
                await message.respond(filters[command])
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

    if message.text:
        try:
            for out in n_l:
##                logging.warning(f'{out},{cid}')
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

                if message.media:
                    if hasattr(message.media,'webpage'):
                        if message.text[:4].lower() == 'http' and len(message.text.split())==1:
                            r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{message.text.strip()}",link_preview=False,reply_to =reply_id)
                            msg_val[out] = r.id
                        else:
                            r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                            msg_val[out] = r.id
                    else:
                        r = await client.send_file(out_channel,message.media,caption=f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                        msg_val[out] = r.id
                else:
                    r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",link_preview=False,reply_to =reply_id)
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
    else:
        try:
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
                r = await client.send_file(out_channel,message.media,caption=f"{flags[str(c_id)]} {sender_link}")
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
