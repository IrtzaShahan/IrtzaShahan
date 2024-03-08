@client.on(events.MessageEdited(entities))
async def edit_handler(message):
    if message.text and message.text.startswith('/') or message.out:
        return

    c_id =f"{message.chat_id}"
    set_id = find_set_id_for_group(c_id)

    if set_id:
        n_l = sets_config[set_id]['channels_list'][:]
        langs = sets_config[set_id]['langs']
        flags = sets_config[set_id]['flags']
    else:
        logging.error('rcvd message out of any provided sets')
        return

    try:
        n_l.remove(c_id)
    except Exception as e:
        logging.error("fatal error")
        logging.error(e)
        return
    await asyncio.sleep(60)
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
                        original_text_line1 = f"{flags[str(c_id)]} {sender_link}\n"
                except:
                    sender = await message.get_sender()
                    sender_link = get_sender_link(sender)
                    original_text_line1 = f"{flags[str(c_id)]} {sender_link}\n"


                await client.edit_message(int(out), msg_id, f"{original_text_line1}\n{completion.strip()}",link_preview=False)
        except rpcerrorlist.MessageNotModifiedError:
            logging.info("edited message is same as original")
            return
        except Exception as e:
            logging.error(e)
        else:
            logging.info('A msg edited succesfully')


@client.on(events.ChatAction(entities))
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
