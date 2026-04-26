from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0004_user_show_contact")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="show_links",
            field=models.BooleanField(default=True, verbose_name="compartilhar vínculos"),
        ),
    ]
