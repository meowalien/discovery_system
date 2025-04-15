-- create table if not exists telegram_reader.version
-- (
--     version serial
--         primary key
-- );
--
-- alter table telegram_reader.version
--     owner to postgres;

create table if not exists telegram_reader.sessions
(
    session_id     text not null
        primary key,
    dc_id          integer,
    server_address text,
    port           integer,
    auth_key       bytea,
    takeout_id     integer
);

alter table telegram_reader.sessions
    owner to postgres;

create table if not exists telegram_reader.entities
(
    id       bigint
        primary key,
    hash     bigint not null,
    username text,
    phone    bigint,
    name     text,
    date     integer
);

alter table telegram_reader.entities
    owner to postgres;

create table if not exists telegram_reader.sent_files
(
    md5_digest bytea   not null,
    file_size  integer not null,
    type       integer not null,
    id         integer,
    hash       integer,
    primary key (md5_digest, file_size, type)
);

alter table telegram_reader.sent_files
    owner to postgres;

create table if not exists telegram_reader.update_state
(
    id   bigint
        primary key,
    pts  integer,
    qts  integer,
    date integer,
    seq  integer
);

alter table telegram_reader.update_state
    owner to postgres;

