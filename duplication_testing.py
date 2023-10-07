async def get_clients_groups_dict():
    try:
        clients_groups_dict = {}
        for i,phone_number in enumerate(phone_number_list):
            print(f"{phone_number} logging in and getting groups")
            client = TelegramClient(phone_number, int(api_id), api_hash)
            await client.start(phone_number)
            groups = await client.get_dialogs()
            groups = [g for g in groups if ((g.is_group) or (g.is_channel))]
            clients_groups_dict[client] = [groups,list_of_messages[i],f'b2({i+1}):{phone_number}',list_of_images[i]]
            print(f" Successfully Logged in and Got list of groups for account {phone_number}")
            await client.disconnect()
        return clients_groups_dict
    except Exception as e:
        print(f"Error occurred: {e}")


async def send_messages(client,groups_messages):
    await client.connect()
    for g in groups_messages[0]:
        try:
            message = groups_messages[1]
            image = groups_messages[3]
            await client.send_file(g,image, caption=message)
        except Exception as e:
            print(f"error for group:{g.id}, {groups_messages[2]}:{e}")
        else:
            print(f"success:{groups_messages[2]}")
        sleep(interval_between_messages)
    await client.disconnect()


async def main():
    clients_groups_dict = await get_clients_groups_dict()
    while True:
        try:
            for client,groups_messages in clients_groups_dict.items():
                await send_messages(client,groups_messages)
                sleep(interval_between_accounts)
        except Exception as e:
            print(f"main error: {e}")
        sleep(interval_between_cycles_in_minutes*60)


asyncio.run(main())
