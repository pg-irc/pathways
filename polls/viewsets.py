from rest_framework import viewsets
from polls import models
from polls import serializers

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChoiceSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return models.Choice.objects.filter(question=question_id)

    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        serializer.save(question_id=question_id)
