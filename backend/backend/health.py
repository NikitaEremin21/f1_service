import logging

import redis
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from django.conf import settings


logger = logging.getLogger(__name__)


@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        try:
            redis_client.ping()
        finally:
            redis_client.close()
    except (DatabaseError, redis.RedisError):
        logger.exception("Service health check failed")
        return JsonResponse({"status": "unhealthy"}, status=503)

    return JsonResponse({"status": "ok"})
