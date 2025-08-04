from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from .models import *
from .serializers import *
from .permissions import *
import logging

logger = logging.getLogger(__name__)


class RegisterView(CreateAPIView):
    """Endpoint регистрации для студента
    url: /register/
    body: username (str), password (str) password2 (str), email (Optional, str),
            first_name (Optional, str), last_name (Optional, str)
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Endpoint для просмотра профиля
    url: /me/
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user).data

        return Response(serializer, status=status.HTTP_200_OK)

class GroupViewSet(ModelViewSet):
    """Endpoint для просмотра, создания и изменения групп
    url: /group/
    body: post: name (str)
    """
    permission_classes = (IsTeacherOrReadOnly, )
    serializer_class = GroupSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Group.objects.prefetch_related('students')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailGroupSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs) -> Response:
        """ Добавление или удаления студентов из группы
        url: /group/<int:id>/
        body: action ('add'-добавить; 'remove'-удалить)
                students (list [student_id, ...])
        """
        students_data = request.data.get('students', [])
        action = request.data.get('action', None)
        group = self.get_object()

        if action not in ['add', 'remove']:
            return Response(
                {'error': 'Invalid action. Use "add" or "remove"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            students = User.objects.filter(
                id__in=students_data,
                role=User.Role.STUDENT
            )

            if action == 'add':
                students.update(group=group)
                message = f"Students {list(students.values_list('id', flat=True))} added to group"

            elif action == 'remove':
                students.filter(group=group).update(group=None)
                message = f"Students {list(students.values_list('id', flat=True))} removed from group"

            return Response({'message': message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserView(ModelViewSet):
    """Endpoint для просмотра всех пользователей (для тг бота)
    url: /users/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserTelegramSerializer
    queryset = User.objects.all()
    http_method_names = ["get"]
    lookup_url_kwarg = 'tg_id'

    def get_object(self):
        # Получаем tg_id из URL параметров
        tg_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            return self.queryset.get(tg_id=tg_id)
        except User.DoesNotExist:
            raise KeyError("Пользователь с таким telegram ID не найден")
        except User.MultipleObjectsReturned:
            # На случай если вдруг несколько пользователей с одинаковым tg_id
            return self.queryset.filter(tg_id=tg_id).first()


class LinkTelegramId(APIView):
    """Endpoint для свзяи тг аккаунта с апи аккаунта
    url: /user/link_telegram/
    """
    def patch(self, request):
        tg_id = request.data.get('tg_id')
        User.objects.filter(tg_id=tg_id).update(tg_id=None)
        user = request.user
        user.tg_id = tg_id
        user.save()
        return Response({"detail": "tg_id прикреплен к аккаунту. "}, status=status.HTTP_200_OK)


# class TeacherRegisterView(CreateAPIView):
#     """Endpoint регистрации аккаунтов для преподавателей (админ only)
#     url: /register/teacher/
#     body: username (str), password (str), email (str),
#             first_name (str), last_name (str)
#     """
#     queryset = User.objects.all()
#     serializer_class = TeacherCreationSerializer
#     permission_classes = (IsAdminUser, )
#
#     def post(self, request, *args, **kwargs) -> Response:
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'slfkjdlfkjdf'