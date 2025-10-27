from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="kind",
            field=models.CharField(
                choices=[
                    ("ORE", "Руды"),
                    ("TOOL", "Инструменты"),
                    ("EQUIPMENT", "Оборудование"),
                    ("CONSUMABLE", "Расходники"),
                ],
                db_index=True,
                default="TOOL",
                max_length=16,
                verbose_name="Тип",
            ),
            preserve_default=False,
        ),
    ]
