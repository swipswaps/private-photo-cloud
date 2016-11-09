# TODO: Implement actual processing per step


class MediaState:
    STATE_CODE = None

    STATES = {}

    @classmethod
    def get_state(cls, code):
        return cls.STATES.get(code, UnknownMediaState)

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
        print("do nothing")


class MetadataMediaState(MediaState):
    STATE_CODE = 1

    @classmethod
    def get_next_state(cls, media):
        from .models import Media

        if media.media_type == Media.MEDIA_VIDEO:
            return ScreenshotMediaState
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """check size, hash, get proper content-type, other metadata (e.g. duration)"""
        print("extract metadata")


class ScreenshotMediaState(MediaState):
    STATE_CODE = 2

    @classmethod
    def get_next_state(cls, media):
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """Extract screenshot of the video"""
        from .models import Media

        if media.media_type != Media.MEDIA_VIDEO:
            return
        print("extract screenshot")


class ThumbnailMediaState(MediaState):
    STATE_CODE = 3

    @classmethod
    def get_next_state(cls, media):
        return OptimizeForWebMediaState

    @classmethod
    def process(cls, media):
        """Extract thumbnail from image or video's screenshot"""
        print("extract thumbnail")


class OptimizeForWebMediaState(MediaState):
    STATE_CODE = 4

    @classmethod
    def get_next_state(cls, media):
        return ReadyMediaState

    @classmethod
    def process(cls, media):
        """Optimize media for web, e.g. transcode video (multiple codecs) and pack images"""
        print("optimize")


class ReadyMediaState(MediaState):
    STATE_CODE = 5

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
                         OptimizeForWebMediaState, ReadyMediaState, UnknownMediaState)
    MediaState.STATES = {state.STATE_CODE: state for state in MediaState.STATES}
