from .models import *
from rest_framework import serializers
from usercontrol_api.serializers import UserSerializer, GroupSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = ('id', 'photo', 'description')
        extra_kwargs = {'photo': {'required': True}}


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVideo
        fields = ('id', 'video', 'description')
        extra_kwargs = {'video': {'required': True}}


class EventSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.FileField(
        use_url=False,
        max_length=1024,
        allow_empty_file=False,
    ),
        write_only=True,
        required=False,
    )
    videos = serializers.ListField(child=serializers.FileField(
        use_url=False,
        allow_empty_file=False,
    ),
        write_only=True,
        required=False,
    )
    action = serializers.CharField(write_only=True, required=False)
    photo_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    video_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False
    )


    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'location', 'attendees', 'max_attendees', 'type', 'author', 'group',
                  'event_date', 'photos', 'videos', 'created_at',
                  'action', 'photo_ids', 'video_ids')
        read_only_fields = ('id', 'author', 'created_at', 'attendees')

    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])

        validated_data['author'] = self.context['request'].user

        event = Event.objects.create(**validated_data)

        if photos_data:
            photo_objects = [EventPhoto(event=event, photo=photo) for photo in photos_data]
            EventPhoto.objects.bulk_create(photo_objects)

        if videos_data:
            video_objects = [EventVideo(event=event, video=video) for video in videos_data]
            EventVideo.objects.bulk_create(video_objects)

        return event

    def update(self, instance, validated_data):
        action = validated_data.pop('action', None)
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])
        photo_ids = validated_data.pop('photo_ids', [])
        video_ids = validated_data.pop('video_ids', [])

        # Обновление основных полей поста
        instance = super().update(instance, validated_data)

        if action == 'add':
            if photos_data:
                photo_objects = [EventPhoto(event=instance, photo=photo) for photo in photos_data]
                EventPhoto.objects.bulk_create(photo_objects)

            if videos_data:
                video_objects = [EventVideo(event=instance, video=video) for video in videos_data]
                EventVideo.objects.bulk_create(video_objects)

        elif action == 'remove':
            if photo_ids:
                photos_to_delete = EventPhoto.objects.filter(event=instance, id__in=photo_ids)

                for photo in photos_to_delete:
                    photo.photo.delete(save=False)
                photos_to_delete.delete()

            if video_ids:
                videos_to_delete = EventVideo.objects.filter(event=instance, id__in=video_ids)
                for video in videos_to_delete:
                    video.video.delete(save=False)
                videos_to_delete.delete()

        return instance

class ListEventSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    first_photo = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'location', 'attendees', 'max_attendees', 'type', 'event_date', 'created_at',
                  'author', 'group', 'first_photo',)

    def get_first_photo(self, obj):
        first_photo = obj.photos.first()
        if first_photo:
            serializer = PhotoSerializer(
                first_photo,
                context=self.context
            )
            return serializer.data
        return None


class DetailEventSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'location', 'attendees', 'max_attendees', 'type', 'author', 'group',
                  'event_date', 'created_at', 'photos', 'videos')
        