"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from config import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView 

urlpatterns = [
    path('d-admin/', admin.site.urls),
]


urlpatterns_v1 = [
    path("api/", include([ 
        path("", include('accounts.urls')),  
        path("", include('merchants.urls')),  
    ]))
]

urlpatterns += urlpatterns_v1 

if settings.PROJECT_ENVIRONMENT != 'production':
    urlpatterns_swagger = [
        # YOUR PATTERNS
        # Optional UI:
        # YOUR PATTERNS 
        path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Optional UI:
        path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema', template_name='swagger-ui.html'), name='swagger-ui'),
        path('docs/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns += urlpatterns_swagger


# Check if local settings are imported
if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)