from django.http import HttpResponseRedirect
from django.urls import reverse
from polls import controllers
from polls import repositories

def vote(request, question_id):
    choice_id = request.POST['choice']
    controller = controllers.VoteController(repositories.ChoiceRepository())
    controller.increment_vote_count_on_choice(question_id, choice_id)
    return HttpResponseRedirect(reverse('polls:results', args=(question_id)))
