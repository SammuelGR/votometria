import json

import pytest
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_handlers import (
    _format_validation_error,
    handle_http_error,
    handle_unexpected_error,
)


def test_format_validation_error_returns_field_and_message():
    formatted_error = _format_validation_error(
        {
            "loc": ["query", "interval"],
            "msg": "Input should be '1h', '4h', '1d' or '1w'",
        }
    )

    assert formatted_error == {
        "field": "interval",
        "message": "Input should be '1h', '4h', '1d' or '1w'",
    }


@pytest.mark.anyio
async def test_handle_http_error_returns_message_payload():
    response = await handle_http_error(
        request=None,
        exc=StarletteHTTPException(
            status_code=400,
            detail="Invalid date range.",
        ),
    )

    assert response.status_code == 400
    assert json.loads(response.body) == {
        "message": "Invalid date range.",
    }


@pytest.mark.anyio
async def test_handle_unexpected_error_returns_internal_server_error_payload():
    response = await handle_unexpected_error(
        request=None,
        exc=Exception("Database connection failed."),
    )

    assert response.status_code == 500
    assert json.loads(response.body) == {
        "message": "Internal server error.",
    }
