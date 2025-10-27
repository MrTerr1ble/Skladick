from decimal import Decimal

from django import forms

from apps.catalog.models import Item

from .models import Movement

INPUT = {"class": "input"}
SELECT = {"class": "input"}
TEXT = {"class": "textarea"}


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = [
            "type", "occurred_at", "item", "qty", "uom",
            "serial_number", "from_location", "to_location", "note"
        ]
        widgets = {
            "type": forms.Select(attrs=SELECT),
            "occurred_at": forms.DateTimeInput(attrs={**INPUT, "type": "datetime-local"}),
            "item": forms.Select(attrs=SELECT),
            "qty": forms.NumberInput(attrs={**INPUT, "step": "0.001"}),
            "uom": forms.Select(attrs=SELECT),
            "serial_number": forms.TextInput(attrs={**INPUT, "placeholder": "Серийный номер"}),
            "from_location": forms.Select(attrs=SELECT),
            "to_location": forms.Select(attrs=SELECT),
            "note": forms.Textarea(attrs={**TEXT, "rows": 3}),
        }

    def clean(self):
        data = super().clean()
        mtype = data.get("type")
        frm = data.get("from_location")
        to = data.get("to_location")
        item = data.get("item")
        qty = data.get("qty")
        serial = data.get("serial_number") or ""
        serial = serial.strip()
        if serial:
            data["serial_number"] = serial

        # Валидируем сценарии
        if mtype == Movement.TRANSFER and (not frm or not to):
            raise forms.ValidationError("Для перемещения укажи и откуда, и куда.")
        if mtype == Movement.ISSUE and not frm:
            raise forms.ValidationError("Для списания укажи локацию-источник.")
        if mtype == Movement.RECEIPT and not to:
            raise forms.ValidationError("Для прихода укажи локацию-приёмник.")
        if frm and to and frm == to:
            raise forms.ValidationError("Локации 'откуда' и 'куда' не могут совпадать.")

        if item and qty is not None:
            kind = item.kind
            if kind in (Item.TOOL, Item.CONSUMABLE):
                if qty != qty.quantize(Decimal("1")):
                    raise forms.ValidationError("Для выбранной номенклатуры укажи целое количество.")
            elif kind == Item.EQUIPMENT:
                if qty != Decimal("1"):
                    raise forms.ValidationError("Для оборудования количество должно быть равно 1.")
                if not serial:
                    raise forms.ValidationError("Для оборудования укажи серийный номер.")
            elif kind == Item.ORE:
                # допускаем дробные значения, дополнительных проверок не требуется
                pass

        if serial and item and item.kind != Item.EQUIPMENT:
            raise forms.ValidationError("Серийный номер указывается только для оборудования.")
        return data
