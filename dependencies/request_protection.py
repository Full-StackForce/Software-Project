"""Shared request-protection settings and their OpenAPI documentation."""

REQUEST_HEADER = "X-PulsePoint-Request"
REQUEST_HEADER_VALUE = "1"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def document_request_protection(app) -> None:
    generate_openapi = app.openapi

    def openapi():
        schema = generate_openapi()
        for path in schema.get("paths", {}).values():
            for method, operation in path.items():
                if method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
                    continue
                parameters = operation.setdefault("parameters", [])
                if any(
                    parameter.get("in") == "header"
                    and parameter.get("name", "").lower() == REQUEST_HEADER.lower()
                    for parameter in parameters
                ):
                    continue
                parameters.append({
                    "name": REQUEST_HEADER,
                    "in": "header",
                    "required": True,
                    "description": "Keep the prefilled value 1 for same-origin changes. This is not a password or session token.",
                    "schema": {
                        "type": "string",
                        "enum": [REQUEST_HEADER_VALUE],
                        "default": REQUEST_HEADER_VALUE,
                    },
                })
        return schema

    app.openapi = openapi
