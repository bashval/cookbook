from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import AvatarSerializer


class UsersViewSet(BaseUserViewSet):

    def get_serializer_class(self):
        if self.action == 'avatar':
            return AvatarSerializer
        return super().get_serializer_class()

    @action(['get'], detail=False, permission_classes=[CurrentUserOrAdmin])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        instance = self.get_instance()
        if request.method == 'PUT':
            serializer = self.get_serializer(
                instance=instance, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            instance.avatar = None
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
