from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Re-process given media (by id)"

    def add_arguments(self, parser):
        parser.add_argument(
            'ids', metavar='ids', nargs='*', type=int,
            help='Media IDs')
        parser.add_argument(
            '--all', action='store_true', dest='all_media', default=False,
            help='Re-process all media',
        )
        parser.add_argument(
            '--failed', action='store_true', dest='failed_media', default=False,
            help='Re-process all media with errors',
        )

    def handle(self, *, ids=None, all_media=None, failed_media=None, **options):
        from storage.models import Media
        from processing import tasks

        fn = tasks.extract_base_metadata.delay

        if all_media:
            ids += list(Media.objects.values_list('id', flat=True))
        elif failed_media:
            ids += list(Media.objects.filter(processing_state_code__lt=0).values_list('id', flat=True))
        elif not ids:
            raise CommandError('Must provide at least one ID or use flags --failed or --all')

        if not ids:
            self.stderr.write('Nothing to do.')
            return

        self.stderr.write(f'Re-process {len(ids)} media...')

        for media_id in ids:
            Media.objects.filter(pk=media_id).update(metadata={})
            fn(media_id=media_id)

        self.stderr.write('Done.')
