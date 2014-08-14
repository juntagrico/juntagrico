# -*- coding: utf-8 -*-
from django.db.models.fields import DecimalField
from django.forms import CharField, PasswordInput, Form, ValidationError, ModelForm, Select, TextInput, ChoiceField, CheckboxInput
from my_ortoloco.models import Loco, User


class PasswordForm(Form):
    password = CharField(label='Passwort', min_length=4, widget=PasswordInput())
    passwordRepeat = CharField(label='Passwort (wiederholen)', min_length=4, widget=PasswordInput())

    def clean_passwordRepeat(self):
        if self.data['password'] != self.data['passwordRepeat']:
            raise ValidationError('Passwörter stimmen nicht überein')
        return self.data['passwordRepeat']


class ProfileLocoForm(ModelForm):
    class Meta:
        model = Loco
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone']
        widgets = {
            'first_name': TextInput(attrs={'placeholder': 'Berta'}),
            'last_name': TextInput(attrs={'placeholder': 'Muster'}),
            'addr_street': TextInput(attrs={'placeholder': 'Zürcherstrasse 123'}),
            'addr_zipcode': TextInput(attrs={'placeholder': '8000', 'class': 'span2'}),
            'addr_location': TextInput(attrs={'placeholder': 'Zürich'}),
            'birthday': TextInput(attrs={'placeholder': '01.12.1956'}),
            'phone': TextInput(attrs={'placeholder': '044 123 45 67'}),
            'mobile_phone': TextInput(attrs={'placeholder': '076 123 45 67'}),
            'email': TextInput(attrs={'placeholder': 'beate@muster.ch'}),
        }


class AboForm(Form):
    anteilscheine = CharField(label='asdf', min_length=1)
    anteilscheine_added = DecimalField(max_digits=2, decimal_places=0)
    small_abos = DecimalField(max_digits=2, decimal_places=0)
    big_abos = DecimalField(max_digits=2, decimal_places=0)
    house_abos = DecimalField(max_digits=2, decimal_places=0)
    depot = CharField(widget=Select)



class RegisterLocoForm(ModelForm):
    class Meta:
        model = Loco
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone']
        widgets = {
            'first_name': TextInput(attrs={'placeholder': 'Berta'}),
            'last_name': TextInput(attrs={'placeholder': 'Muster'}),
            'addr_street': TextInput(attrs={'placeholder': 'Zürcherstrasse 123'}),
            'addr_zipcode': TextInput(attrs={'placeholder': '8000', 'class': 'span2'}),
            'addr_location': TextInput(attrs={'placeholder': 'Zürich'}),
            'birthday': TextInput(attrs={'placeholder': '01.12.1956'}),
            'phone': TextInput(attrs={'placeholder': '044 123 45 67'}),
            'mobile_phone': TextInput(attrs={'placeholder': '076 123 45 67'}),
            'email': TextInput(attrs={'placeholder': 'beate@muster.ch'})
        }