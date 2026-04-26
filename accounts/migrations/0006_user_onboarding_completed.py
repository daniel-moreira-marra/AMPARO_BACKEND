from django.db import migrations, models


def mark_existing_users_onboarded(apps, schema_editor):
    """Existing users already went through onboarding implicitly — don't block them."""
    User = apps.get_model("accounts", "User")
    User.objects.all().update(onboarding_completed=True)


class Migration(migrations.Migration):
    dependencies = [("accounts", "0005_user_show_links")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="onboarding_completed",
            field=models.BooleanField(default=False, verbose_name="onboarding completo"),
        ),
        migrations.RunPython(
            mark_existing_users_onboarded,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
