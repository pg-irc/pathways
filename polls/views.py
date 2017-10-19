from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from polls import business_logic
from polls import repositories
from polls import models

# pylint: disable=too-many-ancestors
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte=timezone.now()). \
            order_by('-pub_date')[:5]


# pylint: disable=too-many-ancestors
class DetailView(generic.DetailView):
    model = models.Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return models.Question.objects.filter(pub_date__lte=timezone.now())


# pylint: disable=too-many-ancestors
class ResultsView(generic.DetailView):
    model = models.Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    choice_id = request.POST['choice']
    controller = business_logic.VoteController(repositories.ChoiceRepository())
    controller.increment_vote_count_on_choice(question_id, choice_id)
    return HttpResponseRedirect(reverse('polls:results', args=(question_id)))
