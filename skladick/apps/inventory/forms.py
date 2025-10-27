from django import forms
from .models import Movement

INPUT = {"class": "input"}
SELECT = {"class": "input"}
TEXT = {"class": "textarea"}


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = [
            "type", "occurred_at", "item", "qty", "uom",
            "from_location", "to_location", "note"
        ]
        widgets = {
            "type": forms.Select(attrs=SELECT),
            "occurred_at": forms.DateTimeInput(attrs={**INPUT, "type": "datetime-local"}),
            "item": forms.Select(attrs=SELECT),
            "qty": forms.NumberInput(attrs={**INPUT, "step": "0.001"}),
            "uom": forms.Select(attrs=SELECT),
            "from_location": forms.Select(attrs=SELECT),
            "to_location": forms.Select(attrs=SELECT),
            "note": forms.Textarea(attrs={**TEXT, "rows": 3}),
        }

    def clean(self):
        data = super().clean()
        mtype = data.get("type")
        frm = data.get("from_location")
        to = data.get("to_location")

        # Валидируем сценарии
        if mtype == Movement.TRANSFER and (not frm or not to):
            raise forms.ValidationError("Для перемещения укажи и откуда, и куда.")
        if mtype == Movement.ISSUE and not frm:
            raise forms.ValidationError("Для списания укажи локацию-источник.")
        if mtype == Movement.RECEIPT and not to:
            raise forms.ValidationError("Для прихода укажи локацию-приёмник.")
        if frm and to and frm == to:
            raise forms.ValidationError("Локации 'откуда' и 'куда' не могут совпадать.")
        return data
