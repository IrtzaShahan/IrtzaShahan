from telethon.sync import TelegramClient,events
from datetime import datetime, timedelta
from time import time
import os, requests,json
import openai

api_id = 27626586
api_hash = '90c8ff00f20929899e1cc2f16d63ffe1'
api_key = '9d693983-8741-6861-6eb9-5b6911c4d4de'
api_key ="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"

english = "2077495168"
pidgin = "2003391866"

langs = {f'{english}':'en_US',f'{pidgin}':'el_GR'}
flags = {f'{english}':'🇺🇸',f'{pidgin}':'🇬🇷'}

channels_list = [f"-100{english}",f"-100{pidgin}"]

client = TelegramClient('bot', api_id, api_hash)

client.start(bot_token="6633748725:AAGIhDfz-dQ3UDSgM3u_qJ2Q_kiYScspHCE")


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
    with open('table.json','r') as fp:
        data = json.load(fp)
    n_l = channels_list[:]
    n_l.remove(f"-100{message.action_message.peer_id.channel_id}")
    for out in n_l:
        out_channel= await client.get_input_entity(int(out))
        await client.pin_message(out_channel,data[f"-100{message.action_message.peer_id.channel_id};{message.action_message.reply_to.reply_to_msg_id}"][out])
        print(out,data[f"-100{message.action_message.peer_id.channel_id};{message.action_message.reply_to.reply_to_msg_id}"][out])



def find_object_with_key_value(data, key, value):
    for parent_key, parent_value in data.items():
        if key in parent_value and parent_value[key] == value:
            return parent_key, parent_value
    return None

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
            for out in n_l:
                if message.reply_to:
                    try:
                        reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                    except KeyError:
                        key, obj = find_object_with_key_value(data,f"-100{message.peer_id.channel_id}",message.reply_to.reply_to_msg_id)
                        if out in key:
                            reply_id = int(key.split(';')[-1])
                        else:
                            try:
                                reply_id = obj[out]
                            except:
                                reply_id= None
                else:
                    reply_id= None
    
                out_channel= await client.get_input_entity(int(out))
                completion = translate_text(message.text.strip(), langs[out[4:]], api_key,langs[str(message.peer_id.channel_id)])
            
                if message.media:
                    if hasattr(message.media,'webpage'):
                        if message.text[:4].lower() == 'http' and len(message.text.split())==1:
                            r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{message.text.strip()}",link_preview=False,reply_to =reply_id)
                            msg_val[out] = r.id
                        else:                           
                            r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                            msg_val[out] = r.id

                    else:
                        r = await client.send_file(out_channel,message.media,caption=f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",reply_to =reply_id)
                        msg_val[out] = r.id
                else:
                    r = await client.send_message(out_channel,f"{flags[str(message.peer_id.channel_id)]} {sender_link}\n{completion.strip()}",link_preview=False,reply_to =reply_id)
                    msg_val[out] = r.id

        except Exception as e:
            print(e)
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
                if message.reply_to:
                    try:
                        reply_id = data[f"-100{message.peer_id.channel_id};{message.reply_to.reply_to_msg_id}"][out]
                    except KeyError:
                        key, obj = find_object_with_key_value(data,f"-100{message.peer_id.channel_id}",message.reply_to.reply_to_msg_id)
                        if out in key:
                            reply_id = int(key.split(';')[-1])
                        else:
                            try:
                                reply_id = obj[out]
                            except:
                                reply_id= None
                else:
                    reply_id= None

                out_channel= await client.get_input_entity(int(out))
                r = await client.send_file(out_channel,message.media,caption=f"{flags[str(message.peer_id.channel_id)]} {sender_link}")
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


print('\nBot is started and will try to forward all rcvd signals from source groups to destination group, please make sure to leave this window open(do not close it)\n')

client.run_until_disconnected()
