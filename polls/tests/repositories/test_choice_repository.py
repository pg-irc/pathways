from django.test import TestCase
from ... import models
from ... import repositories
from .. import helpers

class TestChoiceRepository(TestCase):
    def setUp(self):
        self.votes = 34
        self.choice_text = "bar"
        self.question = helpers.create_question(question_text="foo", days=-30)
        self.choice = self.question.choice_set.create(choice_text=self.choice_text, \
                                                      votes=self.votes)
        self.repository = repositories.ChoiceRepository()

    def test_get_choice_returns_choice_based_on_question_id_and_choice_id(self):
        choice = self.repository.get_choice_by_question_id_and_choice_id(self.question.id,\
                                                                         self.choice.id)
        self.assertEqual(choice.question, self.question)
        self.assertEqual(choice.choice_text, self.choice_text)
        self.assertEqual(choice.votes, self.votes)

    def test_get_choice_throws_on_no_matching_question(self):
        invalid_question_id = 234
        with self.assertRaises(models.Question.DoesNotExist):
            self.repository.get_choice_by_question_id_and_choice_id(invalid_question_id, \
                                                                    self.choice.id)

    def test_get_choice_throws_on_no_matching_choice(self):
        invalid_choice_id = 434
        with self.assertRaises(models.Choice.DoesNotExist):
            self.repository.get_choice_by_question_id_and_choice_id(self.question.id, \
                                                                    invalid_choice_id)

    def test_save_choice_updates_value_in_database(self):
        self.choice.votes = 342

        self.repository.save_choice(self.choice)

        choice_from_database = self.question.choice_set.get(pk=self.choice.id)
        self.assertEqual(choice_from_database.votes, 342)
