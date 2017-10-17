from rest_framework import routers
from polls import views

def build_url_patterns():
    router = routers.DefaultRouter()
    register_question(router)
    register_choice(router)
    return router.urls

def register_question(router):
    pattern = r'^questions'
    question_view_set = views.QuestionViewSet
    router.register(pattern, question_view_set)

def register_choice(router):
    pattern_capturing_id = r'^questions/(?P<question_id>[0-9]+)/choices'
    choice_view_set = views.ChoiceViewSet
    router.register(pattern_capturing_id, choice_view_set, base_name='choice')

# pylint: disable=invalid-name
urlpatterns = build_url_patterns()
