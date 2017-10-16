from rest_framework import serializers
from polls import models


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Question
        fields = ('pk', 'question_text', 'pub_date')
