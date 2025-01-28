from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup site configuration for password reset'

    def handle(self, *args, **kwargs):
        # Get or create the site with ID 1
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'Job Portal'
            }
        )
        
        if not created:
            site.domain = '127.0.0.1:8000'
            site.name = 'Job Portal'
            site.save()
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully {"created" if created else "updated"} site configuration')
        ) 