from django.test import TestCase
from unittest.mock import Mock
from unittest.mock import MagicMock
from django.http import Http404
from ... import controllers

class TestVoteController(TestCase):
    def setUp(self):
        self.question_id = 23
        self.choice_id = "foo"
        self.initial_vote_count = 3

        self.choice = Mock()
        self.choice.votes = self.initial_vote_count

        self.mock_repository = Mock()
        self.controller = controllers.VoteController(self.mock_repository)
        
    def test_calling_vote_retrieves_choice_from_repository(self):
        self.mock_repository.get_choice_by_question_id_and_choice_id = MagicMock()
        self.controller.vote(self.question_id, self.choice_id)
        self.mock_repository.get_choice_by_question_id_and_choice_id.assert_called_with(self.question_id, self.choice_id)

    def test_calling_vote_increments_votes_on_choice(self):
        self.mock_repository.get_choice_by_question_id_and_choice_id = MagicMock(return_value = self.choice)
        self.controller.vote(self.question_id, self.choice_id)
        self.assertEqual(self.choice.votes, self.initial_vote_count + 1)

    def test_calling_vote_saves_choice_back_to_repository(self):
        self.mock_repository.get_choice_by_question_id_and_choice_id = MagicMock(return_value = self.choice)
        self.mock_repository.save_choice = MagicMock()
        self.controller.vote(self.question_id, self.choice_id)
        self.mock_repository.save_choice.assert_called_with(self.choice)

    # TODO want to use our own class for errors probably
    def throw_no_such_entity(self, question_id, choice_id):
        raise Http404()

    def test_throw_404_if_repository_fails_to_find_question(self):
        self.mock_repository.get_choice_by_question_id_and_choice_id = MagicMock(side_effect = self.throw_no_such_entity)
        with self.assertRaises(Http404):
            self.controller.vote(self.question_id, self.choice_id)

    # TODO returns redirect somehow
     