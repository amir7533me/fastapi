import pytest
from fastapi.testclient import TestClient

from ...utils import needs_py310

query_required = {
    "detail": [
        {
            "loc": ["query", "needy"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]
}


@pytest.fixture(name="client")
def get_client():
    from docs_src.query_params.tutorial006_py310 import app

    c = TestClient(app)
    return c


@needs_py310
@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        (
            "/items/foo?needy=very",
            200,
            {"item_id": "foo", "needy": "very", "skip": 0, "limit": None},
        ),
        (
            "/items/foo?skip=a&limit=b",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "needy"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["query", "skip"],
                        "msg": "value is not a valid integer",
                        "type": "type_error.integer",
                    },
                    {
                        "loc": ["query", "limit"],
                        "msg": "value is not a valid integer",
                        "type": "type_error.integer",
                    },
                ]
            },
        ),
    ],
)
def test(path, expected_status, expected_response, client: TestClient):
    response = client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@needs_py310
def test_openapi_schema(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {"title": "FastAPI", "version": "0.1.0"},
        "paths": {
            "/items/{item_id}": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "summary": "Read User Item",
                    "operationId": "read_user_item_items__item_id__get",
                    "parameters": [
                        {
                            "required": True,
                            "schema": {"title": "Item Id", "type": "string"},
                            "name": "item_id",
                            "in": "path",
                        },
                        {
                            "required": True,
                            "schema": {"title": "Needy", "type": "string"},
                            "name": "needy",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {
                                "title": "Skip",
                                "type": "integer",
                                "default": 0,
                            },
                            "name": "skip",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"title": "Limit", "type": "integer"},
                            "name": "limit",
                            "in": "query",
                        },
                    ],
                }
            }
        },
        "components": {
            "schemas": {
                "ValidationError": {
                    "title": "ValidationError",
                    "required": ["loc", "msg", "type"],
                    "type": "object",
                    "properties": {
                        "loc": {
                            "title": "Location",
                            "type": "array",
                            "items": {
                                "anyOf": [{"type": "string"}, {"type": "integer"}]
                            },
                        },
                        "msg": {"title": "Message", "type": "string"},
                        "type": {"title": "Error Type", "type": "string"},
                    },
                },
                "HTTPValidationError": {
                    "title": "HTTPValidationError",
                    "type": "object",
                    "properties": {
                        "detail": {
                            "title": "Detail",
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ValidationError"},
                        }
                    },
                },
            }
        },
    }
