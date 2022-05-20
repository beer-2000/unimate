from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from knox.models import AuthToken
from knox.settings import CONSTANTS


@database_sync_to_async
def get_user(headers):
    try:
        # header에서 Token 받아오기
        token_name, token_key = headers[b'authorization'].decode().split()
        # Token이 존재한다면 AuthToken에서 user 반환하기
        if token_name == 'Token':
            # token_key는 db에 'TOKEN_KEY_LENGTH' 값만큼의 길이만 저장된다.
            token = AuthToken.objects.get(token_key=token_key[:CONSTANTS.TOKEN_KEY_LENGTH])
            return token.user
    except AuthToken.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            scope['user'] = await get_user(headers)
        return await self.inner(scope, receive, send)


class TokenAuthMiddlewareInstance:
    """
    Yeah, this is black magic:
    https://github.com/django/channels/issues/1399
    """

    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        headers = dict(self.scope['headers'])
        if b'authorization' in headers:
            self.scope['user'] = await get_user(headers)
        inner = self.inner(self.scope)
        return await inner(receive, send)


def TokenAuthMiddlewareStack(inner): return TokenAuthMiddleware(
    AuthMiddlewareStack(inner))    
