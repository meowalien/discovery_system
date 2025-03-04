from telethon import TelegramClient, events, utils

# Remember to use your own values from my.telegram.org!
api_id = 24529225
api_hash = '0abc06cc13bab8c228b59bcca4284800'
client = TelegramClient('anon', api_id, api_hash)

async def main():
    # Getting information about yourself
    # me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    # print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    # username = me.username
    # print(username)
    # print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # You can send messages to yourself...
    # await client.send_message('me', 'Hello, myself!')
    # ...to some chat ID
    # await client.send_message(-100123456, 'Hello, group!')
    # # ...to your contacts
    # await client.send_message('+34600123123', 'Hello, friend!')
    # # ...or even to any username
    # await client.send_message('username', 'Testing Telethon!')

    # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # Or send files, songs, documents, albums...
    # await client.send_file('me', '/home/me/Pictures/holidays.jpg')

    # filter messages from group 1001301096229
    @client.on(events.NewMessage(chats=-1001140512009))
    async def handler(event: events.NewMessage.Event):
        sender = await event.get_sender()

        first_name = sender.first_name if sender.first_name is not None else ''
        last_name = sender.last_name if sender.last_name is not None else ''
        fill_name = first_name + last_name

        date = event.date
        print("date: ",date)
        print("source_name: ",sender)
        print("event: ", event)
        print(f"股癌美股夜貓仔 {fill_name}: {event.raw_text}")



    # filter messages from group 1001301096229
    @client.on(events.NewMessage(chats=-1001301096229))
    async def handler(event):
        sender = await event.get_sender()
        first_name = sender.first_name if sender.first_name is not None else ''
        last_name = sender.last_name if sender.last_name is not None else ''
        fill_name = first_name + last_name
        date = event.date
        print("date: ", date)
        print("source_name: ",sender)
        print("event: ",event)
        print(f"股癌台股世界大哥 -> {fill_name}: {event.raw_text}")

    await client.start()
    print("Telegram 客戶端已啟動，正在監聽消息...")


    await client.run_until_disconnected()


    # You can print the message history of any chat:
    # async for message in client.iter_messages(1001301096229):
    #     print(message.id, message.text)

        # You can download media from messages, too!
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media()
        #     print('File saved to', path)  # printed after download is done

with client:
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting...")