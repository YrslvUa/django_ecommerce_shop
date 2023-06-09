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
        fields = ['first_name', 'last_name', 'email', 'city', 'house', 'apartment']

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


# class PromoCodeForm(forms.ModelForm):
#     class Meta:
#         model = PromoCode
#         fields = ['promo_code', ]
