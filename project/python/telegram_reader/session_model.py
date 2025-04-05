from sqlalchemy import Column, String, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SessionModel(Base):
    __tablename__ = 'telethon_sessions'
    name = Column(String, primary_key=True)
    data = Column(LargeBinary)  # 存放序列化後的 session 資料


import pickle
from telethon.sessions import MemorySession
from telethon.sessions.abstract import Session

class PostgresSession(Session):
    def __init__(self, db_url: str, session_name: str = "default"):
        super().__init__()
        self.db_url = db_url
        self.session_name = session_name
        self._engine = create_engine(db_url)
        self._Session = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

        self._mem_session = MemorySession()

        self._load()

    def _load(self):
        db = self._Session()
        row = db.query(SessionModel).filter_by(name=self.session_name).first()
        if row:
            mem_session = pickle.loads(row.data)
            self._mem_session = mem_session
        db.close()

    def save(self):
        db = self._Session()
        binary = pickle.dumps(self._mem_session)
        obj = db.query(SessionModel).filter_by(name=self.session_name).first()
        if obj:
            obj.data = binary
        else:
            obj = SessionModel(name=self.session_name, data=binary)
            db.add(obj)
        db.commit()
        db.close()

    # Proxy methods
    def clone(self, to_instance=None):
        """
        Creates a clone of this session file.
        """
        return to_instance or self.__class__(self.db_url, self.session_name)

    def set_dc(self, dc_id, server_address, port):
        """
        Sets the information of the data center address and port that
        the library should connect to, as well as the data center ID,
        which is currently unused.
        """
        return self._mem_session.set_dc(dc_id, server_address, port)

    @property
    def dc_id(self):
        """
        Returns the currently-used data center ID.
        """
        return self._mem_session.dc_id

    @property
    def server_address(self):
        """
        Returns the server address where the library should connect to.
        """
        return self._mem_session.server_address

    @property
    def port(self):
        """
        Returns the port to which the library should connect to.
        """
        return self._mem_session.port

    @property
    def auth_key(self):
        """
        Returns an ``AuthKey`` instance associated with the saved
        data center, or `None` if a new one should be generated.
        """
        return self._mem_session.auth_key

    @auth_key.setter
    def auth_key(self, value):
        """
        Sets the ``AuthKey`` to be used for the saved data center.
        """
        self._mem_session.auth_key = value

    @property
    def takeout_id(self):
        """
        Returns an ID of the takeout process initialized for this session,
        or `None` if there's no were any unfinished takeout requests.
        """
        return self._mem_session.takeout_id

    @takeout_id.setter
    def takeout_id(self, value):
        """
        Sets the ID of the unfinished takeout process for this session.
        """
        self._mem_session.takeout_id = value


    def get_update_state(self, entity_id):
        """
        Returns the ``UpdateState`` associated with the given `entity_id`.
        If the `entity_id` is 0, it should return the ``UpdateState`` for
        no specific channel (the "general" state). If no state is known
        it should ``return None``.
        """
        return self._mem_session.get_update_state(entity_id)

    
    def set_update_state(self, entity_id, state):
        """
        Sets the given ``UpdateState`` for the specified `entity_id`, which
        should be 0 if the ``UpdateState`` is the "general" state (and not
        for any specific channel).
        """
        return self._mem_session.set_update_state(entity_id, state)

    
    def get_update_states(self):
        """
        Returns an iterable over all known pairs of ``(entity ID, update state)``.
        """
        return self._mem_session.get_update_states()

    def close(self):
        """
        Called on client disconnection. Should be used to
        free any used resources. Can be left empty if none.
        """
        self.save()

    
    def delete(self):
        """
        Called upon client.log_out(). Should delete the stored
        information from disk since it's not valid anymore.
        """
        raise NotImplementedError


    def list_sessions(cls):
        """
        Lists available sessions. Not used by the library itself.
        """
        return cls._Session().query(SessionModel).all()

    
    def process_entities(self, tlo):
        """
        Processes the input ``TLObject`` or ``list`` and saves
        whatever information is relevant (e.g., ID or access hash).
        """
        return self._mem_session.process_entities(tlo)

    
    def get_input_entity(self, key):
        """
        Turns the given key into an ``InputPeer`` (e.g. ``InputPeerUser``).
        The library uses this method whenever an ``InputPeer`` is needed
        to suit several purposes (e.g. user only provided its ID or wishes
        to use a cached username to avoid extra RPC).
        """
        return self._mem_session.get_input_entity(key)

    
    def cache_file(self, md5_digest, file_size, instance):
        """
        Caches the given file information persistently, so that it
        doesn't need to be re-uploaded in case the file is used again.

        The ``instance`` will be either an ``InputPhoto`` or ``InputDocument``,
        both with an ``.id`` and ``.access_hash`` attributes.
        """
        return self._mem_session.cache_file(md5_digest, file_size, instance)

    
    def get_file(self, md5_digest, file_size, cls):
        """
        Returns an instance of ``cls`` if the ``md5_digest`` and ``file_size``
        match an existing saved record. The class will either be an
        ``InputPhoto`` or ``InputDocument``, both with two parameters
        ``id`` and ``access_hash`` in that order.
        """
        return self._mem_session.get_file(md5_digest, file_size, cls)