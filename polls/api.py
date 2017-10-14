from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^', include(router.urls))
]
