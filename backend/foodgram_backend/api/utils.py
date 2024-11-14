# from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.response import Response

# from recipes.models import Recipe
# from .serializers import FavoriteRecipeSerializer

# User = get_user_model()


def user_related_model_request_handler(
        request, obj, serializer, model, lookup_name=None):
    user = request.user
    if lookup_name is None:
        lookup_name = obj._meta.model.__name__.lower()

    lookup = {
        lookup_name: obj,
        'user': user
    }
    if request.method == 'POST':
        if model.objects.filter(**lookup).exists():
            raise serializers.ValidationError('Объект уже был добавлен ранее.')

            # return Response(
            #     {'detail': 'Объект уже был добавлен ранее.'},
            #     status=status.HTTP_400_BAD_REQUEST
            # )
        new_instance = model(**lookup)
        new_instance.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        instance = get_object_or_404(model, **lookup)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_query_by_parameters(objects):
    """Generates query using given objects.
    Uses lookup_name if provided.
    Uses object model name as a lookup_name otherwise.
    """
    query = {}
    print('_____init_obj________:', objects)
    for object in objects:
        print('____object_____;', object, type(object))
        if isinstance(object, dict):
            lookup = object
        else:
            lookup_name = object._meta.model.__name__.lower()
            lookup = {lookup_name: object}
        query.update(lookup)
    return query


def create_related_model_instance(model, objects):
    """Create model instance with the given objects.
    Raise Exception if instance alreeady exists.
    """
    query = get_query_by_parameters(objects)
    if model.objects.filter(**query).exists():
        raise serializers.ValidationError('Объект уже был добавлен ранее.')
    print('________qery________', query)
    instance = model(**query)
    # print('_____inst______', instance)
    instance.save()


def delete_related_model_instance(model, objects):
    """Deletes model instance with the given objects."""
    query = get_query_by_parameters(objects)
    instance = get_object_or_404(model, **query)
    instance.delete()
