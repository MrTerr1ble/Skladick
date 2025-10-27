from django import forms
from .models import OreReceipt

INPUT = {"class": "input"}
SELECT = {"class": "input"}
TEXTAREA = {"class": "textarea"}
FILE = {"class": "file"}


class OreReceiptForm(forms.ModelForm):
    class Meta:
        model = OreReceipt
        fields = ["location", "item", "quantity", "contract", "note", "file"]
        widgets = {
            "location": forms.Select(attrs=SELECT),
            "item": forms.Select(attrs=SELECT),
            "quantity": forms.NumberInput(attrs={**INPUT, "step": "0.001", "id": "f_quantity"}),
            "contract": forms.TextInput(attrs={**INPUT, "placeholder": "№ договора/накладной", "id": "f_contract"}),
            "note": forms.Textarea(attrs={**TEXTAREA, "rows": 4, "id": "f_note"}),
            "file": forms.ClearableFileInput(attrs={**FILE, "id": "f_file"}),
        }
