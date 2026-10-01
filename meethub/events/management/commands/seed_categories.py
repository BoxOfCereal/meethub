from django.core.management.base import BaseCommand
from meethub.events.models import Category


class Command(BaseCommand):
    help = 'Seed the database with initial categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'music',
                'description': 'Music events including concerts, festivals, and performances'
            },
            {
                'name': 'show',
                'description': 'Shows including theater, comedy, and entertainment performances'
            },
            {
                'name': 'viewing',
                'description': 'Viewing events including movie screenings, exhibitions, and presentations'
            },
        ]

        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Categories seeded successfully!')
        )
