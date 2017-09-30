from .. import models

class ChoiceRepository:
    @staticmethod
    def get_choice_by_question_id_and_choice_id(question_id, choice_id):
        question = models.Question.objects.get(pk=question_id)
        return question.choice_set.get(pk=choice_id)

    @staticmethod
    def save_choice(choice):
        choice.save()
