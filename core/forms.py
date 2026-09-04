from django import forms
from .models import Lead, PopupAd, FlatType, Review, Amenity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'flat_preference', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your Phone', 'class': 'form-input'}),
            'flat_preference': forms.Select(attrs={'class': 'form-input'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 4, 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        choices = [('', 'Select Flat Type')] + [(f'{ft.bhk} BHK', f'{ft.bhk} BHK - {ft.name}') for ft in FlatType.objects.all()]
        self.fields['flat_preference'].widget = forms.Select(choices=choices, attrs={'class': 'form-input'})


class PopupAdForm(forms.ModelForm):
    class Meta:
        model = PopupAd
        fields = ['title', 'image', 'description', 'flat_type', 'link', 'is_active', 'is_external', 'project_logo', 'start_date', 'end_date']


class FlatTypeForm(forms.ModelForm):
    class Meta:
        model = FlatType
        fields = ['name', 'bhk', 'carpet_area', 'buildup_area', 'terrace_area', 'super_buildup_area', 'price', 'price_per_sqft', 'description', 'is_available', 'order']


class AmenityForm(forms.ModelForm):
    ICON_CHOICES = [
        ('pool', 'Swimming Pool'),
        ('fitness', 'Gym / Fitness'),
        ('child', 'Kids / Play Area'),
        ('club', 'Clubhouse / Banquet'),
        ('garden', 'Garden / Greenery'),
        ('security', 'Security / Gate'),
        ('power', 'Power Backup'),
        ('parking', 'Parking'),
        ('sports', 'Sports'),
        ('banquet', 'Banquet / Dining'),
        ('star', 'Other'),
    ]

    class Meta:
        model = Amenity
        fields = ['name', 'icon', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Infinity Pool', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Brief description...', 'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(choices=self.ICON_CHOICES, attrs={'class': 'form-input'})


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment', 'designation']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-input'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Your Review', 'rows': 3, 'class': 'form-input'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Your Designation (Optional)', 'class': 'form-input'}),
        }
