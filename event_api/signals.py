import logging
import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import *

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Event)
def delete_post_media_files(sender, instance, **kwargs):
    photos = EventPhoto.objects.filter(event=instance)
    for photo in photos:
        try:
            if photo.photo and os.path.exists(photo.photo.path):
                os.remove(photo.photo.path)
                logger.info(f"Deleted photo file: {photo.photo.path}")
        except Exception as e:
            logger.error(f"Error deleting photo file {photo.photo.path}: {str(e)}")

    videos = EventVideo.objects.filter(event=instance)
    for video in videos:
        try:
            if video.video and os.path.exists(video.video.path):
                os.remove(video.video.path)
                logger.info(f"Deleted video file: {video.video.path}")
        except Exception as e:
            logger.error(f"Error deleting video file {video.video.path}: {str(e)}")
