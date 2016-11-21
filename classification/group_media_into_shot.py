import logging

logger = logging.getLogger(__name__)


def process(session_id=None, media_id=None):
    from storage.models import Media

    # as a first version, we check for every image we got -- not aggregate by shot_at

    media = Media.objects.get(pk=media_id)

    if not media.shot_at or media.media_type != Media.MEDIA_PHOTO:
        # Nothing to recognize here
        return

    if media.shot_at.microsecond:
        logger.info('Shot at is precise identifier: {.shot_at:%Y.%m.%d %H:%M%S.%f%Z}'.format(media))
    else:
        logger.warning('Shot at without microsecond cannot be precise identifier: {.shot_at:%Y.%m.%d %H:%M%S.%f%Z}'.format(media))

    # Find all image that were shot exactly at that time
    qs = Media.objects.filter(shot_at=media.shot_at).exclude(pk=media.id)

    if not qs.exists():
        return

    logger.info('Found other media for the same shot: {}'.format(qs.values('id', 'size_bytes', 'shot_at')))

    # TODO: Implement grouping using the same shot_id
    # TODO: Use postgresql sequences for this:
    #   create sequence shots;
    #   select nextval('shots'); # => 1
    #   select nextval('shots'); # => 2
    #   select nextval('shots'); # => 3

    # TODO: Consider other checks since they are more strict
    # TODO: Add check for identical camera
    # TODO: Add check for similar resolution (it is the case for Nikon: JPEG != RAW => 4608x3072 != 4672x3084)
