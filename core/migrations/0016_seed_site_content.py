from django.db import migrations

FEATURES = [
    ("fa-home", "Independent G+2 Design", "Each villa is designed for maximum space, light, and ventilation with independent access and premium privacy."),
    ("fa-ruler-combined", "{area_range} Buildup Area", "6 villa types to choose from — generous living spaces across 3 floors with 4 bedrooms each."),
    ("fa-swimming-pool", "Private Garden & Plunge Pool", "Every home includes a private backyard garden and a personal plunge pool for your exclusive enjoyment."),
    ("fa-expand-arrows-alt", "9.1 Acres · 121 Premium Villas", "Sprawling gated community nestled amidst lush greenery, just 2.9 km from Southern Bypass."),
]

LANDMARKS = [
    ("fa-hospital", "Ruby Hospital", "14 km"),
    ("fa-subway", "Kavi Nazrul Metro", "8.1 km"),
    ("fa-subway", "Shahid Khudiram Metro", "7.4 km"),
    ("fa-road", "Dhalai Bridge", "7 km"),
    ("fa-map-marker-alt", "Patuli", "8.6 km"),
    ("fa-train", "Sonarpur Station", "9 km"),
    ("fa-map-pin", "Kamalgazi More", "6 km"),
    ("fa-school", "BDMI School", "6.5 km"),
    ("fa-gas-pump", "Narendrapur Petrol Pump", "5.3 km"),
    ("fa-shopping-bag", "Woodsquare Mall", "5.1 km"),
    ("fa-om", "RKM Ashram", "5 km"),
    ("fa-car", "Southern Bypass", "3 km"),
]


def seed(apps, schema_editor):
    GalleryImage = apps.get_model('core', 'GalleryImage')
    BrochureImage = apps.get_model('core', 'BrochureImage')
    VillaFeature = apps.get_model('core', 'VillaFeature')
    Landmark = apps.get_model('core', 'Landmark')

    if not GalleryImage.objects.exists():
        for i in range(1, 7):
            GalleryImage.objects.create(static_path=f'images/gallery{i}.webp', caption='Silverwoods Gallery', order=i)
    if not BrochureImage.objects.exists():
        for i in range(1, 26):
            BrochureImage.objects.create(static_path=f'brochure/{i}.webp', order=i)
    if not VillaFeature.objects.exists():
        for i, (icon, title, desc) in enumerate(FEATURES, 1):
            VillaFeature.objects.create(icon=icon, title=title, description=desc, order=i)
    if not Landmark.objects.exists():
        for i, (icon, name, dist) in enumerate(LANDMARKS, 1):
            Landmark.objects.create(icon=icon, name=name, distance=dist, order=i)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_site_content'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
