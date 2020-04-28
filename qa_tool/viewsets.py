from rest_framework import viewsets, permissions, status, authentication
from rest_framework.response import Response
from qa_tool import models, serializers
from django.utils import timezone


class RelevancyScoreViewSet(viewsets.ModelViewSet):
    queryset = models.RelevancyScore.objects.all()
    serializer_class = serializers.RelevancyScoreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request, algorithm_id=None, *args, **kwargs):
        request_data = request.data.copy()
        algorithm_to_append = self.return_algorithm_to_append_to_data(request_data, algorithm_id)
        if algorithm_to_append is None:
            return Response('Algorithm both missing or both present', status=status.HTTP_400_BAD_REQUEST)
        request_data['algorithm'] = algorithm_to_append
        request_data = self.attach_missing_info(request_data, request.user.id)
        serializer = serializers.RelevancyScoreSerializer(data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        try:
            score = models.RelevancyScore.objects.get(pk=pk)
        except models.RelevancyScore.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        request_data = request.data.copy()
        if 'id' in request_data:
            return Response('id of relevancyscore is immutable', status=status.HTTP_400_BAD_REQUEST)
        if 'user' in request_data:
            return Response('user_id of relevancyscore is immutable', status=status.HTTP_400_BAD_REQUEST)
        request_data = self.attach_missing_info(request_data, request.user.id)
        serializer = serializers.RelevancyScoreSerializer(score, data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def return_algorithm_to_append_to_data(self, data, algorithm_id):
        # TODO give variable names, do not return response here, test all 4 cases with both possible endpoints
        algorithm_id_in_data_body = 'algorithm' in data
        algorithm_id_in_url = algorithm_id is not None
        if not algorithm_id_in_data_body and not algorithm_id_in_url:
            return None
        if algorithm_id_in_data_body and algorithm_id_in_url:
            return None
        if not algorithm_id_in_data_body and algorithm_id_in_url:
            return algorithm_id
        if algorithm_id_in_data_body and not algorithm_id_in_url:
            return data['algorithm']

    def attach_missing_info(self, data, user_id):
        data['time_stamp'] = timezone.now()
        data['user'] = user_id
        return data


class AlgorithmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Algorithm.objects.all()
    serializer_class = serializers.AlgorithmSerializer


class SearchLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.SearchLocation.objects.all()
    serializer_class = serializers.SearchLocationSerializer
