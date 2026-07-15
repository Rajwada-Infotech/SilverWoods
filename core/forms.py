from django import forms
from .models import Lead, PopupAd, FlatType, Review


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
