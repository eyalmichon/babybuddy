"""Create a 'default' permission group with all core model permissions.

New non-read-only users are assigned to this group instead of being granted
``is_superuser``.  Existing users are not modified.
"""

from django.db import migrations

CORE_MODELS = [
    "bmi",
    "child",
    "diaperchange",
    "expirable",
    "feeding",
    "headcircumference",
    "height",
    "medication",
    "medicationschedule",
    "note",
    "pumping",
    "sleep",
    "tag",
    "tagged",
    "temperature",
    "timer",
    "tummytime",
    "weight",
]

ACTIONS = ["view", "add", "change", "delete"]

GROUP_NAME = "default"


def create_default_group(apps, schema_editor):
    from django.apps import apps as real_apps
    from django.contrib.auth.management import create_permissions

    for app_config in real_apps.get_app_configs():
        create_permissions(app_config, verbosity=0)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    codenames = []
    for model in CORE_MODELS:
        for action in ACTIONS:
            codenames.append(f"{action}_{model}")

    perms = Permission.objects.filter(
        content_type__app_label="core",
        codename__in=codenames,
    )
    group.permissions.set(perms)


def remove_default_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("babybuddy", "0036_settings_force_password_change"),
        ("core", "0038_expirable"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_default_group, remove_default_group),
    ]
