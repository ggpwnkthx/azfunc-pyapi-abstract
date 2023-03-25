from libs.utils.threaded import current
from marshmallow_jsonapi import Schema, fields

def create_jsonapi_schema(DynamicSchemaClass):
    class JsonApiSchema(Schema):
        data = fields.List(fields.Nested(DynamicSchemaClass), attribute='items')
        links = fields.Method('get_pagination_links')

        def get_pagination_links(self, obj):
            request = self.context.get('request', None)
            if request:
                query_params = current.request.params
                base_url = current.request.url
                prev_page = None
                next_page = None

                page = int(query_params.get('page', 1))
                per_page = int(query_params.get('per_page', 10))

                if page > 1:
                    prev_page = f"{base_url}?page={page-1}&per_page={per_page}"

                if len(obj) > (page * per_page):
                    next_page = f"{base_url}?page={page+1}&per_page={per_page}"

                return {
                    'prev': prev_page,
                    'next': next_page
                }

    return JsonApiSchema