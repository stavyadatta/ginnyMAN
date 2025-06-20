# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pepper_auto.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pepper_auto.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x11pepper_auto.proto\x1a\x1bgoogle/protobuf/empty.proto\" \n\nImageChunk\x12\x12\n\nimage_data\x18\x01 \x01(\x0c\"&\n\x11\x43onfirmationChunk\x12\x11\n\tconfirmed\x18\x01 \x01(\x08\"@\n\x0c\x45xecuteParam\x12\x12\n\njoint_name\x18\x01 \x01(\t\x12\r\n\x05\x61ngle\x18\x02 \x01(\x02\x12\r\n\x05speed\x18\x03 \x01(\x02\"(\n\rSentenceParam\x12\x17\n\x0fsentence_to_say\x18\x01 \x01(\t2\x9f\x01\n\nPepperAuto\x12-\n\x06GetImg\x12\x16.google.protobuf.Empty\x1a\x0b.ImageChunk\x12\x32\n\rExecuteAction\x12\r.ExecuteParam\x1a\x12.ConfirmationChunk\x12.\n\x08RobotSay\x12\x0e.SentenceParam\x1a\x12.ConfirmationChunkb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_IMAGECHUNK = _descriptor.Descriptor(
  name='ImageChunk',
  full_name='ImageChunk',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='image_data', full_name='ImageChunk.image_data', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=50,
  serialized_end=82,
)


_CONFIRMATIONCHUNK = _descriptor.Descriptor(
  name='ConfirmationChunk',
  full_name='ConfirmationChunk',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='confirmed', full_name='ConfirmationChunk.confirmed', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=84,
  serialized_end=122,
)


_EXECUTEPARAM = _descriptor.Descriptor(
  name='ExecuteParam',
  full_name='ExecuteParam',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='joint_name', full_name='ExecuteParam.joint_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='angle', full_name='ExecuteParam.angle', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='speed', full_name='ExecuteParam.speed', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=124,
  serialized_end=188,
)


_SENTENCEPARAM = _descriptor.Descriptor(
  name='SentenceParam',
  full_name='SentenceParam',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sentence_to_say', full_name='SentenceParam.sentence_to_say', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=190,
  serialized_end=230,
)

DESCRIPTOR.message_types_by_name['ImageChunk'] = _IMAGECHUNK
DESCRIPTOR.message_types_by_name['ConfirmationChunk'] = _CONFIRMATIONCHUNK
DESCRIPTOR.message_types_by_name['ExecuteParam'] = _EXECUTEPARAM
DESCRIPTOR.message_types_by_name['SentenceParam'] = _SENTENCEPARAM
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ImageChunk = _reflection.GeneratedProtocolMessageType('ImageChunk', (_message.Message,), {
  'DESCRIPTOR' : _IMAGECHUNK,
  '__module__' : 'pepper_auto_pb2'
  # @@protoc_insertion_point(class_scope:ImageChunk)
  })
_sym_db.RegisterMessage(ImageChunk)

ConfirmationChunk = _reflection.GeneratedProtocolMessageType('ConfirmationChunk', (_message.Message,), {
  'DESCRIPTOR' : _CONFIRMATIONCHUNK,
  '__module__' : 'pepper_auto_pb2'
  # @@protoc_insertion_point(class_scope:ConfirmationChunk)
  })
_sym_db.RegisterMessage(ConfirmationChunk)

ExecuteParam = _reflection.GeneratedProtocolMessageType('ExecuteParam', (_message.Message,), {
  'DESCRIPTOR' : _EXECUTEPARAM,
  '__module__' : 'pepper_auto_pb2'
  # @@protoc_insertion_point(class_scope:ExecuteParam)
  })
_sym_db.RegisterMessage(ExecuteParam)

SentenceParam = _reflection.GeneratedProtocolMessageType('SentenceParam', (_message.Message,), {
  'DESCRIPTOR' : _SENTENCEPARAM,
  '__module__' : 'pepper_auto_pb2'
  # @@protoc_insertion_point(class_scope:SentenceParam)
  })
_sym_db.RegisterMessage(SentenceParam)



_PEPPERAUTO = _descriptor.ServiceDescriptor(
  name='PepperAuto',
  full_name='PepperAuto',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=233,
  serialized_end=392,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetImg',
    full_name='PepperAuto.GetImg',
    index=0,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=_IMAGECHUNK,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ExecuteAction',
    full_name='PepperAuto.ExecuteAction',
    index=1,
    containing_service=None,
    input_type=_EXECUTEPARAM,
    output_type=_CONFIRMATIONCHUNK,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='RobotSay',
    full_name='PepperAuto.RobotSay',
    index=2,
    containing_service=None,
    input_type=_SENTENCEPARAM,
    output_type=_CONFIRMATIONCHUNK,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_PEPPERAUTO)

DESCRIPTOR.services_by_name['PepperAuto'] = _PEPPERAUTO

# @@protoc_insertion_point(module_scope)
