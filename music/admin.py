from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserNew

from .models import GenresMusic, Artist, Album, Music, Playlist
from .models import *


class MusicAdminInline(admin.TabularInline):
    model = Music
    fields = ('sub_artist', 'name', 'track_type', 'language', 'audio_file', 'genres')
    extra = 0



class AlbumAdminInline(admin.TabularInline):
    model = Album
    fields = ('name', 'image', 'album_status')
    extra = 0


@admin.register(UserNew)
class UserNewAdmin(UserAdmin):
    list_display = ('username', 'displayName', 'custom_url', 'email', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (('Info'), {'fields': ('avatar', 'custom_url', 'displayName', 'genres')}),
    )

@admin.register(UserMusicSetting)
class UserMusicSetting(admin.ModelAdmin):
    list_display = ('user', 'last_playlist', 'last_track')




@admin.register(GenresMusic)
class GenresMusicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_author', 'url')
    fieldsets = (
        (None, {'fields': ('url', 'slug_name')}),
        (('Info'), {'fields': ('name', 'description', 'image', 'is_author', 'verification', 'genres')}),
    )
    readonly_fields = ('url', 'slug_name')
    search_fields = ('name', 'is_author', 'genres__name', 'slug_name')
    inlines = (AlbumAdminInline,)

@admin.register(Album)
class ArtistAlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'date_create')
    fieldsets = (
        (None, {'fields': ('url', 'slug_name')}),
        (('Info'), {'fields': ('name', 'artist', 'image', 'date_album', 'album_status')}),
    )
    readonly_fields = ('url', 'slug_name')
    search_fields = ('name', 'artist__name', 'slug_name')
    inlines = (MusicAdminInline,)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.who_added = request.user
            instance.save()
        formset.save_m2m()




@admin.register(Music)
class ArtistAlbumMusicAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'auditions', 'track_time')
    fieldsets = (
        (None, {'fields': ('url', 'slug_name', 'language')}),
        (('Info'), {'fields': ('name', 'artist', 'sub_artist', 'album', 'auditions')}),
        (('Data'), {'fields': ('genres', 'track_type', 'image', 'audio_file', 'track_time')}),
    )
    readonly_fields = ('url', 'auditions', 'track_time', 'slug_name')
    search_fields = ('name', 'album__name', 'artist__name', 'slug_name')
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'who_added', None) is None:
            obj.who_added = request.user
        obj.save()


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'opened')
    fieldsets = (
        (None, {'fields': ('url',)}),
        (('Info'), {'fields': ('name', 'author', 'image', 'correction', 'opened')}),
        (('data'), {'fields': ('tracks', 'quantity')}),
    )
    readonly_fields = ('url', 'quantity', 'correction')
    search_fields = ('name', 'author__name')


@admin.register(FavoriteMusic)
class FavoriteMusicAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_timestamp')

    search_fields = ('user',)

@admin.register(FavoritePlaylist)
class FavoritePlaylistAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_timestamp')

    search_fields = ('user',)