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
from usercontrol_api.permissions import IsTeacherOrReadOnly
from rest_framework.permissions import IsAuthenticated

@extend_schema_view(
    list=extend_schema(
        summary="Список постов",
        description="Получить список всех постов с пагинацией",
        responses={
            200: EventSerializer(many=True),
            401: OpenApiResponse(description="Не авторизован")
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value=[
                    {
                        "id": 7,
                        "title": "test",
                        "description": "описание события",
                        "location": "test location",
                        "attendees": 2,
                        "max_attendees": 100,
                        "type": "conference",
                        "author": {
                            "id": 1,
                            "username": "root",
                            "role": "teacher",
                            "email": "root@example.com",
                            "first_name": "",
                            "last_name": ""
                        },
                        "group": {
                            "id": 1,
                            "name": "БПИ-231"
                        },
                        "event_date": "2025-06-18T18:18:26.400886+03:00",
                        "created_at": "2025-06-18T18:18:26.421883+03:00",
                        "first_photo": {
                            "id": 13,
                            "photo": "http://localhost:8000/media/photo/5404762823990565366_ykiOwa9.jpg",
                            "description": "описание фото..."
                            }

                    },
                ],
                response_only=True,
                status_codes=['200']
            )
        ]
    ),
    create=extend_schema(
        summary="Создать мероприятие",
        description="Создание нового поста (требуется аутентификация)",
        request=EventSerializer,
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    "title": "Пирожки с Олесей",
                    'description': "Кирилл отведал пирожок...",
                    "location": "Челюскинцев 381",
                    'photos': ['media_files'],
                    'videos': ['media_files'],
                    'group_id': 'id группы'
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
                value=
                    {
                        "id": 1,
                        "title": "Экскурсия Костика в аквариум",
                        "description": "18 по идеи пост",
                        "location": "Аквариум \"Поцелуй 11-классницы\"",
                        "attendees": 0,
                        "max_attendees": 0,
                        "type": "excursion",
                        "author": 4,
                        "group": 1,
                        "event_date": "2025-06-20T17:30:00+03:00",
                        "created_at": "2025-06-17T12:12:39.820795+03:00",
                        "photos": [
                            {
                                "id": 30,
                                "photo": "http://localhost:8000/media/photo/Screenshot_2025-05-02_151209_eVc1aVh.png",
                                "description": 'описание...'
                            },
                            {
                                "id": 31,
                                "photo": "http://localhost:8000/media/photo/Screenshot_2025-05-15_173931_esRD9kW.png",
                                "description": 'описание...'
                            }
                        ],
                        "videos": [
                            {
                                "id": 14,
                                "video": "http://localhost:8000/media/video/content_warning_0c895d38_nTqs3LT.webm",
                                "description": 'описание...'
                            }
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
        request=EventSerializer,
    ),
    destroy=extend_schema(
        summary="Удалить пост",
        description="Удаление поста (требуется аутентификация)",
    )
)
class PostViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = (IsTeacherOrReadOnly, )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Event.objects.prefetch_related('photos', 'videos').select_related('author')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailEventSerializer
        return super().get_serializer_class()


