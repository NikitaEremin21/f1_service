"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from services.http_client import http_client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

_application = get_asgi_application()


async def application_with_lifespan(scope, receive, send):

    if scope['type'] == 'lifespan':
        while True:
            message = await receive()

            if message['type'] == 'lifespan.startup':
                await http_client.get_session()
                await send({'type': 'lifespan.startup.complete'})

            elif message['type'] == 'lifespan.shutdown':
                await http_client.close()
                await send({'type': 'lifespan.shutdown.complete'})
                break

    else:
        await _application(scope, receive, send)

application = application_with_lifespan

