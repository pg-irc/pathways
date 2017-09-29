from django.views import generic
from .. import models

class ResultsView(generic.DetailView):
    model = models.Question
    template_name = 'polls/results.html'
