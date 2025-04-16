import asyncio
from asyncio import CancelledError


from core.telegram_client_manager import TelegramClientManager

# 你需要填入自己的 API 資訊
API_ID = 24529225        # 替換成你的 api_id
API_HASH = '0abc06cc13bab8c228b59bcca4284800'
SESSION_ID = "63f99658-6f35-4eac-b076-8ee2575a2133"
phone = '+886968893589'
password = 'kingkingjin'

manager = TelegramClientManager()

from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaContact, MessageMediaWebPage,
    MessageMediaGame, MessageMediaInvoice, MessageMediaPoll,
    MessageMediaDice, MessageMediaGeoLive, MessageService
)

async def message_callback(event: NewMessage.Event):
    message: Message = event.message

    # 檢查是否是服務消息（系統通知、群組事件等）
    # 一般來說，服務消息會有 action 屬性或已被 Telethon 包裝成 MessageService
    if getattr(message, 'service', None) or isinstance(message, MessageService):
        print("Service Message")
        return

    # 接下來針對非服務消息使用 match-case 判斷內容
    match message.media:
        # 無媒體：純文字或者空消息
        case None:
            if message.text:
                print("Text Message")
            else:
                print("Empty Message")
        # 有媒體
        case media:
            # 使用嵌套 match-case 對媒體進行進一步判斷
            match media:
                case MessageMediaPhoto():
                    print("Photo Message")
                case MessageMediaDocument(document=document):
                    # 根據 document 的 mime_type 區分不同文件類型
                    if document.mime_type == "application/x-tgsticker":
                        print("Sticker Message")
                    elif document.mime_type.startswith("video/"):
                        print("Video Message")
                    elif document.mime_type.startswith("audio/"):
                        print("Audio Message")
                    else:
                        print("Document Message")
                case MessageMediaGeo():
                    print("Geo Location Message")
                case MessageMediaVenue():
                    print("Venue Message")
                case MessageMediaContact():
                    print("Contact Message")
                case MessageMediaWebPage():
                    print("Web Page Preview Message")
                case MessageMediaGame():
                    print("Game Message")
                case MessageMediaInvoice():
                    print("Invoice Message")
                case MessageMediaPoll():
                    print("Poll Message")
                case MessageMediaDice():
                    print("Dice Message")
                case MessageMediaGeoLive():
                    print("Geo Live Message")
                case _:
                    print("Other Media Message")


async def main():
    # Step 1: 創建 TelegramClient
    await manager.load_client(SESSION_ID)

    phone_code_hash = await manager.sign_in(SESSION_ID, phone)
    if phone_code_hash:
        code = input(f"請輸入從 Telegram 收到的驗證碼: ")
        await manager.complete_sign_in(SESSION_ID, phone, code,phone_code_hash, password=password)

    # Step 2: 取得所有 dialogs
    dialogs = await manager.get_dialogs(SESSION_ID)
    if not dialogs:
        print("❗ 無可用的對話")
        return

    print(f"✅ Found {len(dialogs)} dialogs.")
    # print all dialog name
    for dialog in dialogs:
        entity = dialog.entity
        print(f"Dialog: {getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))}, id: {entity.id}, access_hash: {getattr(entity,'access_hash', 'Unknown')}")

    # filter the first entity where id is 334253352
    dialog = next((dialog for dialog in dialogs if dialog.entity.id == 1301096229), None)
    entity = dialog.entity
    print("entity: ",getattr(entity, 'title', getattr(entity, 'username', 'Unknown')))


    print(f"👀 Listening to: {getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))}")

    # 只處理頻道或群組的情況
    if hasattr(entity, "id"):
        await manager.register_channel_callback(
            session_id=SESSION_ID,
            callback=message_callback
        )
    else:
        print("⚠️ 第一個對話沒有 id 和 access_hash，無法註冊監聽器")
        return

    try:
        await asyncio.Event().wait()
    except CancelledError:
        print("❌ 停止監聽")

if __name__ == "__main__":
    asyncio.run(main())