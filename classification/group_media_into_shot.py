import logging

logger = logging.getLogger(__name__)


def process(session_id=None, media_id=None):
    from storage.models import Media

    # as a first version, we check for every image we got -- not aggregate by shot_at

    media = Media.objects.get(pk=media_id)

    if not media.shot_at or media.media_type != Media.MEDIA_IMAGE:
        # Nothing to recognize here
        return

    if media.shot_at.microsecond:
        logger.info('Shot at is precise identifier: {.shot_at:%Y.%m.%d %H:%M%S.%f%Z}'.format(media))
    else:
        logger.warning('Shot at without microsecond cannot be precise identifier: {.shot_at:%Y.%m.%d %H:%M%S.%f%Z}'.format(media))

    # Find all image that were shot exactly at that time
    shot_media = list(Media.objects.filter(shot_at=media.shot_at))

    if len(shot_media) < 2:
        # Somehow it was marked as having the same shot, but actually it is not
        if media.shot_id:
            media.shot_id = None
            media.save(update_fields=['shot_id'])
        return

    logger.info(f'Found multiple media for the same shot: {len(shot_media)}')

    shot_id = [m.shot_id for m in shot_media if m.shot_id]

    if shot_id:
        shot_id = shot_id[0]
    else:
        shot_id = Media.get_next_shot_id()

    Media.objects.filter(id__in=[m.id for m in shot_media]).update(shot_id=shot_id)

    # TODO: Consider other checks since they are more strict
    # TODO: Add check for identical Media.camera
    # TODO: Add check for similar resolution (it is the case for Nikon: JPEG != RAW => 4608x3072 != 4672x3084)
