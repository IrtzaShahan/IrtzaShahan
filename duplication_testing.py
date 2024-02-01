def translate_text(text, target_language, api_key,source_language):
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "a_Srrj954JR2Kp5RYULdKL3tCNy1sd5UoG6SDFlPRuAmeos7BJePiTJ5ESjSVQfEMWoo1ZPrnZdr5JlaIz"
    }

    data =  {
        "platform": "api",
        "to": target_language,
        "data": text
    }

    response = requests.post(url, headers=headers, json=data)
    
    if 'result' in response.json():
        translated_text = response.json()['result']
        return translated_text
    else:
        print(response.json())
        return False


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
    try:
        n_l.remove(f"-100{message.peer_id.channel_id}")
        msg_key,msg_val = f"-100{message.peer_id.channel_id};{message.id}",{}
        c_id = f"-100{message.peer_id.channel_id}"
    except:
        n_l.remove(f"-{message.peer_id.chat_id}")
        msg_key,msg_val = f"-{message.peer_id.chat_id};{message.id}",{}
        c_id = f"-{message.peer_id.chat_id}"

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
                                    reply_id = data[f"{c_id};{message.reply_to.reply_to_msg_id}"][out]
                                except KeyError:
                                    reply_id = None
                            else:
                                reply_id= None

                            out_channel= await client.get_input_entity(int(out))
                            r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{message.text.strip()}",link_preview=False,reply_to =reply_id)
                            msg_val[out] = r.id

                    else:
                        for out in n_l:
                            if message.reply_to:
                                try:
                                    reply_id = data[f"{c_id};{message.reply_to.reply_to_msg_id}"][out]
                                except KeyError:
                                    reply_id = None
                            else:
                                reply_id= None
                            
                            completion = translate_text(message.text.strip(), langs[out], api_key,langs[str(c_id)])
                            out_channel= await client.get_input_entity(int(out))
                            r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
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

                        completion = translate_text(message.text.strip(), langs[out], api_key,langs[str(c_id)])
                        out_channel= await client.get_input_entity(int(out))
                        r = await client.send_file(out_channel,message.media,caption=f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                        msg_val[out] = r.id
            else:
                for out in n_l:
                    if message.reply_to:
                        try:
                            reply_id = data[f"`{c_id};{message.reply_to.reply_to_msg_id}"][out]
                        except KeyError:
                            reply_id = None
                    else:
                        reply_id= None

                    completion = translate_text(message.text.strip(), langs[out], api_key,langs[str(c_id)])
                    out_channel= await client.get_input_entity(int(out))
                    r = await client.send_message(out_channel,f"{flags[str(c_id)]} {sender_link}\n{completion.strip()}",link_preview=False,reply_to =reply_id)
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
                await client.send_file(out_channel,message.media,caption=f"{flags[str(c_id)]} {sender_link}")
        except Exception as e:
            print(e)
            print(type(e).__name__)


print(f'\nBot {me.username} is started and will try to forward all rcvd signals from source groups to destination group, please make sure to leave this window open(do not close it)\n')

client.run_until_disconnected()
