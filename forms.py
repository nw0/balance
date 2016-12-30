from django import forms

from balance.models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = []