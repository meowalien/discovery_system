import uuid
from typing import TypeVar, Generic, Type, Optional
import json
from redis_client import redis_client, new_redis_key, RedisKey

T = TypeVar("T")



class Session(Generic[T]):
    """
    A generic session class that stores an object of type T in Redis.

    When instantiating this class, you must supply the data class type via `data_cls`
    so that the stored JSON string can be deserialized into an instance of T.
    """

    def __init__(self, session_id: str, data_cls: Type[T]):
        self.session_id = session_id
        self.data_cls = data_cls

    async def get_data(self) -> Optional[T]:
        """
        Reads the session data from Redis, deserializes it from JSON, and returns an
        object of type T. Returns None if no data is found.
        """
        redis_key = new_redis_key(RedisKey.SESSION, self.session_id)
        data_str = await redis_client.get(redis_key)
        if data_str is None:
            return None
        data_dict = json.loads(data_str)
        # Instantiate an object of type T using keyword arguments.
        return self.data_cls(**data_dict)

    async def set_data(self, value: T) -> None:
        """
        Serializes the provided object of type T into JSON and stores it in Redis.
        """
        redis_key = new_redis_key(RedisKey.SESSION, self.session_id)
        # Assumes that `value` has a __dict__ attribute (or you can customize serialization).
        data_str = json.dumps(value.__dict__)
        await redis_client.set(redis_key, data_str)


def new_session(data_cls: Type[T]) -> Session[T]:
    """
    Creates a new Session instance with a generated session_id.

    :param data_cls: The data class type for deserialization.
    :return: A new Session instance.
    """
    session_id = str(uuid.uuid4())
    return Session(session_id, data_cls)