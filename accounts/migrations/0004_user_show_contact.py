from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="show_email",
            field=models.BooleanField(default=False, verbose_name="compartilhar e-mail"),
        ),
        migrations.AddField(
            model_name="user",
            name="show_phone",
            field=models.BooleanField(default=False, verbose_name="compartilhar telefone"),
        ),
    ]
