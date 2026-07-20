"""
Management command: python manage.py cleanup_cloudinary_temp

Deletes assets in Cloudinary's popups/temp/ and popups/temp/logos/ folders
that are older than 1 hour and have no matching PopupAd record.

Run via cron every hour on the server:
  0 * * * * /path/to/venv/bin/python /path/to/manage.py cleanup_cloudinary_temp
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Delete orphaned Cloudinary temp assets older than 1 hour'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='List assets without deleting')
        parser.add_argument('--hours', type=int, default=1, help='Min age in hours (default: 1)')

    def handle(self, *args, **options):
        try:
            import cloudinary
            import cloudinary.api
            import cloudinary.uploader
        except ImportError:
            self.stderr.write('cloudinary package not installed')
            return

        if not cloudinary.config().cloud_name:
            self.stderr.write('Cloudinary not configured — skipping')
            return

        from core.models import PopupAd

        dry_run = options['dry_run']
        min_age = timedelta(hours=options['hours'])
        cutoff = timezone.now() - min_age

        # Collect all public_ids stored in PopupAd records
        saved_ids = set()
        for p in PopupAd.objects.all():
            for field in (p.image, p.project_logo):
                name = field.name if hasattr(field, 'name') else str(field or '')
                if name:
                    saved_ids.add(name.rsplit('.', 1)[0])  # strip extension

        deleted = 0
        errors = 0

        for folder in ('popups/temp', 'popups/temp/logos'):
            for resource_type in ('image', 'video'):
                try:
                    result = cloudinary.api.resources(
                        type='upload',
                        resource_type=resource_type,
                        prefix=folder + '/',
                        max_results=500,
                    )
                except Exception as e:
                    self.stderr.write(f'Could not list {resource_type}s in {folder}: {e}')
                    continue

                for asset in result.get('resources', []):
                    public_id = asset['public_id']
                    created_at_str = asset.get('created_at', '')
                    try:
                        from datetime import datetime
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        import django.utils.timezone as tz
                        if not tz.is_aware(created_at):
                            created_at = tz.make_aware(created_at)
                    except Exception:
                        continue

                    if created_at > cutoff:
                        continue  # too recent, skip

                    if public_id in saved_ids:
                        continue  # referenced by a real PopupAd, skip

                    if dry_run:
                        self.stdout.write(f'[dry-run] would delete {resource_type}: {public_id}')
                    else:
                        try:
                            cloudinary.uploader.destroy(public_id, resource_type=resource_type, invalidate=True)
                            self.stdout.write(f'Deleted {resource_type}: {public_id}')
                            deleted += 1
                        except Exception as e:
                            self.stderr.write(f'Failed to delete {public_id}: {e}')
                            errors += 1

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Done — deleted {deleted}, errors {errors}'))
