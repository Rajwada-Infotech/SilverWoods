from django.db import migrations

# Images the homepage used to pick by icon before amenity images were uploadable
ICON_IMAGES = {
    'pool': 'images/amenities/Infinity_Pool.webp',
    'fitness': 'images/amenities/Gym.webp',
    'child': 'images/amenities/Kids.webp',
    'club': 'images/amenities/Clubhouse.webp',
    'garden': 'images/amenities/Personal_Pool.webp',
    'security': 'images/amenities/Gate.webp',
    'banquet': 'images/amenities/Banquet.webp',
    'sports': 'images/amenities/Sports.webp',
}


def forwards(apps, schema_editor):
    Amenity = apps.get_model('core', 'Amenity')
    for a in Amenity.objects.filter(static_path='', image=''):
        a.static_path = ICON_IMAGES.get(a.icon, 'images/amenities/Clubhouse.webp')
        a.save(update_fields=['static_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_amenity_image'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
