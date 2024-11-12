from rest_framework import routers

from django.urls import path, include

from social import views

router = routers.SimpleRouter()

router.register(r'posts', views.PostViewSet, basename='posts')

urlpatterns = [
    path("", include(router.urls)),
]

app_name = 'social'
