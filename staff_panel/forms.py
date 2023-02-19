from django import forms
from django.forms import ModelForm
from music.models import *


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class ArtistForm(ModelForm):
    class Meta:
        model = Artist
        fields = '__all__'
        labels = {
            'url': ('Страница'),
            'image': (''),
            'name': ('Имя'),
            'slug_name': ('Slug'),
            'is_author': ('Is author'),
            'verification': ('verification'),
            'description': ('Описание'),
            'genres': ('Жанры')
        }