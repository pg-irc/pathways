from rest_framework import viewsets
from polls import models
from polls import serializers


class ChoiceViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ChoiceSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return models.Choice.objects.filter(question=question_id)
