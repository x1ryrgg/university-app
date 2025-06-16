from .models import *
from rest_framework import serializers


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPhoto
        fields = ['id', 'photo', 'description']
        extra_kwargs = {'photo': {'required': True}}


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['id', 'video', 'description']
        extra_kwargs = {'video': {'required': True}}


class PostSerializer(serializers.ModelSerializer):
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
        model = Post
        fields = ('id', 'author', 'type', 'description', 'event_date', 'photos', 'videos', 'created_at',
                  'action', 'photo_ids', 'video_ids')
        read_only_fields = ('id', 'author', 'created_at',)

    def validate(self, data):
        action = data.get('action')

        if action and action not in ['add', 'remove']:
            raise serializers.ValidationError(
                {"action": "Допустимые значения 'action': 'add' или 'remove'"}
            )

        if action == 'remove' and not (data.get('photo_ids') or data.get('video_ids')):
            raise serializers.ValidationError(
                {"detail": "Для удаления необходимо указать photo_ids или video_ids, а также action 'remove' "}
            )
        if action == 'add' and not (data.get('photos') or data.get('videos')):
            raise serializers.ValidationError(
                {"detail": "Для добавления необходимо указать photos или videos, а также action 'add' "}
            )

        return data

    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])
        validated_data['author'] = self.context['request'].user

        post = Post.objects.create(**validated_data)

        for photo in photos_data:
            PostPhoto.objects.create(post=post, photo=photo)

        for video in videos_data:
            PostVideo.objects.create(post=post, video=video)

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
                photo_objects = [PostPhoto(post=instance, photo=photo) for photo in photos_data]
                PostPhoto.objects.bulk_create(photo_objects)

            if videos_data:
                video_objects = [PostVideo(post=instance, video=video) for video in videos_data]
                PostVideo.objects.bulk_create(video_objects)

        elif action == 'remove':
            if photo_ids:
                photos_to_delete = PostPhoto.objects.filter(post=instance, id__in=photo_ids)

                for photo in photos_to_delete:
                    photo.photo.delete(save=False)
                photos_to_delete.delete()

            if video_ids:
                videos_to_delete = PostVideo.objects.filter(post=instance, id__in=video_ids)
                for video in videos_to_delete:
                    video.video.delete(save=False)
                videos_to_delete.delete()

        return instance


class PostDetailSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'type', 'description', 'event_date', 'photos', 'videos', 'created_at')
        