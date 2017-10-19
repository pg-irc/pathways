from rest_framework import serializers
from polls import models

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    # choices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='choice-view-set')
    choices = serializers.SlugRelatedField(many=True, read_only=True, slug_field='choice_text')
    class Meta:
        model = models.Question
        fields = ('pk', 'question_text', 'pub_date', 'choices')


class ChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Choice
        fields = ('pk', 'choice_text', 'votes')
