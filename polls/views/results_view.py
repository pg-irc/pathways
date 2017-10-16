from django.views import generic
from polls import models

# pylint: disable=too-many-ancestors
class ResultsView(generic.DetailView):
    model = models.Question
    template_name = 'polls/results.html'
