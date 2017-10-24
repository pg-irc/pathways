from behave import given, when, then

KEY = 1
QUESTION_URL = '/v1/questions/{0}/'.format(KEY)

@given(u'a question')
def given_a_question(context):
    data = {'pub_date': '2017-10-17T12:34:56Z', 'question_text': "Original question"}
    url = '/v1/questions/'
    context.response = context.test.client.post(url, data)
    context.test.assertEqual(context.response.status_code, 201)

@given(u'a question with text "{text}"')
def given_a_question_with_text(context, text):
    data = {'pub_date': '2017-10-17T12:34:56Z', 'question_text': text}
    url = '/v1/questions/'
    context.response = context.test.client.post(url, data)
    context.test.assertEqual(context.response.status_code, 201)

@when(u'I create a question with text "{text}"')
def when_i_create_a_question(context, text):
    data = {'pub_date': '2017-10-17T12:34:56Z', 'question_text': text}
    url = '/v1/questions/'
    context.response = context.test.client.post(url, data)
    context.test.assertEqual(context.response.status_code, 201)

@when(u'I update the question with text "{text}"')
def step_impl(context, text):
    post_data = {'pub_date':'2017-10-17T12:34:56Z', 'question_text': text}
    context.response = context.test.client.put(QUESTION_URL, post_data)
    context.test.assertEqual(context.response.status_code, 200)

@when(u'I delete the question')
def when_i_delete_the_question(context):
    context.response = context.test.client.delete(QUESTION_URL)

@then(u'I can get the question with text "{text}"')
def then_i_can_get_the_question(context, text):
    get_response = context.test.client.get(QUESTION_URL)
    context.test.assertEqual(get_response.status_code, 200)
    context.test.assertEqual(get_response.json()['question_text'], text)

@then(u'I can get the updated question')
def then_i_can_get_the_updated_question(context):
    get_response = context.test.client.get(QUESTION_URL)
    context.test.assertEqual(get_response.status_code, 200)
    context.test.assertEqual(get_response.json()['question_text'], 'New question')

@then(u'I fail to get the question')
def then_i_fail_to_get_the_question(context):
    get_response = context.test.client.get(QUESTION_URL)
    context.test.assertEqual(get_response.status_code, 404)
