# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: email_sender.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x65mail_sender.proto\x12\x0c\x65mail_sender\"5\n\x10SendEmailRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nemail_body\x18\x02 \x01(\t\"\x10\n\x0eSendEmailReply2Z\n\x0b\x45mailSender\x12K\n\tSendEmail\x12\x1e.email_sender.SendEmailRequest\x1a\x1c.email_sender.SendEmailReply\"\x00\x62\x06proto3')



_SENDEMAILREQUEST = DESCRIPTOR.message_types_by_name['SendEmailRequest']
_SENDEMAILREPLY = DESCRIPTOR.message_types_by_name['SendEmailReply']
SendEmailRequest = _reflection.GeneratedProtocolMessageType('SendEmailRequest', (_message.Message,), {
  'DESCRIPTOR' : _SENDEMAILREQUEST,
  '__module__' : 'email_sender_pb2'
  # @@protoc_insertion_point(class_scope:email_sender.SendEmailRequest)
  })
_sym_db.RegisterMessage(SendEmailRequest)

SendEmailReply = _reflection.GeneratedProtocolMessageType('SendEmailReply', (_message.Message,), {
  'DESCRIPTOR' : _SENDEMAILREPLY,
  '__module__' : 'email_sender_pb2'
  # @@protoc_insertion_point(class_scope:email_sender.SendEmailReply)
  })
_sym_db.RegisterMessage(SendEmailReply)

_EMAILSENDER = DESCRIPTOR.services_by_name['EmailSender']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SENDEMAILREQUEST._serialized_start=36
  _SENDEMAILREQUEST._serialized_end=89
  _SENDEMAILREPLY._serialized_start=91
  _SENDEMAILREPLY._serialized_end=107
  _EMAILSENDER._serialized_start=109
  _EMAILSENDER._serialized_end=199
# @@protoc_insertion_point(module_scope)
