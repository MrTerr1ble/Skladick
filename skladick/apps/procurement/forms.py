from django import forms
from .models import PurchaseRequest

INPUT = {"class": "input"}
SELECT = {"class": "input"}
TEXTAREA = {"class": "textarea"}
FILE = {"class": "file"}


class PurchaseRequestForm(forms.ModelForm):
    """Форма создания и редактирования заявок на закупку."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "supplier" in self.fields:
            self.fields["supplier"].empty_label = "—"

    class Meta:
        model = PurchaseRequest
        fields = [
            "number",
            "item",
            "qty",
            "uom",
            "warehouse",
            "supplier",
            "comment",
            "attachment",
        ]
        widgets = {
            "number": forms.TextInput(attrs=INPUT),
            "item": forms.Select(attrs=SELECT),
            "qty": forms.NumberInput(attrs={**INPUT, "step": "0.001"}),
            "uom": forms.Select(attrs=SELECT),
            "warehouse": forms.Select(attrs=SELECT),
            "supplier": forms.Select(attrs=SELECT),
            "comment": forms.Textarea(attrs={**TEXTAREA, "rows": 4}),
            "attachment": forms.ClearableFileInput(attrs=FILE),
        }
