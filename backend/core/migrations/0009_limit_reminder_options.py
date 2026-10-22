from django.db import migrations, models
from django.db.models import Min


def limit_existing_reminders(apps, schema_editor):
    Subscription = apps.get_model('core', 'UserSessionSubscription')
    database = schema_editor.connection.alias

    Subscription.objects.using(database).exclude(
        reminder_time__in=[120, 60, 30]
    ).delete()

    subscriptions = Subscription.objects.using(database)
    groups = subscriptions.values(
        'user_id',
        'session_type',
    ).annotate(
        reminder_to_keep=Min('reminder_time')
    )

    for group in groups.iterator():
        subscriptions.filter(
            user_id=group['user_id'],
            session_type=group['session_type'],
            reminder_time__gt=group['reminder_to_keep'],
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_driver_flag_driver_is_primary_alter_driver_code_and_more'),
    ]

    operations = [
        migrations.RunPython(limit_existing_reminders, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usersessionsubscription',
            name='reminder_time',
            field=models.PositiveIntegerField(
                choices=[
                    (120, '120 минут'),
                    (60, '60 минут'),
                    (30, '30 минут'),
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name='usersessionsubscription',
            unique_together={('user', 'session_type')},
        ),
    ]
