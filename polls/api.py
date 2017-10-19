from rest_framework import routers
from polls import views

def url_patterns_for_question_and_choice():
    router = routers.DefaultRouter()
    router.register(r'^questions', views.QuestionViewSet)
    router.register(r'^questions/(?P<question_id>[0-9]+)/choices', views.ChoiceViewSet, 'choice')
    return router.urls

# pylint: disable=invalid-name
urlpatterns = url_patterns_for_question_and_choice()
