from django.db import migrations, models


def copy_institution_address(apps, schema_editor):
    InstitutionProfile = apps.get_model("accounts", "InstitutionProfile")
    User = apps.get_model("accounts", "User")

    for profile in InstitutionProfile.objects.select_related("user").all():
        user = profile.user
        update_fields = []
        for field in ("address_line", "city", "state", "zip_code"):
            profile_value = getattr(profile, field, "")
            user_value = getattr(user, field, "")
            if not user_value and profile_value:
                setattr(user, field, profile_value)
                update_fields.append(field)
        if update_fields:
            user.save(update_fields=update_fields)


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_alter_elderprofile_caregivers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address_line",
            field=models.CharField(blank=True, max_length=255, verbose_name="endereço"),
        ),
        migrations.AddField(
            model_name="user",
            name="city",
            field=models.CharField(blank=True, max_length=120, verbose_name="cidade"),
        ),
        migrations.AddField(
            model_name="user",
            name="state",
            field=models.CharField(blank=True, max_length=2, verbose_name="estado"),
        ),
        migrations.AddField(
            model_name="user",
            name="zip_code",
            field=models.CharField(blank=True, max_length=8, verbose_name="CEP"),
        ),
        migrations.RunPython(copy_institution_address, noop),
        migrations.RemoveField(
            model_name="institutionprofile",
            name="address_line",
        ),
        migrations.RemoveField(
            model_name="institutionprofile",
            name="city",
        ),
        migrations.RemoveField(
            model_name="institutionprofile",
            name="state",
        ),
        migrations.RemoveField(
            model_name="institutionprofile",
            name="zip_code",
        ),
    ]
