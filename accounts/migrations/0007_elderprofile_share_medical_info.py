from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_onboarding_completed"),
    ]

    operations = [
        migrations.AddField(
            model_name="elderprofile",
            name="share_medical_info",
            field=models.BooleanField(
                default=False,
                verbose_name="compartilhar ficha médica no perfil público",
            ),
        ),
    ]
