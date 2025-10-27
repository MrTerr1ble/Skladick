from django import forms

from .models import PurchaseRequest


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
            "number": forms.TextInput(attrs={"class": "form-control"}),
            "item": forms.Select(attrs={"class": "form-select"}),
            "qty": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "uom": forms.Select(attrs={"class": "form-select"}),
            "warehouse": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

