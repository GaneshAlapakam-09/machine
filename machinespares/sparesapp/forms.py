
from django import forms
from .models import spare_details

class SpareForm(forms.ModelForm):
    class Meta:
        model = spare_details  # Link to your model
        fields = ['specification_I','specification_II','specification_III','specification_IV','minimum_stock_quantity']  # List the fields you want to include in the form
        widgets = {
            
            'specification_I': forms.TextInput(attrs={'class': 'form-control'}),
            'specification_II': forms.TextInput(attrs={'class': 'form-control'}),
            'specification_III': forms.TextInput(attrs={'class': 'form-control'}),
            'specification_IV': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }