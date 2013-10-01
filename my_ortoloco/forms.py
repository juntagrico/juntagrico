# -*- coding: utf-8 -*-
from django.db.models.fields import DecimalField
from django.forms import CharField, PasswordInput, Form, ValidationError, ModelForm, Select
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
        fields = ['addr_street', 'addr_zipcode', 'addr_location', 'birthday', 'phone', 'mobile_phone']


class ProfileUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AboForm(Form):
    anteilsscheine = DecimalField(max_digits=2,decimal_places=0)
    anteilsscheine_added = DecimalField(max_digits=2,decimal_places=0)
    kleine_abos = DecimalField(max_digits=2,decimal_places=0)
    grosse_abos = DecimalField(max_digits=2,decimal_places=0)
    haus_abos = DecimalField(max_digits=2,decimal_places=0)
    depot = CharField(widget=Select )