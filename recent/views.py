from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from music.models import *
import collections
import operator

def get_subscriptions(user):
    my_playlists = Playlist.objects.filter(author = user)
    return my_playlists


@login_required
def recent(request):
    albums = Album.objects.all().order_by("-id")[0:8]
    playlists = Playlist.objects.all().order_by("-id")[0:8]
    artists = Artist.objects.all().order_by("-id")[0:8]


    top_sub_artist = Artist.objects.all()
    top_artists = {}
    for item in top_sub_artist:
        tracks = Music.objects.filter(artist = item.id).aggregate(auditions=Sum("auditions"))
        if not tracks['auditions'] == None:
            top_artists[item.id] = tracks['auditions']
    top_artists = sorted(top_artists.items(), key=lambda kv: kv[1])[-8:]
    top_artist = []
    for item in top_artists:
        art = Artist.objects.get(id=item[0])
        top_artist.append({ 
                'image':art.image,
                'name':art.name,
                'url':art.url,
                },)

    top_sub_album = Album.objects.all()
    top_albums = {}
    for item in top_sub_album:
        tracks = Music.objects.filter(album = item.id).aggregate(auditions=Sum("auditions"))
        if not tracks['auditions'] == None:
            top_albums[item.id] = tracks['auditions']
    top_albums = sorted(top_albums.items(), key=lambda kv: kv[1])[-8:]
    top_album = []
    for item in top_albums:
        albu = Album.objects.get(id=item[0])
        top_album.append({ 
                'image':albu.image,
                'name':albu.name,
                'url':albu.url,
                'date_create':albu.date_create,
                'get_album_status_display':albu.get_album_status_display,
                },)

    top_tracks = Music.objects.all().order_by("-auditions")[0:8]

    # playlists = Playlist.objects.all()[0:8]
    context = {
        'top_artist': top_artist[::-1],
        'top_album': top_album[::-1],
        'top_tracks': top_tracks,

        'artists': artists,
        'albums': albums,
        'playlist': playlists,
        'playlists': get_subscriptions(request.user),
    }





    if request.method == 'POST':
        return HttpResponse(render(request, 'recent/pages/recent.html', context))
    return render(request, 'recent/recent.html', context)