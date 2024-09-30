from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()


class SessionAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        session_key = scope['cookies'].get('sessionid')

        if session_key:
            try:
                session = await sync_to_async(Session.objects.get)(session_key=session_key)
                user_id = session.get_decoded().get('_auth_user_id')

                if user_id:
                    scope['user'] = await sync_to_async(User.objects.get)(pk=user_id)
                else:
                    scope['user'] = AnonymousUser()
            except Session.DoesNotExist:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
