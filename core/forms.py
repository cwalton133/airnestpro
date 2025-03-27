from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from core.models import Property, Booking, PropertyReview 
from tinymce.widgets import TinyMCE


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']


# class UserProfileForm(forms.ModelForm):
#     """ A form to enable users to update their profiles. """
#
#     class Meta:
#         model = UserProfile
#         fields = ['bio', 'phone', 'location']  # Adjust fields based on your UserProfile model


# class PropertyForm(forms.ModelForm):
#     class Meta:
#         model = Property
#         fields = [
#             'realtor',
#             'category',
#             'title',
#             'image',
#             'description',
#             'price_per_night',
#             'max_guests',
#             'num_bedrooms',
#             'num_bathrooms',
#             'location',
#             'available',
#             'featured',
#             'tags'
#         ]
#         widgets = {
#             'tags': forms.CheckboxSelectMultiple()  
#         }

#     def __init__(self, *args, **kwargs):
#         super(PropertyForm, self).__init__(*args, **kwargs)

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'realtor',
            'category',
            'title',
            'image',
            'description',
            'price_per_night',
            'max_guests',
            'num_bedrooms',
            'num_bathrooms',
            'location',
            'available',
            'featured',
            'tags'
        ]
        widgets = {
            'description': TinyMCE(),  
            'tags': forms.CheckboxSelectMultiple()  
        }

    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)


class PropertyAdminForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'
        widgets = {
            'description': TinyMCE(),  
        }
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'user',               
            'property',           
            'check_in_date',      
            'check_out_date',     
            'guests',             
            'total_price',        
            'status',             
        ]
        widgets = {
            'check_in_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'total_price': forms.NumberInput(attrs={'step': "0.01"}),  
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get("check_in_date")
        check_out_date = cleaned_data.get("check_out_date")

        if check_in_date and check_out_date and check_in_date >= check_out_date:
            raise forms.ValidationError("Check-out date must be after check-in date.")

        return cleaned_data


class PropertyReviewForm(forms.ModelForm):

    class Meta:
        model = PropertyReview
        fields = ['property', 'rating', 'comment']  
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)],
                               widget=forms.RadioSelect)

