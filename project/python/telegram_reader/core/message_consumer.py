from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaContact, MessageMediaWebPage,
    MessageMediaGame, MessageMediaInvoice, MessageMediaPoll,
    MessageMediaDice, MessageMediaGeoLive, MessageService
)

class MessageConsumer:
    def __init__(self):
        pass

    async def on_new_event(self, event: NewMessage.Event) -> None:
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
                    print(f"Text Message: {message.text}")
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