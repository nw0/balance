import datetime

from django import forms
from django.utils.safestring import mark_safe

from balance.models import Entry


class BSDateInput(forms.TextInput):
    def render(self, name, value, attrs=None, choices=()):
        output = ['<div class="input-group date datepicker">',
                  super(BSDateInput, self).render(name, value, attrs),
                  '<span class="input-group-addon">',
                  '<i class="glyphicon glyphicon-calendar"></i></span></div>']
        return mark_safe('\n'.join(output))


class EntryForm(forms.ModelForm):
    date = forms.DateField(label="Date", initial=datetime.date.today, widget=BSDateInput())

    class Meta:
        model = Entry
        exclude = []
