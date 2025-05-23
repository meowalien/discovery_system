# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: telegram_reader.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'telegram_reader.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15telegram_reader.proto\x12\x08telegram\x1a\x1bgoogle/protobuf/empty.proto\"7\n\x13\x43reateClientRequest\x12\x0e\n\x06\x61pi_id\x18\x01 \x01(\x05\x12\x10\n\x08\x61pi_hash\x18\x02 \x01(\t\"*\n\x14\x43reateClientResponse\x12\x12\n\nsession_id\x18\x01 \x01(\t\")\n\x13UnLoadClientRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\"\'\n\x11LoadClientRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\"8\n\x13SignInClientRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\x12\r\n\x05phone\x18\x02 \x01(\t\"\x8c\x01\n\x14SignInClientResponse\x12\x35\n\x06status\x18\x01 \x01(\x0e\x32%.telegram.SignInClientResponse.Status\x12\x17\n\x0fphone_code_hash\x18\x02 \x01(\t\"$\n\x06Status\x12\r\n\tNEED_CODE\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\"s\n\x15\x43ompleteSignInRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\x12\r\n\x05phone\x18\x02 \x01(\t\x12\x0c\n\x04\x63ode\x18\x03 \x01(\t\x12\x17\n\x0fphone_code_hash\x18\x04 \x01(\t\x12\x10\n\x08password\x18\x05 \x01(\t\"*\n\x13ListClientsResponse\x12\x13\n\x0bsession_ids\x18\x01 \x03(\t\"\'\n\x11GetDialogsRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\"#\n\x06\x44ialog\x12\n\n\x02id\x18\x01 \x01(\x03\x12\r\n\x05title\x18\x02 \x01(\t\"7\n\x12GetDialogsResponse\x12!\n\x07\x64ialogs\x18\x01 \x03(\x0b\x32\x10.telegram.Dialog\"-\n\x17StartReadMessageRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t2\xee\x04\n\x15TelegramReaderService\x12M\n\x0c\x43reateClient\x12\x1d.telegram.CreateClientRequest\x1a\x1e.telegram.CreateClientResponse\x12\x41\n\nLoadClient\x12\x1b.telegram.LoadClientRequest\x1a\x16.google.protobuf.Empty\x12\x45\n\x0cUnLoadClient\x12\x1d.telegram.UnLoadClientRequest\x1a\x16.google.protobuf.Empty\x12M\n\x0cSignInClient\x12\x1d.telegram.SignInClientRequest\x1a\x1e.telegram.SignInClientResponse\x12O\n\x14\x43ompleteSignInClient\x12\x1f.telegram.CompleteSignInRequest\x1a\x16.google.protobuf.Empty\x12\x44\n\x0bListClients\x12\x16.google.protobuf.Empty\x1a\x1d.telegram.ListClientsResponse\x12G\n\nGetDialogs\x12\x1b.telegram.GetDialogsRequest\x1a\x1c.telegram.GetDialogsResponse\x12M\n\x10StartReadMessage\x12!.telegram.StartReadMessageRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'telegram_reader_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CREATECLIENTREQUEST']._serialized_start=64
  _globals['_CREATECLIENTREQUEST']._serialized_end=119
  _globals['_CREATECLIENTRESPONSE']._serialized_start=121
  _globals['_CREATECLIENTRESPONSE']._serialized_end=163
  _globals['_UNLOADCLIENTREQUEST']._serialized_start=165
  _globals['_UNLOADCLIENTREQUEST']._serialized_end=206
  _globals['_LOADCLIENTREQUEST']._serialized_start=208
  _globals['_LOADCLIENTREQUEST']._serialized_end=247
  _globals['_SIGNINCLIENTREQUEST']._serialized_start=249
  _globals['_SIGNINCLIENTREQUEST']._serialized_end=305
  _globals['_SIGNINCLIENTRESPONSE']._serialized_start=308
  _globals['_SIGNINCLIENTRESPONSE']._serialized_end=448
  _globals['_SIGNINCLIENTRESPONSE_STATUS']._serialized_start=412
  _globals['_SIGNINCLIENTRESPONSE_STATUS']._serialized_end=448
  _globals['_COMPLETESIGNINREQUEST']._serialized_start=450
  _globals['_COMPLETESIGNINREQUEST']._serialized_end=565
  _globals['_LISTCLIENTSRESPONSE']._serialized_start=567
  _globals['_LISTCLIENTSRESPONSE']._serialized_end=609
  _globals['_GETDIALOGSREQUEST']._serialized_start=611
  _globals['_GETDIALOGSREQUEST']._serialized_end=650
  _globals['_DIALOG']._serialized_start=652
  _globals['_DIALOG']._serialized_end=687
  _globals['_GETDIALOGSRESPONSE']._serialized_start=689
  _globals['_GETDIALOGSRESPONSE']._serialized_end=744
  _globals['_STARTREADMESSAGEREQUEST']._serialized_start=746
  _globals['_STARTREADMESSAGEREQUEST']._serialized_end=791
  _globals['_TELEGRAMREADERSERVICE']._serialized_start=794
  _globals['_TELEGRAMREADERSERVICE']._serialized_end=1416
# @@protoc_insertion_point(module_scope)
