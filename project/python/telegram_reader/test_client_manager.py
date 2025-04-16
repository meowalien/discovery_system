import asyncio

from telethon.events import NewMessage

from core.telegram_client_manager import TelegramClientManager

# 你需要填入自己的 API 資訊
API_ID = 24529225        # 替換成你的 api_id
API_HASH = '0abc06cc13bab8c228b59bcca4284800'
SESSION_ID = '886968893589'
phone = '+886968893589'
password = 'kingkingjin'

manager = TelegramClientManager()

async def message_callback(event:NewMessage.Event):
#     encode event object as json string
    json_str = str(event).encode('utf-8')
    print("json_str: ", json_str)

async def main():
    # Step 1: 創建 TelegramClient
    await manager._load_or_create_client(SESSION_ID, API_ID, API_HASH)

    phone_code_hash = await manager.sign_in(SESSION_ID, phone, password=password)
    if phone_code_hash:
        code = input(f"請輸入從 Telegram 收到的驗證碼: ")
        await manager.complete_sign_in(SESSION_ID, phone, code,phone_code_hash, password=password)

    # Step 2: 取得所有 dialogs
    dialogs = await manager.get_user_dialogs(SESSION_ID)
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

    # first_dialog = dialogs[0]
    # entity = first_dialog.entity

    # Step 3: 顯示第一個對話的資訊
    print(f"👀 Listening to: {getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))}")

    # 只處理頻道或群組的情況
    if hasattr(entity, "id") and hasattr(entity, "access_hash"):
        await manager.register_channel_callback(
            session_id=SESSION_ID,
            channel_id=entity.id,
            access_hash=entity.access_hash,
            callback=message_callback
        )
    else:
        print("⚠️ 第一個對話沒有 id 和 access_hash，無法註冊監聽器")
        return

    # Step 4: 保持執行以等待事件發生
    print("🚀 Ready and listening for messages...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())