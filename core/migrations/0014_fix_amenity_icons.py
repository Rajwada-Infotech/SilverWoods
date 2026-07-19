from django.db import migrations


def fix_amenity_icons(apps, schema_editor):
    Amenity = apps.get_model('core', 'Amenity')
    Amenity.objects.filter(name='Sports Arena').update(icon='sports')
    Amenity.objects.filter(name='Guest Rooms & Banquet').update(icon='banquet')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_chatbotqa'),
    ]

    operations = [
        migrations.RunPython(fix_amenity_icons, migrations.RunPython.noop),
    ]
