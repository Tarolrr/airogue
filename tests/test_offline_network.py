"""Regression coverage for the default no-network test policy."""
from __future__ import annotations

import socket

import pytest


def test_offline_suite_rejects_socket_connections(pytestconfig) -> None:
    """An accidental client connection fails before it can send a request."""
    if pytestconfig.getoption("--run-requires-openai-api"):
        pytest.skip("the explicit real-API mode permits network access")

    with socket.socket() as connection:
        with pytest.raises(RuntimeError, match="Network access is disabled"):
            connection.connect(("127.0.0.1", 1))
