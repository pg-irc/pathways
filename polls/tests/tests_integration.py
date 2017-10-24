import unittest
from rest_framework import test as rest_test

def create_question_entity(client):
    data = {'pub_date': '2017-10-17T12:34:56Z', 'question_text': 'Original question'}
    url = '/v1/questions/'
    return client.post(url, data)

def create_choice_entity(client, question):
    data = {'choice_text': 'Original choice', 'votes': 3}
    parent_key = question.json()['pk']
    url = '/v1/questions/{0}/choices/'.format(parent_key)
    return client.post(url, data)


class QuestionEntityTests(rest_test.APITestCase):
    def setUp(self):
        self.post_response = create_question_entity(self.client)
        primary_key = self.post_response.json()['pk']
        self.url = '/v1/questions/{0}/'.format(primary_key)

    def test_can_create_entity(self):
        self.assertEqual(self.post_response.status_code, 201)
        self.assertEqual(self.post_response.json()['question_text'], 'Original question')

    def test_can_get_entity(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()['question_text'], 'Original question')

    def test_can_update_entity(self):
        post_data = {'pub_date':'2017-10-17T12:34:56Z', 'question_text': 'New question'}
        put_response = self.client.put(self.url, post_data)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.json()['question_text'], 'New question')

    def test_can_delete_entity(self):
        delete_response = self.client.delete(self.url)
        self.assertEqual(delete_response.status_code, 204)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 404)


class ChoiceEntityTests(rest_test.APITestCase):
    def setUp(self):
        self.parent_post_response = create_question_entity(self.client)
        self.post_response = create_choice_entity(self.client, self.parent_post_response)
        self.parent_key = self.parent_post_response.json()['pk']
        self.child_key = self.post_response.json()['pk']
        self.url = '/v1/questions/{0}/choices/{1}/'.format(self.parent_key, self.child_key)

    def test_can_create_entity(self):
        self.assertEqual(self.post_response.status_code, 201)
        self.assertEqual(self.post_response.json()['choice_text'], 'Original choice')

    def test_can_get_entity(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()['choice_text'], 'Original choice')

    def test_can_update_entity(self):
        post_data = {'choice_text': 'New choice', 'votes': 3}
        put_response = self.client.put(self.url, post_data)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.json()['choice_text'], 'New choice')

    def test_can_delete_entity(self):
        delete_response = self.client.delete(self.url)
        self.assertEqual(delete_response.status_code, 204)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 404)

    @unittest.expectedFailure
    def test_can_vote_on_choice(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.json()['votes'], 3)
        vote_url = '/v1/questions/{0}/choices/{1}/vote'.format(self.parent_key, self.child_key)
        post_response = self.client.post(vote_url, content_type='application/json')
        # TODO not sure if 301 is the right response here, watch for missing /
        self.assertEqual(post_response.status_code, 301)
        self.assertEqual(post_response.json()['votes'], 4)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.json()['votes'], 4)


class QuestionChoiceEntityTests(rest_test.APITestCase):
    def setUp(self):
        parent_post_response = create_question_entity(self.client)
        parent_key = parent_post_response.json()['pk']
        self.parent_url = '/v1/questions/{0}/'.format(parent_key)
        self.post_response = create_choice_entity(self.client, parent_post_response)
        child_key = self.post_response.json()['pk']
        self.url = '/v1/questions/{0}/choices/{1}/'.format(parent_key, child_key)

    def test_can_get_entity(self):
        get_response = self.client.get(self.parent_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()['choices'][0], 'Original choice')

    def test_deleting_parent_removes_child_entities(self):
        delete_response = self.client.delete(self.parent_url)
        self.assertEqual(delete_response.status_code, 204)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 404)
