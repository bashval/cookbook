from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet


class UserRelatedModelMixin(
        CreateModelMixin, DestroyModelMixin, GenericViewSet):
    ralated_object_model = None
    related_object_field_name = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.relted_object = self.get_related_object()
        self.filter_parameters = {
            'user': request.user,
            self.related_object_field_name: self.relted_object
        }
        self.request.data.update({
            'user': request.user.id,
            self.related_object_field_name: self.relted_object.id
        })

    def get_object(self):
        if not self.queryset.filter(**self.filter_parameters).exists():
            raise ParseError('Неверный запрос.')
        return self.queryset.get(**self.filter_parameters)

    def get_related_object(self):
        return get_object_or_404(
            self.ralated_object_model,
            pk=self.kwargs['obj_id']
        )

    def perform_create(self, serializer):
        serializer.save(**self.filter_parameters)
