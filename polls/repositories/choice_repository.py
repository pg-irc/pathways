from django.shortcuts import get_object_or_404
from .. import models

# to break the business logic dependency on the framework, this class would
# adapt DTOs to a non-framework DTOs, this would make it impossible to make
# changes to the database outside of repository code
class ChoiceRepository:
    def get_choice_by_question_id_and_choice_id(self, question_id, choice_id):
        question = models.Question.objects.get(pk = question_id)
        return question.choice_set.get(pk = choice_id)

    def save_choice(self, choice):
        choice.save()
