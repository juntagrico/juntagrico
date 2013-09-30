# -*- coding: utf-8 -*-
from django.forms import CharField, PasswordInput, Form, ValidationError


class PasswordForm(Form):
    password = CharField(label='Passwort', min_length=4, widget=PasswordInput())
    passwordRepeat = CharField(label='Passwort (wiederholen)', min_length=4, widget=PasswordInput())

    def clean_passwordRepeat(self):
        if self.data['password'] != self.data['passwordRepeat']:
            raise ValidationError('Passwörter stimmen nicht überein')
        return self.data['passwordRepeat']


class ProfileForm(Form):
    password = CharField(label='Passwort', min_length=4, widget=PasswordInput())
    passwordRepeat = CharField(label='Passwort (wiederholen)', min_length=4, widget=PasswordInput())

    def clean_passwordRepeat(self):
        if self.data['password'] != self.data['passwordRepeat']:
            raise ValidationError('Passwörter stimmen nicht überein')
        return self.data['passwordRepeat']