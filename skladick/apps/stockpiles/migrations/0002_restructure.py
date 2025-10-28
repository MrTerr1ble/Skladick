from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stockpiles", "0001_initial"),
        ("catalog", "0001_initial"),
        ("warehouses", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(name="StockpileAlert"),
        migrations.DeleteModel(name="StockpileThreshold"),
        migrations.DeleteModel(name="Stockpile"),
        migrations.CreateModel(
            name="Stockpile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50)),
                ("name", models.CharField(max_length=255)),
                ("warehouse", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="warehouses.warehouse")),
                ("location", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to="warehouses.location")),
            ],
            options={
                "verbose_name": "Стокпайл",
                "verbose_name_plural": "Стокпайлы",
                "ordering": ["warehouse__name", "code"],
                "unique_together": {("warehouse", "code")},
            },
        ),
        migrations.CreateModel(
            name="StockpileInventory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("qty_on_ground", models.DecimalField(decimal_places=3, default=0, max_digits=14)),
                ("item", models.ForeignKey(limit_choices_to={"kind": "ORE"}, on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
                ("stockpile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="stockpiles.stockpile")),
                ("uom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.uom")),
            ],
            options={
                "verbose_name": "Остаток стокпайла",
                "verbose_name_plural": "Остатки стокпайлов",
                "unique_together": {("stockpile", "item")},
            },
        ),
        migrations.CreateModel(
            name="StockpileMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("movement_type", models.CharField(choices=[("RECEIPT", "Приход"), ("ISSUE", "Расход"), ("TRANSFER", "Перемещение")], max_length=16)),
                ("qty", models.DecimalField(decimal_places=3, max_digits=14)),
                ("occurred_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.TextField(blank=True)),
                ("actor", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("from_stockpile", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movements_out", to="stockpiles.stockpile")),
                ("item", models.ForeignKey(limit_choices_to={"kind": "ORE"}, on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
                ("to_stockpile", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movements_in", to="stockpiles.stockpile")),
                ("uom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.uom")),
            ],
            options={
                "verbose_name": "Движение стокпайла",
                "verbose_name_plural": "Движения стокпайлов",
                "ordering": ["-occurred_at"],
            },
        ),
        migrations.CreateModel(
            name="StockpileThreshold",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("min_qty", models.DecimalField(blank=True, decimal_places=3, max_digits=14, null=True)),
                ("max_qty", models.DecimalField(blank=True, decimal_places=3, max_digits=14, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("item", models.ForeignKey(limit_choices_to={"kind": "ORE"}, on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
                ("stockpile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="stockpiles.stockpile")),
                ("uom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.uom")),
            ],
            options={
                "verbose_name": "Порог стокпайла",
                "verbose_name_plural": "Пороги стокпайлов",
                "unique_together": {("stockpile", "item")},
            },
        ),
        migrations.CreateModel(
            name="StockpileAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("current_qty", models.DecimalField(decimal_places=3, max_digits=14)),
                (
                    "state",
                    models.CharField(
                        choices=[("OPEN", "Открыт"), ("ACK", "Принят"), ("CLOSED", "Закрыт")],
                        default="OPEN",
                        max_length=10,
                    ),
                ),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("item", models.ForeignKey(limit_choices_to={"kind": "ORE"}, on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
                ("stockpile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="stockpiles.stockpile")),
                ("uom", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.uom")),
            ],
            options={
                "verbose_name": "Алерт стокпайла",
                "verbose_name_plural": "Алерты стокпайлов",
                "ordering": ["-created_at"],
            },
        ),
    ]
