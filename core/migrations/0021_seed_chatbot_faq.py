import json
from pathlib import Path

from django.db import migrations

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures' / 'initial_data.json'


def seed(apps, schema_editor):
    """Load the default chatbot Q&A only into an empty table (never overwrites admin edits)."""
    ChatbotQA = apps.get_model('core', 'ChatbotQA')
    if ChatbotQA.objects.exists() or not FIXTURE.exists():
        return
    rows = [o['fields'] for o in json.loads(FIXTURE.read_text(encoding='utf-8')) if o.get('model') == 'core.chatbotqa']
    ChatbotQA.objects.bulk_create([
        ChatbotQA(question=f['question'], answer=f['answer'], keywords=f['keywords'],
                  is_active=f.get('is_active', True), order=f.get('order', 0))
        for f in rows
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_amenity_static_images'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
