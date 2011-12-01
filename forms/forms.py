from django import forms

class GeneralForm(forms.ModelForm):
    """
    Form to use when you dont know what class you're dealing with, and don't
    care
    """
    class Meta:
        pass

