class JsonApiMethodException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 405
        self.errors = [
            {
                "status": "405",
                "source": {"pointer": "http/method"},
                "title": "Method Not Allowed",
                "detail": "Method not allowed. Supported methods are: GET, POST, PATCH, DELETE",
            }
        ]


class JsonApiHeaderContentTypeException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 415
        self.errors = [
            {
                "status": "415",
                "source": {"pointer": "http/header/content-type"},
                "title": "Unsupported Media Type",
                "detail": "Content-Type must be set to application/vnd.api+json",
            }
        ]


class JsonApiHeaderAcceptException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 406
        self.errors = [
            {
                "status": "406",
                "source": {"pointer": "http/header/accept"},
                "title": "Not Acceptable",
                "detail": "Accept header must be set to application/vnd.api+json",
            }
        ]


class JsonApiInvalidPayloadException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.errors = [
            {
                "status": "400",
                "source": {"pointer": "http/body"},
                "title": "Invalid JSON Payload",
                "detail": "The body of the request is not valid JSON",
            }
        ]


class JsonApiInvalidVersionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.errors = [
            {
                "status": "400",
                "source": {"pointer": "http/body"},
                "title": "Invalid JSONAPI Version",
                "detail": f"JSONAPI version must be set to {args[0]}",
            }
        ]


class JsonApiInvalidEmptyPayloadException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.errors = [
            {
                "status": "400",
                "source": {"pointer": "http/body"},
                "title": "Invalid Payload",
                "detail": "Body should contain an empty JSON object",
            }
        ]


class JsonApiInvalidRequestException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.errors = [
            {
                "status": "400",
                "source": {"pointer": "http/body"},
                "title": "Invalid Request",
                "detail": "Request is missing 'data', 'type', or 'id' values",
            }
        ]
