client = TelegramClient('bot', api_id, api_hash)
client.start(bot_token=bot_token_hash)
me = client.get_me()


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

    headers = {"accept": "application/json", "content-type": "application/json", "Authorization": api_key}

    if source_language == "zh-Hant_TW":
        data = {"platform": "api", "to": target_language, "data": text}
    else:
        data = {"platform": "api", "from": source_language, "to": target_language, "data": text}

    response = requests.post(url, headers=headers, json=data)

    if 'result' in response.json():
        translated_text = response.json()['result']
        return translated_text
    else:
        logging.warning(response.text)
        return False


def find_object_with_key_value(data, key, value):
    for parent_key, parent_value in data.items():
        if key in parent_value and parent_value[key] == value:
            return parent_key, parent_value
    logging.warning(f"key,val '{key},{value}' not found")
    return 'None','None;None'


def get_entities():
    entity_list= []
    for channel in channels_list:
        try:
            input_par = int(channel)
        except:
            input_par = channel
        entity=client.get_input_entity(input_par)
        entity_list.append(entity)
    return entity_list


entities = get_entities()

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
    c_id = f"{message.chat_id}"
    n_l = channels_list[:]
    
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
        if message.text.startswith('/'):
            return
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
                completion = translate_text(message.text.strip(), langs[out], api_key,langs[str(c_id)])

                if not completion:
                    return

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
