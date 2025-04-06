create table if not exists public.sessions
(
    session_id     text not null
        primary key,
    dc_id          integer,
    server_address text,
    port           integer,
    auth_key       bytea,
    takeout_id     integer
);

alter table public.sessions
    owner to postgres;

create table if not exists public.entities
(
    id       serial
        primary key,
    hash     bigint not null,
    username text,
    phone    bigint,
    name     text,
    date     integer
);

alter table public.entities
    owner to postgres;

create table if not exists public.sent_files
(
    md5_digest bytea   not null,
    file_size  integer not null,
    type       integer not null,
    id         integer,
    hash       integer,
    primary key (md5_digest, file_size, type)
);

alter table public.sent_files
    owner to postgres;

create table if not exists public.update_state
(
    id   serial
        primary key,
    pts  integer,
    qts  integer,
    date integer,
    seq  integer
);

alter table public.update_state
    owner to postgres;

