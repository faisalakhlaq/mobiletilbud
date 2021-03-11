from rest_framework import renderers
import json

class ResponseWrapperRenderer(renderers.JSONRenderer):
    """Append error to the response if it contains errors.
    Otherwise append data to the response. 
    This is used to generate consistent responses."""
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''
        if 'ErrorDetail' in str(data):
            response = json.dumps({'error': data})
        else:
            response = json.dumps({'data': data})
        return response
