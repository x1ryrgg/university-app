from .models import *
from rest_framework import serializers


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
    )
    videos = serializers.ListField(child=serializers.FileField(
        use_url=False,
        allow_empty_file=False,
    ),
        write_only=True,
    )
    action = serializers.CharField(write_only=True, required=False)
    photo_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    video_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'location', 'attendees', 'max_attendees', 'type', 'author', 'group',
                  'event_date', 'photos', 'videos', 'created_at',
                  'action', 'photo_ids', 'video_ids')
        read_only_fields = ('id', 'author', 'created_at', 'attendees')
        extra_kwargs = {'max_attendees': {'required': True}}

    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])
        validated_data['author'] = self.context['request'].user

        post = Event.objects.create(**validated_data)

        for photo in photos_data:
            EventPhoto.objects.create(post=post, photo=photo)

        for video in videos_data:
            EventVideo.objects.create(post=post, video=video)

        return post

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
                photo_objects = [EventPhoto(post=instance, photo=photo) for photo in photos_data]
                EventPhoto.objects.bulk_create(photo_objects)

            if videos_data:
                video_objects = [EventVideo(post=instance, video=video) for video in videos_data]
                EventVideo.objects.bulk_create(video_objects)

        elif action == 'remove':
            if photo_ids:
                photos_to_delete = EventPhoto.objects.filter(post=instance, id__in=photo_ids)

                for photo in photos_to_delete:
                    photo.photo.delete(save=False)
                photos_to_delete.delete()

            if video_ids:
                videos_to_delete = EventVideo.objects.filter(post=instance, id__in=video_ids)
                for video in videos_to_delete:
                    video.video.delete(save=False)
                videos_to_delete.delete()

        return instance


class DetailEventSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'location', 'attendees', 'max_attendees', 'type', 'author', 'group',
                  'event_date', 'created_at', 'photos', 'videos')
        