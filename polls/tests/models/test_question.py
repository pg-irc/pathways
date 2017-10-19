import datetime
from django.test import TestCase
from django.utils import timezone
from polls import models
from polls import business_logic

class TestQuestion(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = models.Question(pub_date=time)
        self.assertIs(business_logic.was_published_recently(future_question), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = models.Question(pub_date=time)
        self.assertIs(business_logic.was_published_recently(old_question), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = models.Question(pub_date=time)
        self.assertIs(business_logic.was_published_recently(recent_question), True)
