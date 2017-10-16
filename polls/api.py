from rest_framework import routers
from polls import views

def build_api_router():
    router = routers.DefaultRouter()
    register_question_views(router)
    register_choice_views(router)
    return router

def register_question_views(router):
    pattern = r'^questions'
    view_set = views.QuestionViewSet
    router.register(pattern, view_set)

def register_choice_views(router):
    pattern = r'^questions/(?P<question_id>[0-9]+)/choices'
    view_set = views.ChoiceViewSet
    router.register(pattern, view_set, base_name='choice')

# pylint: disable=invalid-name
urlpatterns = build_api_router().urls
