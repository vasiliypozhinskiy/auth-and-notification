from concurrent import futures

import grpc
import auth_pb2 as auth_pb2
import auth_pb2_grpc as auth_pb2_grpc

from main import app
from app.services.auth_services.auth_services import AUTH_SERVICE
from app.utils.exceptions import InvalidToken


def with_flask_ctx(func):
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


class Auth(auth_pb2_grpc.AuthServicer):

    def Greet(self, request, context):
        print("Got request " + str(request), flush=True)
        return auth_pb2.GreetingResponse(greetings="hello")

    @with_flask_ctx
    def Authorize(self, request, context):
        # access_token = request.access_token
        metadata = {k: v for k, v in context.invocation_metadata()}
        access_token = metadata['access_token']
        try:
            roles, is_su = AUTH_SERVICE.authorize(access_token=access_token)
            out = auth_pb2.AuthorizeResponse(
                roles=roles,
                is_superuser=is_su,
            )
        except InvalidToken:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            out = auth_pb2.AuthorizeResponse()
        return out


def server():
    _server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    auth_pb2_grpc.add_AuthServicer_to_server(Auth(), _server)

    _server.add_insecure_port('[::]:50051')
    _server.start()
    _server.wait_for_termination()


server()
