from rest_framework import viewsets
from qa_tool import models, serializers


class RelevantScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.RelevancyScore.objects.all()
    serializer_class = serializers.RelevancyScoreSerializer
