from rest_framework import serializers
from .models import *


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        read_only_fields = ('id',)

    def validate(self, attrs):
        if not attrs.get('email'):
            attrs['email'] = f"{attrs['username']}@вгту_university.edu"

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            role=User.Role.STUDENT, **validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'email', 'first_name', 'last_name')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
        read_only_fields = ('id', )


class DetailGroupSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'students')




# class TeacherCreationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
#         extra_kwargs = {
#             'email': {'required': True},
#             'password': {'write_only': True},
#             "first_name": {"required": True},
#             "last_name": {"required": True}
#         }
#         read_only_fields = ('id', )
#
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             role=User.Role.TEACHER,
#             is_staff=True,
#             **validated_data
#         )
#         return user



