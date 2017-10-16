from rest_framework import serializers
from polls import models


class ChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Choice
        fields = ('pk', 'choice_text', 'votes')
