from django.http import HttpResponseRedirect
from django.urls import reverse
from .. import controllers
from .. import repositories

def vote(request, question_id):
    choice_id = request.POST['choice']
    controllers.VoteController(repositories.ChoiceRepository()).vote(question_id, choice_id)
    return HttpResponseRedirect(reverse('polls:results', args = (question_id)))
