import datetime
from django.utils import timezone
from ... import models

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return models.Question.objects.create(question_text=question_text, pub_date=time)
