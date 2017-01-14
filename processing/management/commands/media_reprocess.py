from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Re-process given media (by id)"

    def add_arguments(self, parser):
        parser.add_argument(
            'ids', metavar='ids', nargs='+', type=int,
            help='Media IDs')
        parser.add_argument(
            '--bg', '-b', action='store_true', dest='use_background', default=False,
            help='Create Celery tasks instead of running in foreground.',
        )

    def handle(self, *, ids=None, use_background=None, **options):
        from storage.models import Media
        from processing import tasks

        fn = tasks.extract_base_metadata

        if use_background:
            fn = fn.delay

        for media_id in ids:
            Media.objects.filter(pk=media_id).update(metadata={})
            fn(media_id=media_id)
