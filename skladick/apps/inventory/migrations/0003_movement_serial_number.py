from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="movement",
            name="serial_number",
            field=models.CharField(blank=True, default="", max_length=64, verbose_name="Серийный номер"),
            preserve_default=False,
        ),
    ]
