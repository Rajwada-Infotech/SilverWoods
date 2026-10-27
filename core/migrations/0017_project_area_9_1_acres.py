import re

from django.db import migrations

ACRES = re.compile(r'8\.1(\s*)(acre)', re.I)


def fix(text):
    return ACRES.sub(lambda m: '9.1' + m.group(1) + m.group(2), text or '')


def forwards(apps, schema_editor):
    ProjectInfo = apps.get_model('core', 'ProjectInfo')
    for p in ProjectInfo.objects.all():
        p.project_area = fix(p.project_area)
        p.description = fix(p.description)
        p.save(update_fields=['project_area', 'description'])
    PageContent = apps.get_model('core', 'PageContent')
    for c in PageContent.objects.filter(value__icontains='8.1'):
        c.value = fix(c.value)
        c.save(update_fields=['value'])
    ChatbotQA = apps.get_model('core', 'ChatbotQA')
    for q in ChatbotQA.objects.filter(answer__icontains='8.1'):
        q.answer = fix(q.answer)
        q.keywords = q.keywords.replace('project area,8.1,', 'project area,9.1,')
        q.save(update_fields=['answer', 'keywords'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_seed_site_content'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
