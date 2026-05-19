import logging 
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import exceptions

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension 

logging = logging.getLogger('django')


class SecretKeySitesPermission(permissions.BasePermission):
    """
    Custom permission to only allow specific site to access api
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        safe_key = request.headers.get("api-key", False)
        if (
                not request.user.is_authenticated and (safe_key == settings.API_SECRET_KEY)
        ) or (request.user.is_authenticated and not safe_key):
            return True



# class TraxionAuthPermission(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         authorization_header = request.headers.get("Authorization")
#         if not authorization_header:
#             return {"is_authenticated": False}, None

#         authorization_header = authorization_header.split("Bearer ")[1] 
        
#         return {"is_authenticated": True, "data": data}, None
    
#         logging.error(data)
#         data = 'Session Expired' if str(data) == 'Signature has expired' else data
#         raise exceptions.AuthenticationFailed({
#             "statusCode": 401,
#             "message": data,
#             "is_token_expired": (str(data) == 'Session Expired'),
#             "data": None
#         })

#     def has_permission(self, request, view, obj=None):
#         # Write permissions are only allowed to the owner of the snippet
#         if not request.__dict__.get("_user").get("is_authenticated"):
#             raise exceptions.NotAuthenticated({
#                 "statusCode": 401,
#                 "message": ["Authentication credentials were not provided."],
#                 "is_token_expired": False,
#                 "data": None
#             })
#         return True

#     def authenticate_header(self, request):
#         return request


class TraxionBearerAuthScheme(OpenApiAuthenticationExtension):
    target_class = (
        "utils.permissions.TraxionAuthPermission"  # full import path OR class ref
    )
    name = "bearerAuthTraxion"  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "name": "Authorization",
            "in": "header",
        }


class DimesAuthPermission(authentication.BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get("Secret-key")
        if not authorization_header:
            return {"is_authenticated": False}, None

        if authorization_header == settings.DIMES_KEY:
            return {"is_authenticated": True}, None

        return {"is_authenticated": False}, None

    def authenticate_header(self, request):
        return request

    def has_permission(self, request, view, obj=None):
        # Write permissions are only allowed to the owner of the snippet
        if not request.__dict__.get("_user").get("is_authenticated"):
            raise exceptions.NotAuthenticated({
                "statusCode": 401,
                "message": ["Authentication credentials were not provided."],
                'is_token_expired': False,
                "data": None
            })
        return True


class DimesAuthScheme(OpenApiAuthenticationExtension):
    target_class = (
        "utils.permissions.DimesAuthPermission"  # full import path OR class ref
    )
    name = "dimesAuth"  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Secret-key"
        }
 

class AllowAnyOnGetMethod(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if (
                request.method in ["GET"]
                or request.user
                and request.user["is_authenticated"]
        ):
            return True
        return False
