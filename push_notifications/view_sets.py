from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from push_notifications import models, serializers
from rest_framework.decorators import api_view, action
from push_notifications.models import PushNotificationToken


@api_view(['PUT'])
def hello_world(request, *args, **kwargs):
    the_id = kwargs['theid']
    locale = request.data['locale']

    result = PushNotificationToken()
    result.id = the_id
    result.locale = locale
    result.save()

    return Response({'id': the_id, 'locale': locale})


class TokenViewSet(viewsets.ModelViewSet):
    queryset = models.PushNotificationToken.objects.all()
    serializer_class = serializers.TokenSerializer

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticatedOrReadOnly])
    def create_or_update_token(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return self.bad_request(serializer.errors)
        serializer.save()
        return self.success(serializer.data)

    def bad_request(self, errors):
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def success(self, data):
        return Response(data, status=status.HTTP_201_CREATED)