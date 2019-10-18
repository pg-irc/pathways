from rest_framework import serializers
from qa_tool import models


class RelevancyScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RelevancyScore
        fields = ('id', 'value', 'time_stamp', 'algorithm',
                  'search_location', 'user', 'service_at_location')


class AlgorithmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Algorithm
        fields = ('id', 'url', 'name', 'notes')
