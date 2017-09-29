
class VoteController:
    def __init__(self, choice_repository):
        self.choice_repository = choice_repository

    def vote(self, question_id, choice_id):
        choice = self.choice_repository.get_choice_by_question_id_and_choice_id(question_id, choice_id)
        choice.votes += 1
        self.choice_repository.save_choice(choice)
