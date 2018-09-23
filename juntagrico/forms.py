# -*- coding: utf-8 -*-
from django.forms import CharField, PasswordInput, Form, ValidationError, ModelForm, TextInput, CheckboxInput, DateInput

from schwifty import IBAN

from juntagrico.models import Member, Subscription


class PasswordForm(Form):
    password = CharField(label='Passwort', min_length=4,
                         widget=PasswordInput())
    passwordRepeat = CharField(
        label='Passwort (wiederholen)', min_length=4, widget=PasswordInput())

    def clean_password_repeat(self):
        if self.data['password'] != self.data['passwordRepeat']:
            raise ValidationError('Passwörter stimmen nicht überein')
        return self.data['passwordRepeat']


class MemberProfileForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone', 'iban', 'reachable_by_email']
        widgets = {
            'first_name': TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'last_name': TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'addr_street': TextInput(attrs={'class': 'form-control'}),
            'addr_zipcode': TextInput(attrs={'class': 'form-control'}),
            'addr_location': TextInput(attrs={'class': 'form-control'}),
            'birthday': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'iban': TextInput(attrs={'class': 'form-control'}),
            'reachable_by_email': CheckboxInput(attrs={'class': 'slider'}),
        }

    def clean_iban(self):
        if self.data['iban'] != '':
            try:
                iban = IBAN(self.data['iban'])
            except:
                raise ValidationError('IBAN ist nicht gültig')
        return self.data['iban']


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['start_date']
        widgets = {
            'start_date': DateInput(attrs={'format': '%d.%m.%y', 'class': 'form-control'}),
        }


class RegisterMemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'addr_street': TextInput(attrs={'class': 'form-control'}),
            'addr_zipcode': TextInput(attrs={'class': 'form-control'}),
            'addr_location': TextInput(attrs={'class': 'form-control'}),
            'birthday': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'})
        }
