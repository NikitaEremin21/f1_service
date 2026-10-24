import json
from unittest.mock import MagicMock, patch

import redis
from django.db import DatabaseError
from django.test import RequestFactory, SimpleTestCase

from backend.health import health_check


class HealthCheckTests(SimpleTestCase):
    @patch("backend.health.redis.Redis")
    @patch("backend.health.connection")
    def test_returns_ok_when_database_and_redis_are_available(
        self, mock_connection, mock_redis
    ):
        mock_connection.cursor.return_value = MagicMock()
        mock_redis.return_value.ping.return_value = True

        response = health_check(RequestFactory().get("/health/"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "ok"})
        mock_connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT 1"
        )
        mock_redis.return_value.ping.assert_called_once_with()

    @patch("backend.health.redis.Redis")
    @patch("backend.health.connection")
    def test_returns_service_unavailable_when_database_is_unavailable(
        self, mock_connection, mock_redis
    ):
        mock_connection.cursor.side_effect = DatabaseError("offline")

        response = health_check(RequestFactory().get("/health/"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {"status": "unhealthy"})
        mock_redis.assert_not_called()

    @patch("backend.health.redis.Redis")
    @patch("backend.health.connection")
    def test_returns_service_unavailable_when_redis_is_unavailable(
        self, mock_connection, mock_redis
    ):
        mock_connection.cursor.return_value = MagicMock()
        mock_redis.return_value.ping.side_effect = redis.RedisError("offline")

        response = health_check(RequestFactory().get("/health/"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {"status": "unhealthy"})
        mock_redis.return_value.close.assert_called_once_with()
