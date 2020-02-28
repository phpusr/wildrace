from app.models import StatLog
from django import forms


class PostForm(forms.Form):
    me = forms.ChoiceField(required=False, choices=(
        ('true', 'True'),
        ('false', 'False')
    ))
    status = forms.IntegerField(required=False, min_value=1, max_value=4)


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
