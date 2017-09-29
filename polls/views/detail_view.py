from django.views import generic
from django.utils import timezone
from .. import models

class DetailView(generic.DetailView):
    model = models.Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte = timezone.now())
