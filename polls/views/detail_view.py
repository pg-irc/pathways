from django.views import generic
from django.utils import timezone
from polls import models

# pylint: disable=too-many-ancestors
class DetailView(generic.DetailView):
    model = models.Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte=timezone.now())
