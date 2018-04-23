# -*- coding: utf-8 -*-
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import device_gateway_pb2 as proto_dot_gateway_dot_device__gateway__pb2


class DeviceGatewayStub(object):
  """DeviceGateway 定义设备网关交互协议.

  所有的 RPC 请求都需要携带 device-id、device-key、device-secret 头作为认证信息.
  device-key、device-secret 首次调用 Authentication 由设备网关下发.

  device-id 是设备的唯一标识，包含字母 "[a-z][A-Z][0-9]-".

  设备调用网关接口失败后，重试请遵循指数退避原则。
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Authentication = channel.unary_unary(
        '/device.proto.gateway.DeviceGateway/Authentication',
        request_serializer=proto_dot_gateway_dot_device__gateway__pb2.AuthenticationRequest.SerializeToString,
        response_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AuthenticationReply.FromString,
        )
    self.Authorization = channel.unary_unary(
        '/device.proto.gateway.DeviceGateway/Authorization',
        request_serializer=proto_dot_gateway_dot_device__gateway__pb2.AuthorizationRequest.SerializeToString,
        response_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AuthorizationReply.FromString,
        )
    self.Stream = channel.stream_stream(
        '/device.proto.gateway.DeviceGateway/Stream',
        request_serializer=proto_dot_gateway_dot_device__gateway__pb2.StreamMessage.SerializeToString,
        response_deserializer=proto_dot_gateway_dot_device__gateway__pb2.StreamMessage.FromString,
        )
    self.AliyunFederationToken = channel.unary_unary(
        '/device.proto.gateway.DeviceGateway/AliyunFederationToken',
        request_serializer=proto_dot_gateway_dot_device__gateway__pb2.AliyunFederationTokenRequest.SerializeToString,
        response_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AliyunFederationTokenReply.FromString,
        )


class DeviceGatewayServicer(object):
  """DeviceGateway 定义设备网关交互协议.

  所有的 RPC 请求都需要携带 device-id、device-key、device-secret 头作为认证信息.
  device-key、device-secret 首次调用 Authentication 由设备网关下发.

  device-id 是设备的唯一标识，包含字母 "[a-z][A-Z][0-9]-".

  设备调用网关接口失败后，重试请遵循指数退避原则。
  """

  def Authentication(self, request, context):
    """Authentication 用于设备向网关进行认证.

    设备向网关认证后，颁发新的认证 device-key、device-secret.
    设备 device-secret 第一次向网关通信后生效.

    设备认证锁定后, 与认证 device-key 不匹配的认证信息失效.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Authorization(self, request, context):
    """Authorization 用于更新设备对外授权码.

    设备对外授权码特性如下:
    1. 有效期较短.
    2. 授权后立即失效.
    3. Stream  重建后需刷新授权码.

    当设备正在被使用时, 返回 grpc 错误码  codes.FailedPrecondition.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Stream(self, request_iterator, context):
    """Stream 用于设备与设备网关之间的双向通信.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def AliyunFederationToken(self, request, context):
    """AliyunFederationToken 用户设备更新阿里云访问临时账号.

    账号信息和设备绑定, 只能访问设备对应的目录.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DeviceGatewayServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Authentication': grpc.unary_unary_rpc_method_handler(
          servicer.Authentication,
          request_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AuthenticationRequest.FromString,
          response_serializer=proto_dot_gateway_dot_device__gateway__pb2.AuthenticationReply.SerializeToString,
      ),
      'Authorization': grpc.unary_unary_rpc_method_handler(
          servicer.Authorization,
          request_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AuthorizationRequest.FromString,
          response_serializer=proto_dot_gateway_dot_device__gateway__pb2.AuthorizationReply.SerializeToString,
      ),
      'Stream': grpc.stream_stream_rpc_method_handler(
          servicer.Stream,
          request_deserializer=proto_dot_gateway_dot_device__gateway__pb2.StreamMessage.FromString,
          response_serializer=proto_dot_gateway_dot_device__gateway__pb2.StreamMessage.SerializeToString,
      ),
      'AliyunFederationToken': grpc.unary_unary_rpc_method_handler(
          servicer.AliyunFederationToken,
          request_deserializer=proto_dot_gateway_dot_device__gateway__pb2.AliyunFederationTokenRequest.FromString,
          response_serializer=proto_dot_gateway_dot_device__gateway__pb2.AliyunFederationTokenReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'device.proto.gateway.DeviceGateway', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
