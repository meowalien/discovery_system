from kafka import KafkaProducer
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaContact, MessageMediaWebPage,
    MessageMediaGame, MessageMediaInvoice, MessageMediaPoll,
    MessageMediaDice, MessageMediaGeoLive, MessageService,
    PeerUser, PeerChat, PeerChannel
)


class MessageConsumer:
    def __init__(self, kafka_producer: KafkaProducer):
        self._kafka_producer = kafka_producer

    def get_source_type(self, message: Message) -> str:
        """
        判斷消息來源類型
        """
        source_type = "unknown"
        if message.chat:
            chat_class = message.chat.__class__.__name__
            if chat_class == "User":
                source_type = "private"
            elif chat_class == "Chat":
                source_type = "group"
            elif chat_class == "Channel":
                source_type = "supergroup" if getattr(message.chat, 'megagroup', False) else "channel"
        else:
            if message.peer_id:
                peer_class = message.peer_id.__class__.__name__
                if peer_class == "PeerUser":
                    source_type = "private"
                elif peer_class == "PeerChat":
                    source_type = "group"
                elif peer_class == "PeerChannel":
                    source_type = "channel"
        return source_type

    async def on_new_event(self, event: NewMessage.Event) -> None:
        message: Message = event.message

        # 唯一識別碼：chat.id 或 sender_id
        unique_id = message.chat.id if message.chat else message.sender_id

        # 來源類型
        source_type = self.get_source_type(message)

        # 討論串 id（如果有）
        if hasattr(message, 'forum_topic_id') and message.forum_topic_id is not None:
            discussion_thread_id = message.forum_topic_id
            unique_discussion_id = f"{message.chat.id}_{message.forum_topic_id}"
        else:
            discussion_thread_id = None
            unique_discussion_id = None

        # 回覆相關
        reply_to_msg_id = message.reply_to_msg_id or None
        reply_to_msg_text = None
        if reply_to_msg_id:
            try:
                reply = await event.get_reply_message()
                reply_to_msg_text = reply.message if reply else None
            except Exception as e:
                print(f"Error fetching reply message: {e}")

        # 渠道/群組名稱與 ID
        chat = message.chat
        if chat and chat.__class__.__name__ in ("Chat", "Channel"):
            channel_id = chat.id
            channel_name = getattr(chat, "title", None)
        else:
            channel_id = None
            channel_name = None

        # 發送者名稱
        try:
            sender = await event.get_sender()
            first = getattr(sender, "first_name", "") or ""
            last = getattr(sender, "last_name", "") or ""
            sender_name = f"{first} {last}".strip()
            if not sender_name:
                sender_name = getattr(sender, "title", None) or str(getattr(sender, "id", ""))
        except:
            sender_name = None

        # 組訊息
        msg_dict = {
            "message_id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "sender_id": message.sender_id,
            "sender_name": sender_name,
            "peer_id": str(message.peer_id) if message.peer_id else None,
            "text": message.message,
            "media": str(message.media) if message.media else None,
            "source_type": source_type,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "reply_to_msg_id": reply_to_msg_id,
            "reply_to_msg_text": reply_to_msg_text,
            "discussion_thread_id": discussion_thread_id,
            "unique_discussion_id": unique_discussion_id,
        }

        # 發送到 Kafka
        self._kafka_producer.send(
            'telegram_topic',
            key=str(unique_id).encode('utf-8'),
            value=msg_dict
        )
        self._kafka_producer.flush()
        print("Message: ", msg_dict)