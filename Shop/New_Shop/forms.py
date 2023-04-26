from django import forms
from New_Shop.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'description',
            'url',
            'category',
            'product_img',
            'stock',
            'available'
        ]


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = SubscribedUser
        fields = ('email', 'name')


class AddressForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'product', 'first_name', 'last_name', 'email', 'city', 'house', 'apartment']
        widgets = {
            'customer': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'house': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row g-3'
        self.helper.label_class = 'col-sm-6'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group'),
                Column('last_name', css_class='form-group'),
                css_class='form-row'
            ),
            'email',
            'city',
            Row(
                Column('house', css_class='form-group col-md-3'),
                Column('apartment', css_class='form-group col-md-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Submit', css_class='btn btn-primary'))


class PromoCodeForm(forms.Form):
    promo_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'name': 'promo_code'}))
