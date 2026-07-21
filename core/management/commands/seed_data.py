from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ProjectInfo, FlatType, Amenity, Review, BuildingFlat


class Command(BaseCommand):
    help = 'Seed initial data for Silverwoods'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@silverwoods.co.in', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin user created (admin/admin123)'))

        project = ProjectInfo.load()
        project.name = "Silverwoods"
        project.tagline = (
            "Silverwoods is more than just a home, it's a lifestyle statement. "
            "Come, discover your dream villa and embark on a journey of serene luxury."
        )
        project.description = (
            "Escape the urban hustle and embrace a life of serene luxury at Silverwoods, "
            "an exclusive residential villa project meticulously designed for those who seek "
            "comfort, privacy, and sophisticated living. Nestled amidst lush greenery on a "
            "generous 8.1 Acre expanse, Silverwoods offers an unparalleled lifestyle just "
            "a short drive from the city's Southern Bypass."
        )
        project.address = "Dr. B.C. Roy Road, Dingelpota"
        project.city = "Dingelpota"
        project.state = "West Bengal"
        project.pincode = "700151"
        project.phone = "+91 7411781881"
        project.email = "info@silverwoods.co.in"
        project.website = "https://deltarealtech.in/"
        project.director_name = "Delta Realtech"
        project.director_title = "Developer & Promoter"
        project.director_bio = (
            "Delta Realtech is a renowned real estate development company committed to "
            "delivering signature landmarks that blend luxury, comfort, and sustainability. "
            "With a vision to create exceptional living spaces, Delta Realtech brings decades "
            "of expertise in crafting homes that stand as a testament to quality and innovation."
        )
        project.rera_number = "WBRERA/P/2024/001234"
        project.total_units = 121
        project.total_floors = 2
        project.total_towers = 6
        project.project_area = "8.1 Acres"
        project.possession_date = "October 2029"
        project.map_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3684.0!2d88.35!3d22.57!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjLCsDM0JzEyLjAiTiA4OMKwMjEnMDAuMCJF!5e0!3m2!1sen!2sin!4v1"
        project.save()
        self.stdout.write(self.style.SUCCESS('Project info seeded'))

        flat_types_data = [
            {'name': 'Villa Type 1', 'bhk': 4, 'carpet_area': '2,400.36 sq.ft', 'price': 11521728, 'price_per_sqft': 4800, 'order': 1,
             'description': 'Independent 4 BHK (G+2) villa with maximum space, light, and ventilation. Includes private backyard garden and plunge pool.'},
            {'name': 'Villa Type 2', 'bhk': 4, 'carpet_area': '2,557.51 sq.ft', 'price': 12276048, 'price_per_sqft': 4800, 'order': 2,
             'description': 'Spacious 4 BHK (G+2) villa with premium interiors, private garden, plunge pool, and panoramic green views.'},
            {'name': 'Villa Type 3', 'bhk': 4, 'carpet_area': '2,181.96 sq.ft', 'price': 10473408, 'price_per_sqft': 4800, 'order': 3,
             'description': 'Expansive 4 BHK (G+2) villa with designer finishes, double-height living, private garden, and plunge pool.'},
            {'name': 'Villa Type 4', 'bhk': 4, 'carpet_area': '2,286.72 sq.ft', 'price': 10976256, 'price_per_sqft': 4800, 'order': 4,
             'description': 'Grand 4 BHK (G+2) villa with luxury interiors, spacious terrace, private backyard garden, and plunge pool.'},
            {'name': 'Villa Type 5', 'bhk': 4, 'carpet_area': '3,175.36 sq.ft', 'price': 15241728, 'price_per_sqft': 4800, 'order': 5,
             'description': 'Premium 4 BHK (G+2) villa with home automation, private garden, plunge pool, and exclusive amenities.'},
            {'name': 'Villa Type 6', 'bhk': 4, 'carpet_area': '3,069.95 sq.ft', 'price': 14735760, 'price_per_sqft': 4800, 'order': 6,
             'description': 'Ultra-luxury 4 BHK (G+2) villa — the largest layout with maximum privacy, garden, plunge pool, and bespoke finishes.'},
        ]
        FlatType.objects.all().delete()
        for ftd in flat_types_data:
            FlatType.objects.create(**ftd)
        self.stdout.write(self.style.SUCCESS('Flat types seeded'))

        amenities_data = [
            {'name': 'Infinity Pool', 'icon': 'pool', 'description': 'Stunning infinity pool with dedicated lounge area — where every day is a staycation', 'order': 1},
            {'name': '50,000 sq.ft Clubhouse', 'icon': 'club', 'description': 'Massive clubhouse — the ultimate social hub for the privileged few, with banquet halls and bar area', 'order': 2},
            {'name': 'Gym, Yoga & Zumba', 'icon': 'fitness', 'description': 'Fully equipped gym, yoga rooms, Zumba rooms, and a dedicated health arena', 'order': 3},
            {'name': 'Sports Arena', 'icon': 'child', 'description': 'Badminton, football, volleyball, billiards, and table tennis — recreation for all ages', 'order': 4},
            {'name': 'Kids Play & Pet Zones', 'icon': 'child', 'description': 'Great outdoors designed for little explorers — dedicated kids play and pet-friendly zones', 'order': 5},
            {'name': 'Gated Security', 'icon': 'security', 'description': 'High-tech gated community with 24/7 surveillance ensuring a safe, worry-free environment', 'order': 6},
            {'name': 'Guest Rooms & Banquet', 'icon': 'club', 'description': 'Social spaces with guest rooms, banquet halls for gatherings and celebrations', 'order': 7},
            {'name': 'Private Garden & Pool', 'icon': 'garden', 'description': 'Every villa includes a private backyard garden and a personal plunge pool', 'order': 8},
            {'name': 'Traffic-Free Podium', 'icon': 'parking', 'description': 'Grand traffic-free podium for safe walking, cycling, and community activities', 'order': 9},
        ]
        Amenity.objects.all().delete()
        for ad in amenities_data:
            Amenity.objects.create(**ad)
        self.stdout.write(self.style.SUCCESS('Amenities seeded'))

        reviews_data = [
            {'name': 'Anita Sharma', 'rating': 5, 'comment': 'Silverwoods has truly redefined villa living. The quality of construction and the serene environment make it a perfect home.', 'designation': 'Homeowner'},
            {'name': 'Vikram Patel', 'rating': 5, 'comment': 'Exceptional project by Delta Realtech. The villa layout is brilliant and amenities are world-class. Best investment decision!', 'designation': 'Business Owner'},
            {'name': 'Priya Mukherjee', 'rating': 4, 'comment': 'Beautiful villas with great ventilation and natural light. The landscaped gardens are a huge plus for our family.', 'designation': 'Doctor'},
        ]
        for rd in reviews_data:
            Review.objects.update_or_create(name=rd['name'], defaults=rd)
        self.stdout.write(self.style.SUCCESS('Reviews seeded'))

        flat_type = FlatType.objects.first()
        BuildingFlat.objects.all().delete()
        for cluster in ['A', 'B', 'C', 'D', 'E', 'F']:
            for floor in range(0, 3):
                for unit in range(1, 4):
                    flat_num = f"{cluster}{floor}{unit:02d}"
                    BuildingFlat.objects.create(
                        tower=cluster, flat_number=flat_num,
                        floor=floor, flat_type=flat_type, status='available'
                    )
        self.stdout.write(self.style.SUCCESS('Building flats seeded'))
        self.stdout.write(self.style.SUCCESS('All data seeded successfully!'))
