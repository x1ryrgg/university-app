from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
    inline_serializer
)

from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

@extend_schema_view(
    list=extend_schema(
        summary="Список постов",
        description="Получить список всех постов с пагинацией",
        responses={
            200: PostSerializer(many=True),
            401: OpenApiResponse(description="Не авторизован")
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value=[
                    {
                        "id": 1,
                        "title": "бабушка валя",
                        "content": "Я люблю баб Валю...",
                        "author": 1
                    }
                ],
                response_only=True,
                status_codes=['200']
            )
        ]
    ),
    create=extend_schema(
        summary="Создать пост",
        description="Создание нового поста (требуется аутентификация)",
        request=PostSerializer,
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    "title": "Новый пост",
                    "content": "Содержание поста..."
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Детали поста",
        description="Получить детальную информацию о посте с фотографиями и видео",
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    "post": {
                        "id": 1,
                        "title": "Бабушка валя",
                        "content": "баб валя...",
                        "author": 1
                    },
                    "photos": [
                        {"id": 1, "image": "http://example.com/photo1.jpg"}
                    ],
                    "videos": [
                        {"id": 1, "video_url": "http://example.com/video_with_bab_valya_full.mp4"}
                    ]
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Обновить пост",
        description="Частичное обновление поста: если добавления media, то action == 'add', photos и videos"
                    "если удаление media из поста: action == 'remove', photo_ids [photo_id, ...] и video_ids [video_id, ...]",
        request=PostSerializer,
    ),
    destroy=extend_schema(
        summary="Удалить пост",
        description="Удаление поста (требуется аутентификация)",
    )
)
class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Post.objects.prefetch_related('photos', 'videos').select_related('author')

    # def retrieve(self, request, *args, **kwargs):
    #     post = self.get_object()
    #     photos = PostPhoto.objects.filter(post=post)
    #     videos = PostVideo.objects.filter(post=post)
    #     data = {
    #         'post': self.get_serializer(post).data,
    #         'photos': PhotoSerializer(photos, many=True).data,
    #         'videos': VideoSerializer(videos, many=True).data,
    #     }
    #     return Response(data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return super().get_serializer_class()
