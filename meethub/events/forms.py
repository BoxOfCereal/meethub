from django import forms

from meethub.events.models import Event, Category


class EventForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    time = forms.TimeField(
        input_formats=['%I:%M %p', '%H:%M'],  # Acepta '02:30 PM' y '14:30'
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'datetimepicker2',
            'data-td-target': '#datetimepicker2'
        })
    )

    date = forms.DateField(
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],  # Ajusta según el formato de tu widget
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'datetimepicker1',
            'data-td-target': '#datetimepicker1'
        })
    )

    latitude = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Latitude (e.g., 40.7128)',
            'id': 'latitude-field',
            'step': 'any'
        })
    )

    longitude = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Longitude (e.g., -74.0060)',
            'id': 'longitude-field',
            'step': 'any'
        })
    )

    class Meta:
        model = Event
        fields = ('category', 'name', 'details', 'venue', 'time', 'date', 'latitude', 'longitude',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
        }

