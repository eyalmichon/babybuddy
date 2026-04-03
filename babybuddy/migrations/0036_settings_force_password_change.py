from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("babybuddy", "0035_alter_settings_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="force_password_change",
            field=models.BooleanField(
                default=False,
                editable=False,
                verbose_name="Force password change",
            ),
        ),
    ]
