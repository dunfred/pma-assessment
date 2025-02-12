from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

class TokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Check if token is blacklisted
            if cache.get(f'blacklisted_token_{token}'):
                return JsonResponse(
                    {'detail': 'Token has been blacklisted'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        return self.get_response(request)