from django.urls import path, include
from rest_framework.routers import DefaultRouter
from auth_app.views import RegistrationView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', RegistrationView.as_view(), name='registration')
]
