from rest_framework import routers
from polls import viewsets

def url_patterns_for_question_and_choice():
    router = routers.DefaultRouter()
    router.register(r'^questions', viewsets.QuestionViewSet)
    router.register(r'^questions/(?P<question_id>[0-9]+)/choices', viewsets.ChoiceViewSet, 'choice')
    return router.urls

# pylint: disable=invalid-name
urlpatterns = url_patterns_for_question_and_choice()
