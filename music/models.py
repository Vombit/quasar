from email.policy import default
import random
from sqlite3 import Timestamp
import string
import secrets
import os
import mutagen
from turtle import mode
from unicodedata import name
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from functools import partial
from transliterate import translit, detect_language
import cutlet
import re




def slug_name(sender, instance, *args, **kwargs):
    if not instance.slug_name:
        katsu = cutlet.Cutlet()
        katsu.ensure_ascii = False
        katsu.use_foreign_spelling = False
        text = katsu.romaji(instance.name)

        if not detect_language(text) == None:
            instance.slug_name = re.sub("[^a-zA-Z0-9_ ]", "", translit(text, reversed=True).lower()).replace("  ", " ")
        else:
            instance.slug_name = re.sub("[^a-zA-Z0-9_ ]", "", text.lower()).replace("  ", " ")





def update_filename(instance, filename, path):
    path = path
    ext = filename.split('.')[-1]
    file_code = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(32))
    filename = '{}.{}'.format(file_code, ext)
    return os.path.join(path, filename)
def upload_to(path):
    return partial(update_filename, path=path)

def track_duration(sender, instance, raw, using, update_fields, **kwargs):
    file_was_updated = False
    if hasattr(instance.audio_file, 'file'):
        file_was_updated = True
    if update_fields and "audio_file" in update_fields:
        file_was_updated = True          
    if file_was_updated:
        audio_info = mutagen.File(instance.audio_file).info
        time = int(audio_info.length)
        time_min = time // 60
        time_sec = time - ((time // 60) * 60)
        instance.track_time = time
        instance.track_time_min = time_min
        if time_sec < 10:
            instance.track_time_sec = '{:02}'.format(time_sec)
        else:
            instance.track_time_sec = time_sec

            

def generator_url(sender, instance, *args, **kwargs):
    if not instance.url:
        instance.url = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(16))





class GenresMusic(models.Model):
    name = models.CharField(max_length=48, unique=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserNew(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_login = models.DateTimeField(null=True)
    avatar = models.ImageField(upload_to=upload_to("user/avatar"), blank=True, null=True)
    custom_url = models.CharField(max_length=24, unique=True, blank=True, null=True)
    displayName = models.CharField(max_length=24, blank=True, null=True)
    genres = models.ManyToManyField(GenresMusic, blank=True, related_name = 'tasks_as_genres')

    def save(self, *args, **kwargs):
        if not self.displayName:
            self.displayName = self.username
        super(UserNew, self).save(*args, **kwargs)






class Artist(models.Model):
    url = models.SlugField(max_length = 18, unique=True, db_index=True, blank=True)
    image = models.ImageField(upload_to=upload_to("artist/image"), blank=True, null=True)

    name = models.CharField(max_length=128)
    slug_name = models.CharField(max_length=128, blank=True)

    is_author = models.CharField(max_length=16, blank=True, null=True)
    verification = models.BooleanField(default=False)

    description = models.TextField(max_length=2048, blank=True)
    genres = models.ManyToManyField(GenresMusic, blank = True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/artist/{self.url}'

class Album(models.Model):
    state = (
    ('S', 'Сингл'),
    ('A', 'Альбом'),
    ('MA', 'Мини-альбом'),
    )

    url = models.SlugField(max_length = 18, unique=True, db_index=True, blank=True)
    image = models.ImageField(upload_to=upload_to("artist/album"), blank=True, null=True)

    name = models.CharField(max_length=128)
    slug_name = models.CharField(max_length=128, blank=True)

    artist = models.ManyToManyField(Artist)

    date_create = models.DateTimeField(auto_now=True, editable=True)
    date_album = models.DateField(blank=True, null=True)
    album_status = models.CharField(max_length=30, choices=state, default='Сингл')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/album/{self.url}'


langs = (
    ('rus', 'russian'),
    ('eng', 'english'),
    ('jpn', 'japanese'),
    ('fra', 'french'),
    ('zho', 'chinese'),
    ('ukr', 'ukrainian'),
    ('isl', 'icelandic'),
    )

class Music(models.Model):
    url = models.SlugField(max_length = 18, unique=True, db_index=True, blank=True)
    image = models.ImageField(upload_to=upload_to("tracks/images"), blank=True, null=True)
    audio_file = models.FileField(upload_to=upload_to("tracks"), blank=True)

    name = models.CharField(max_length=128)
    slug_name = models.CharField(max_length=128, blank=True)
    language = models.CharField(max_length=30, choices=langs, blank=True, null=True)

    genres = models.ForeignKey(GenresMusic, on_delete = models.SET_NULL, blank=True, null = True)
    date_create = models.DateTimeField(auto_now_add=True)

    track_time = models.PositiveIntegerField("Track duration ins seconds", blank=True, null=True)
    track_time_min = models.PositiveIntegerField("Track duration ins min", blank=True, null=True)
    track_time_sec = models.CharField(max_length = 3, blank=True, null=True)

    auditions = models.IntegerField(default=0)
    track_type = models.CharField(max_length=64, blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.RESTRICT)

    sub_artist = models.ManyToManyField(Artist, blank=True, related_name = 'tasks_as_sub_artist')

    who_added = models.ForeignKey(UserNew, null=True, blank=True, on_delete = models.PROTECT)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url
    
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = self.album.image
        if not self.artist:
            self.artist = self.album.artist

        super(Music, self).save(*args, **kwargs)



class FavoriteMusic(models.Model):
    user = models.ForeignKey(UserNew, on_delete=models.CASCADE)
    tracks = models.ForeignKey(Music, on_delete=models.CASCADE)
    added_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_timestamp']
    def __str__(self):
        return f'{self.user.username} | {self.added_timestamp}'

class ListenedTrack(models.Model):
    user = models.ForeignKey(UserNew, on_delete=models.CASCADE)
    tracks = models.ForeignKey(Music, on_delete=models.CASCADE)
    added_timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-added_timestamp']
    def __str__(self):
        return f'{self.user.username} | {self.tracks} | {self.duration}'






class Playlist(models.Model):
    url = models.SlugField(max_length = 18, unique=True, db_index=True, blank=True)
    image = models.ImageField(upload_to=upload_to("user/playlist"), blank=True, null=True)
    name = models.CharField(max_length=32)
    opened = models.BooleanField(default=True)
    correction = models.DateTimeField(auto_now=True)
    tracks = models.ManyToManyField(Music)
    author = models.ForeignKey(UserNew, on_delete = models.SET_NULL, null = True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def as_json(self):
        return dict(
            tracks=self.tracks, 
        )

class FavoritePlaylist(models.Model):
    user = models.ForeignKey(UserNew, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    added_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_timestamp']
    def __str__(self):
        return f'{self.user.username} | {self.added_timestamp}'





class UserMusicSetting(models.Model):
    user = models.ForeignKey(UserNew, on_delete=models.CASCADE, null=True)
    type_t = models.CharField(max_length=128, default='123')
    last_playlist = models.CharField(max_length=128, default='123')
    last_track = models.CharField(max_length=32, default='123')
    tracks = models.ManyToManyField(Music, blank=True, related_name = 'last_list')
    current_volume = models.FloatField(default=0.5)   



pre_save.connect(slug_name, sender=Artist)
pre_save.connect(slug_name, sender=Album)
pre_save.connect(slug_name, sender=Music)

pre_save.connect(generator_url, sender=Music)
pre_save.connect(generator_url, sender=Artist)
pre_save.connect(generator_url, sender=Album)
pre_save.connect(generator_url, sender=Playlist)

pre_save.connect(track_duration, sender=Music)