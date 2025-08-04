from django import forms
from .models import CentreInteret
from django.core.validators import MinValueValidator, MaxValueValidator

class CentreInteretForm(forms.ModelForm):
    # Ajout de champs personnalisés pour une meilleure validation
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        validators=[
            MinValueValidator(-90, message="La latitude doit être entre -90 et 90"),
            MaxValueValidator(90, message="La latitude doit être entre -90 et 90")
        ],
        required=True
    )
    
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        validators=[
            MinValueValidator(-180, message="La longitude doit être entre -180 et 180"),
            MaxValueValidator(180, message="La longitude doit être entre -180 et 180")
        ],
        required=True
    )

    class Meta:
        model = CentreInteret
        fields = ['nom', 'type', 'quartier', 'description', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Description détaillée du centre...'
            }),
            'nom': forms.TextInput(attrs={
                'placeholder': 'Nom du centre'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quartier': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nom': 'Nom du centre',
            'type': 'Type de centre',
            'quartier': 'Quartier',
            'description': 'Description'
        }
        help_texts = {
            'latitude': 'Cliquez sur la carte pour définir la position',
            'longitude': 'Cliquez sur la carte pour définir la position'
        }

    def __init__(self, *args, **kwargs):
        commune = kwargs.pop('commune', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les quartiers par commune si elle est fournie
        if commune:
            self.fields['quartier'].queryset = commune.quartiers.all()
        
        # Ajouter des classes CSS aux champs
        for field in self.fields:
            if field not in ['latitude', 'longitude']:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Validation supplémentaire des coordonnées
        if latitude and longitude:
            if not (-90 <= latitude <= 90):
                self.add_error('latitude', "La latitude doit être entre -90 et 90")
            if not (-180 <= longitude <= 180):
                self.add_error('longitude', "La longitude doit être entre -180 et 180")
        
        return cleaned_data