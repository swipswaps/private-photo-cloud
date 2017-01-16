import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def process_media_state(media_id):
    from storage.models import Media
    try:
        media = Media.objects.get(pk=media_id)
    except Media.DoesNotExist:
        return

    media.processing_state.run(media)


# TODO: Have separate task for every processing -- to have reasonable tasks names, not single entry point


class MediaState:
    STATE_CODE = None

    STATES = {}

    @classmethod
    def get_state(cls, code):
        return cls.STATES.get(code, UnknownMediaState)

    @classmethod
    def post_save(cls, media):
        pass

    @classmethod
    def run(cls, media):
        try:
            cls.process(media)
        except Exception as ex:
            # That is breaking an abstraction
            media.processing_state_code = - cls.STATE_CODE
            media.save()
            raise

        media.processing_state = cls.get_next_state(media)

        # That would trigger execution of the next state
        media.save()
        cls.post_save(media)

    @classmethod
    def get_next_state(cls, media):
        raise NotImplementedError()

    @classmethod
    def process(cls, media):
        raise NotImplementedError()


class InitialMediaState(MediaState):
    STATE_CODE = 0

    @classmethod
    def get_next_state(cls, media):
        return MetadataMediaState

    @classmethod
    def process(cls, media):
        logger.debug("do nothing")


class MetadataMediaState(MediaState):
    STATE_CODE = 1

    @classmethod
    def get_next_state(cls, media):
        if media.media_type == media.MEDIA_VIDEO:
            return ScreenshotMediaState
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """check size, hash, get proper content-type, other metadata (e.g. duration)"""
        logger.debug("extract metadata")


class ScreenshotMediaState(MediaState):
    STATE_CODE = 2

    @classmethod
    def get_next_state(cls, media):
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """Extract screenshot of the video"""
        if media.media_type != media.MEDIA_VIDEO:
            return

        logger.debug("extract screenshot")


class ThumbnailMediaState(MediaState):
    STATE_CODE = 3

    @classmethod
    def get_next_state(cls, media):
        return ClassifyMediaState

    @classmethod
    def process(cls, media):
        """Extract thumbnail from image or video's screenshot"""
        logger.debug("extract thumbnail")


class ClassifyMediaState(MediaState):
    STATE_CODE = 4

    @classmethod
    def get_next_state(cls, media):
        return OptimizeForWebMediaState

    @classmethod
    def process(cls, media):
        """Classify the media"""
        from classification import group_media_into_shot, media_categories

        media.categories = list(media_categories.get(media=media))

        group_media_into_shot.process(media_id=media.pk, session_id=media.session_id)

        # TODO: Add more classification

        # TODO: Group SDR + HDR
        # TODO: Group bursts
        # TODO: Mark media with tags, e.g. "RAW", "Orig", "HDR", "Modified"


class OptimizeForWebMediaState(MediaState):
    STATE_CODE = 5

    @classmethod
    def get_next_state(cls, media):
        return ReadyMediaState

    @classmethod
    def process(cls, media):
        """Optimize media for web, e.g. transcode video (multiple codecs) and pack images, find good screenshot"""
        # See http://superuser.com/questions/538112/meaningful-thumbnails-for-a-video-using-ffmpeg
        logger.debug("optimize")
        # TODO: Implement generating content, optimized for viewing in browser, e.g. max 2880 x 1800, jpeg / mp4
        # TODO: Consider generating "original rotated" media, identical with quality but ready for usage


class ReadyMediaState(MediaState):
    STATE_CODE = 6

    @classmethod
    def run(cls, media):
        # do nothing
        pass


class UnknownMediaState(MediaState):
    STATE_CODE = None

    @classmethod
    def run(cls, media):
        # nothing to do
        pass


if not MediaState.STATES:
    MediaState.STATES = (InitialMediaState, MetadataMediaState, ScreenshotMediaState, ThumbnailMediaState,
                         ClassifyMediaState, OptimizeForWebMediaState, ReadyMediaState, UnknownMediaState)
    MediaState.STATES = {state.STATE_CODE: state for state in MediaState.STATES}
