def translate_text(text, target_language, api_key,source_language):
    base_url = 'https://libretranslate.com/translate'
    
    params = {
        'api_key': api_key,
        'q': text,
        'target': target_language,
        'format': 'text',
        'source': source_language,
    }

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    response = requests.post(base_url, headers=headers, data=params)

    if response.status_code == 200:
        if 'translatedText' in response.json():
            return response.json()['translatedText']
        else:
            print(response.json())
            return response.text
    else:
        print(f"Error: {response.status_code}, {response.text}")


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
    n_l = channels_list[:]
    n_l.remove(f"-100{message.peer_id.channel_id}")
    msg_key,msg_val = f"-100{message.peer_id.channel_id};{message.id}",{}
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
            if message.media:
                if hasattr(message.media,'webpage'):
                    if message.text[:4].lower() == 'http' and len(message.text.split())==1:
                        for out in n_l:
                            if message.reply_to:
                                try:
                                    reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                                except KeyError:
                                    reply_id = None
                            else:
                                reply_id= None

                            out_channel= await client.get_input_entity(int(out))
                            r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{message.text.strip()}",link_preview=False,reply_to =reply_id)
                            msg_val[out] = r.id

                    else:
                        for out in n_l:
                            if message.reply_to:
                                try:
                                    reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                                except KeyError:
                                    reply_id = None
                            else:
                                reply_id= None
                            
                            completion = translate_text(message.text.strip(), langs[out[4:]], api_key,langs[str(message.peer_id.channel_id)])
                            out_channel= await client.get_input_entity(int(out))
                            r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                            msg_val[out] = r.id
                    
                else:
                    for out in n_l:
                        if message.reply_to:
                            try:
                                reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                            except KeyError:
                                reply_id = None
                        else:
                            reply_id= None

                        completion = translate_text(message.text.strip(), langs[out[4:]], api_key,langs[str(message.peer_id.channel_id)])
                        out_channel= await client.get_input_entity(int(out))
                        r = await client.send_file(out_channel,message.media,caption=f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                        msg_val[out] = r.id
            else:
                for out in n_l:
                    if message.reply_to:
                        try:
                            reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                        except KeyError:
                            reply_id = None
                    else:
                        reply_id= None

                    completion = translate_text(message.text.strip(), langs[out[4:]], api_key,langs[str(message.peer_id.channel_id)])
                    out_channel= await client.get_input_entity(int(out))
                    r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",link_preview=False,reply_to =reply_id)
                    msg_val[out] = r.id

        except Exception as e:
            print(e)
            print(type(e).__name__)
        else:
            print('A msg forwarded succesfully')
            with open('table.json','r') as fp:
                data = json.load(fp)
            data[msg_key] = msg_val
            with open('table.json','w') as fp:
                json.dump(data,fp,indent=1)
            
    else:
        try:
            for out in n_l:
                out_channel= await client.get_input_entity(int(out))
                await client.send_file(out_channel,message.media,caption=f"{flags[str(message.peer_id.channel_id)]} {sender_link}")
        except Exception as e:
            print(e)
            print(type(e).__name__)


print(f'\nBot {me.username} is started and will try to forward all rcvd signals from source groups to destination group, please make sure to leave this window open(do not close it)\n')

client.run_until_disconnected()
