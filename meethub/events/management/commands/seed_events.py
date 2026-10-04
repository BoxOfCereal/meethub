from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from meethub.events.models import Event, Category
from meethub.accounts.models import Account


class Command(BaseCommand):
    help = 'Seed the database with sample events around coordinates 44.000000, -71.500000'

    def handle(self, *args, **kwargs):
        # Center coordinates (New Hampshire/Vermont area)
        center_lat = 44.000000
        center_lon = -71.500000

        # Create or get a test user
        test_user, created = Account.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_client': True,
                'is_staff': False,
                'is_active': True,
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {test_user.email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Test user already exists: {test_user.email}')
            )

        # Get all categories
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(
                self.style.ERROR('No categories found. Run "python manage.py seed_categories" first.')
            )
            return

        # Sample event data
        event_templates = [
            {
                'name': 'Mountain Music Festival',
                'venue': 'White Mountain Amphitheater',
                'details': '<p>A weekend celebration of local and regional music talent featuring folk, bluegrass, and indie artists.</p>'
            },
            {
                'name': 'Art Gallery Opening',
                'venue': 'Downtown Art Center',
                'details': '<p>Join us for the opening of our new contemporary art exhibition featuring works from local artists.</p>'
            },
            {
                'name': 'Community Theater Production',
                'venue': 'Town Hall Theater',
                'details': '<p>The local theater group presents their annual spring production. A night of entertainment for the whole family.</p>'
            },
            {
                'name': 'Outdoor Movie Night',
                'venue': 'Riverside Park',
                'details': '<p>Bring your blankets and enjoy a classic film under the stars. Free popcorn and drinks provided.</p>'
            },
            {
                'name': 'Jazz Night at the Cafe',
                'venue': 'Blue Note Cafe',
                'details': '<p>An evening of smooth jazz performed by the regional jazz quartet. Dinner and drinks available.</p>'
            },
            {
                'name': 'Farmers Market',
                'venue': 'Main Street Plaza',
                'details': '<p>Weekly farmers market featuring local produce, handmade crafts, and fresh baked goods.</p>'
            },
            {
                'name': 'Comedy Show',
                'venue': 'Laugh Factory Club',
                'details': '<p>A night of stand-up comedy featuring touring comedians from across the country.</p>'
            },
            {
                'name': 'Book Reading',
                'venue': 'Public Library',
                'details': '<p>Local author reading from their latest novel followed by a Q&A session and book signing.</p>'
            },
            {
                'name': 'Wine Tasting Event',
                'venue': 'Vineyard Estate',
                'details': '<p>Sample wines from local vineyards paired with artisan cheeses and appetizers.</p>'
            },
            {
                'name': 'Charity Run',
                'venue': 'City Park',
                'details': '<p>Annual 5K charity run to support local community programs. All fitness levels welcome.</p>'
            },
            {
                'name': 'Craft Fair',
                'venue': 'Convention Center',
                'details': '<p>Over 100 local artisans showcasing handmade jewelry, pottery, textiles, and more.</p>'
            },
            {
                'name': 'Rock Concert',
                'venue': 'Arena Stadium',
                'details': '<p>Headlining rock band performs live with opening acts. An electric night of music.</p>'
            },
        ]

        # Generate events with coordinates around the center point
        base_date = datetime.now().date()
        events_created = 0
        events_skipped = 0

        for i, template in enumerate(event_templates):
            # Generate random coordinates within ~0.1 degrees of center
            lat_offset = random.uniform(-0.1, 0.1)
            lon_offset = random.uniform(-0.1, 0.1)
            event_lat = center_lat + lat_offset
            event_lon = center_lon + lon_offset

            # Generate date within next 30 days
            days_offset = random.randint(0, 30)
            event_date = base_date + timedelta(days=days_offset)

            # Generate random time
            event_time = datetime.strptime(
                f"{random.randint(10, 20):02d}:{random.randint(0, 59):02d}:00",
                "%H:%M:%S"
            ).time()

            # Select random category
            category = random.choice(categories)

            # Create or get event
            event, created = Event.objects.get_or_create(
                name=template['name'],
                venue=template['venue'],
                date=event_date,
                time=event_time,
                category=category,
                creator=test_user,
                defaults={
                    'details': template['details'],
                    'latitude': event_lat,
                    'longitude': event_lon,
                    'num_of_attendees': random.randint(0, 50),
                }
            )

            if created:
                events_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created event: {event.name} at ({event_lat:.6f}, {event_lon:.6f})'
                    )
                )
            else:
                events_skipped += 1
                self.stdout.write(
                    self.style.WARNING(f'Event already exists: {event.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete! Created {events_created} new events, skipped {events_skipped} existing events.'
            )
        )
