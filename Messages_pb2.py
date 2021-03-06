# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Messages.proto',
  package='ICD',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0eMessages.proto\x12\x03ICD\"@\n\x07Request\x12\x0c\n\x04user\x18\x01 \x01(\x0c\x12\x12\n\nauth_token\x18\x02 \x01(\x0c\x12\x13\n\x0bidentifiers\x18\x03 \x03(\x0c\"S\n\x08Response\x12\x1b\n\x06result\x18\x01 \x01(\x0e\x32\x0b.ICD.Result\x12\x13\n\x0b\x61\x64\x64\x65\x64_users\x18\x02 \x03(\x0c\x12\x15\n\rremoved_users\x18\x03 \x03(\x0c*~\n\x06Result\x12\x0b\n\x07SUCCESS\x10\x00\x12\x1a\n\x16\x41UTHENTICATION_INVALID\x10\x01\x12\x17\n\x13RATE_LIMIT_EXCEEDED\x10\x02\x12\x18\n\x14REQUEST_DATA_MISSING\x10\x03\x12\x18\n\x14REQUEST_DATA_INVALID\x10\x04\x62\x06proto3')
)

_RESULT = _descriptor.EnumDescriptor(
  name='Result',
  full_name='ICD.Result',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='AUTHENTICATION_INVALID', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RATE_LIMIT_EXCEEDED', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_DATA_MISSING', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_DATA_INVALID', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=174,
  serialized_end=300,
)
_sym_db.RegisterEnumDescriptor(_RESULT)

Result = enum_type_wrapper.EnumTypeWrapper(_RESULT)
SUCCESS = 0
AUTHENTICATION_INVALID = 1
RATE_LIMIT_EXCEEDED = 2
REQUEST_DATA_MISSING = 3
REQUEST_DATA_INVALID = 4



_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='ICD.Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user', full_name='ICD.Request.user', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth_token', full_name='ICD.Request.auth_token', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='identifiers', full_name='ICD.Request.identifiers', index=2,
      number=3, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=23,
  serialized_end=87,
)


_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='ICD.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='ICD.Response.result', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='added_users', full_name='ICD.Response.added_users', index=1,
      number=2, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='removed_users', full_name='ICD.Response.removed_users', index=2,
      number=3, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=89,
  serialized_end=172,
)

_RESPONSE.fields_by_name['result'].enum_type = _RESULT
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
DESCRIPTOR.enum_types_by_name['Result'] = _RESULT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {
  'DESCRIPTOR' : _REQUEST,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:ICD.Request)
  })
_sym_db.RegisterMessage(Request)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSE,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:ICD.Response)
  })
_sym_db.RegisterMessage(Response)


# @@protoc_insertion_point(module_scope)
