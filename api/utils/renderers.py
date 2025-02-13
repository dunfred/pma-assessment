from rest_framework import serializers
from drf_spectacular.utils import OpenApiResponse
from rest_framework.renderers import JSONRenderer


class CustomResponseRenderer(JSONRenderer):
    '''
    A custom Renderer to make all responses return a success key by default
    '''

    res = "data"
    is_paginated = False

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        if data is None:
            return b''

        if self.is_paginated:
            response = {"success": True, "data": data}
        else:
            if self.res == "data":
                response = {
                    "success": True,
                    "data": {
                        **data,
                    },
                }
            else:
                response = {
                "success": True,
                "data": {
                    self.res: data,
                },
            }
        if not str(status_code).startswith('2'):
            response = {
                "success": False,
                "errors": data,
            }
        return super(CustomResponseRenderer, self).render(response, accepted_media_type, renderer_context)


class LoginRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        if data is None:
            return b''
        else:
            response = {"success": True, "data": data}
        if not str(status_code).startswith('2'):
            response = {
                "success": False,
                "errors": data,
            }
        return super(LoginRenderer, self).render(response, accepted_media_type, renderer_context)


class UserResponseRenderer(CustomResponseRenderer):
    res = 'user'

# For overriding extend_schema per API and dynamically nest the actual serializer inside our standard response format.

class StandardResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()

def get_standard_response(serializer=None, example=None):
    """
    Wraps a given serializer inside the standard response structure.
    Handles both single object and list serializers.
    """
    class WrappedStandardResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=True)
        data = serializers.DictField()

    if serializer:
        # Check if the serializer is a ListSerializer (many=True)
        if isinstance(serializer, serializers.ListSerializer):
            class WrappedSerializer(serializers.Serializer):
                success = serializers.BooleanField(default=True)
                data = serializers.ListField(child=serializer)
        else:
            class WrappedSerializer(serializers.Serializer):
                success = serializers.BooleanField(default=True)
                data = serializer()

        return OpenApiResponse(response=WrappedSerializer)
    
    return OpenApiResponse(response=WrappedStandardResponseSerializer, examples=[example] if example else None)
