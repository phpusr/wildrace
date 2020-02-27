from django import forms

from app.models import StatLog


class StatForm(forms.Form):
    start_range = forms.IntegerField(required=False)
    end_range = forms.IntegerField(required=False)
    type = forms.ChoiceField(choices=[
        ('distance', 'Distance'),
        ('date', 'Date')
    ])

    @property
    def stat_type(self):
        if self.cleaned_data['type'] == 'distance':
            return StatLog.StatType.DISTANCE
        elif self.cleaned_data['type'] == 'date':
            return StatLog.StatType.DATE
