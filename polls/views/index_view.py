from django.views import generic
from django.utils import timezone
from .. import models

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
