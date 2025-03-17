from django import forms
from .models import Profile, User, Ingredient, BurgerReview


class ProfileUpdateForm(forms.ModelForm):
    '''
    Form to update user profile information.

    Allows users to update their profile picture and phone number.
    '''
    class Meta:
        model = Profile
        fields = ('picture', 'phone')

class UserUpdateForm(forms.ModelForm):
    '''
    Form to update user account information.

    Allows users to update their email address.
    '''
    class Meta:
        model = User
        fields = ('email',)

class BurgerReviewForm(forms.ModelForm):
    '''
    Form for submitting a burger review.
    '''
    class Meta:
        model = BurgerReview
        fields = ('user', 'burger', 'content', 'rating')
        widgets = {
            'burger': forms.HiddenInput(),
            'user': forms.HiddenInput(),

        }


class CustomBurgerForm(forms.Form):
    '''
    Form for creating a custom burger.

    Allows users to name their burger, select a bun, and choose multiple ingredients.
    '''
    name = forms.CharField(max_length=50, label='Burger Name')

    bun = forms.ModelChoiceField(
        queryset=Ingredient.objects.filter(category='Bun'),
        widget=forms.RadioSelect,
        required=True,
        label='Choose Your Bun'
    )

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.exclude(category='Bun'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Choose Your Ingredients'
    )
