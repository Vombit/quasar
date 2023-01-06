from pkgutil import iter_modules
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User
from music.models import UserNew as User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from .forms import UploadFileForm
from music.models import *
from transliterate import translit, detect_language
import cutlet
import re


def user_data(user_name):
    user = UserNew.objects.get(username = user_name)
    return user


def get_subscriptions(user):
    my_playlists = Playlist.objects.filter(author = user)
    return my_playlists

def get_favorite(user):
    my_favorite = FavoriteMusic.objects.filter(user=user)
    return my_favorite


def slug_search(context):
    katsu = cutlet.Cutlet()
    katsu.ensure_ascii = False
    katsu.use_foreign_spelling = False
    text = katsu.romaji(context)

    if not detect_language(text) == None:
        context = re.sub("[^a-zA-Z0-9_ ]", "", translit(text, reversed=True).lower()).replace("  ", " ")
    else:
        context = re.sub("[^a-zA-Z0-9_ ]", "", text.lower()).replace("  ", " ")

    return context






def signupuser(request):
    if request.method == 'GET':
        return render(request, 'music/signup.html')
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
                user.save()
                login(request, user)
                return redirect('me')
            except IntegrityError:
                return render(request, 'music/signup.html', {'error':'That username has already been taken'})
        else:
            return render(request, 'music/signup.html', {'error':'Passwords did not match'})

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('me')
    elif request.method == 'GET':
        return render(request, 'music/index.html')
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'music/index.html', {'form':AuthenticationForm(), 'error':"login or password did't match"})
        elif user.is_active:
            login(request, user)
            return redirect('me')

@login_required
def logoutuser(request):
    logout(request)
    return redirect('/')

@login_required
def profile(request):
    user = UserNew.objects.get(username = request.user.username)

    context = {
        'title': 'Profile',
        'genres': user.genres.all(),
        'playlists': get_subscriptions(request.user),
        'tracks':  FavoriteMusic.objects.filter(user=request.user),
    }

    if request.method == 'POST':
        return HttpResponse(render(request, 'music/pages/profile.html', context))

    return render(request, 'music/profile.html', context)






@login_required
def favorite_music(request):
    music = FavoriteMusic.objects.filter(user=request.user)

    tracks = []

    for item in music:
        tracks.append({ 
                'image':item.tracks.image,
                'url':item.tracks.url,
                'name':item.tracks.name,
                'artist':item.tracks.artist,
                'track_type':item.tracks.track_type,
                'album':item.tracks.album,
                'auditions':item.tracks.auditions,
                'track_time_min':item.tracks.track_time_min,
                'track_time_sec':item.tracks.track_time_sec,
                'sub_artist': item.tracks.sub_artist,
                },)
        
    context = {
        'title': 'Favorite Music',
        'tracks': tracks,
        'playlists': get_subscriptions(request.user),
        'type': 'fav',
        'id': '',
    }

    if request.method == 'POST':
        return HttpResponse(render(request, 'music/pages/favorite.html', context))
    return render(request, 'music/favorite_music.html', context)

@login_required
def author(request, author_id):
    author = get_object_or_404(Artist, url = author_id)
    tracks = Music.objects.filter(Q(artist=author.id) | Q(sub_artist=author.id)).distinct().order_by('-auditions')[:5]
    
    albums = Album.objects.filter(artist = author.id).order_by('-date_album')

    context = {
        'title': f'artist - {author.name}',
        'author_avatar': author.image,
        'name': author.name,
        'is_author': author.is_author,
        'genres': author.genres.all(),
        'tracks': tracks,
        'albums': albums,
        'playlists': get_subscriptions(request.user),
        'type': 'artist',
        'id': author.url,
    }
    if request.method == 'POST':
        return HttpResponse(render(request, 'music/pages/author.html', context))

    return render(request, 'music/author.html', context)

@login_required
def album(request, album_id):
    album = get_object_or_404(Album, url = album_id)
    tracks = Music.objects.filter(album = album.id)
    context = {
        'title': f'album - {album.name}',
        'album_avatar': album.image,
        'album_date': album.date_album,
        'name': album.name,
        'album_status': album,
        'tracks': tracks,
        'playlists': get_subscriptions(request.user),
        'type': 'album',
        'id': album.url,
    }
    if request.method == 'POST':
        return HttpResponse(render(request, 'music/pages/album.html', context))
    return render(request, 'music/album.html', context)

@login_required
def playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, url = playlist_id)

    context = {
        'title': f'playlist - {playlist.name}',
        'name': playlist.name,
        'playlist_avatar': playlist.image,
        'author': playlist.author,
        'correction': playlist.correction,
        'tracks': playlist.tracks.all(),
        'playlists': get_subscriptions(request.user),
        'type': 'playlist',
        'id': playlist.url,
    }

    if request.method == 'POST':
        return HttpResponse(render(request, 'music/pages/playlist.html', context))

    return render(request, 'music/playlist.html', context)


@login_required
def manage_track_user(request, track_id, classname):
    track = Music.objects.get(url = track_id)
    liked = FavoriteMusic.objects.filter(user=request.user, tracks=track)

    if classname == 'add':
        if not liked.exists():
            FavoriteMusic.objects.create(user=request.user, tracks=track)
    elif classname == 'remove':
        if liked.exists():
            liked.delete()

    return redirect(request.META.get('HTTP_REFERER'))




@login_required
def preferences(request):
    context = {
        "user_genres": request.user.genres.all(),
        "genres": GenresMusic.objects.all().order_by('name'),
    }

    if request.method == 'POST':
        if len(request.POST) > 2:
            user = UserNew.objects.get(username = request.user.username)
            if request.FILES: user.avatar = request.FILES['avatar']
            user.displayName = request.POST['username']
            user.email = request.POST['email']
            user.genres.clear()

            for item in request.POST.getlist('preferences_genres'):
                genre = GenresMusic.objects.get(name = item)
                user.genres.add(genre)

            user.save()
            return redirect('me')

        return HttpResponse(render(request, 'music/pages/preferences.html', context))

    return render(request, 'music/preferences.html', context)

@login_required
def get_liked(request):
    tracks = get_favorite(request.user)
    if request.method == 'GET':
        array = []
        for item in tracks:
            array.append(item.tracks.url,)
        data = {
            'array_tracks_id': array,
        }
        return JsonResponse({'message':data}, safe=False)


@login_required
def search_result(request):
    if request.method == 'POST':
        series = request.POST.get('data')
        if len(series) > 1:
            post_msg = slug_search(series)

            author = Artist.objects.filter(slug_name__icontains=post_msg)
            authors = []
            for index, item in enumerate(author):
                if index == 5: break
                items = {
                    'name': item.name,
                    'image': str(item.image),
                    'url': item.url,
                }
                authors.append(items)

            album = Album.objects.filter(slug_name__icontains=post_msg)
            albums = []
            for index, item in enumerate(album):
                if index == 5: break
                items = {
                    'name': item.name,
                    'image': str(item.image),
                    'url': item.url,
                }
                albums.append(items)

            track = Music.objects.filter(Q(slug_name__icontains=post_msg) | Q(artist__slug_name__icontains=author[0]))
            tracks = []
            for index, item in enumerate(track):
                if index == 5: break
                items = {
                    'name': item.name,
                    'author': item.artist.name,
                    'url': item.album.url,
                    'image': str(item.image),
                }
                tracks.append(items)

            data = {
                'authors': authors,
                'albums': albums,
                'tracks': tracks,
            }

            return JsonResponse({'message':data})
    return JsonResponse({'message':'not found'})


@login_required
def datacloud(request):
    user = UserMusicSetting.objects.filter(user=request.user)
    userdata = UserMusicSetting.objects.get(user=request.user)

    if not user.exists():
        usr = UserMusicSetting.objects.create(user=request.user)
        usr.save()

    if request.method == 'POST':
        track = Music.objects.get(url = request.POST['data[track]'])

        userdata.last_track = request.POST['data[track]']
        userdata.current_volume = request.POST['data[curvolume]']
        userdata.current_time = request.POST['data[curtime]']

        needtime = track.track_time * 0.6
        if int(float(request.POST['data[curtime]'])) >= needtime:
            if not int(float(request.POST['data[curtime]'])) >= needtime+10:
                track.auditions += 1
                track.save()


        userdata.save()
        return JsonResponse(True, safe=False)




@login_required
def sync(request):
    userdata = UserMusicSetting.objects.get(user=request.user)

    if request.method == 'GET':
        tracks = []
        if userdata.type_t == 'fav':
            music = FavoriteMusic.objects.filter(user=request.user).order_by('-added_timestamp')
            for item in music:
                a_dict = ({
                        "id": item.tracks.url, 
                        "name": item.tracks.name, 
                        "image": str(item.tracks.image),
                        "author": item.tracks.artist.name,
                        "author_url": item.tracks.artist.url
                    }, )
                tracks += list(a_dict)
        else:
            for item in userdata.tracks.all().order_by('date_create'):
                a_dict = ({
                        "id": item.url, 
                        "name": item.name, 
                        "image": str(item.image), 
                        "audio_file": str(item.audio_file),
                        "author": item.artist.name,
                        "author_url": item.artist.url
                    }, )
                tracks += list(a_dict)

        data = {
            'playlist':tracks,
            'track': userdata.last_track,
            'curtime': userdata.current_time,
            'curvol': userdata.current_volume,
        }
        return JsonResponse({'message':data}, safe=False)

    elif request.method == 'POST':
        data_type = request.POST.get('type')
        data_id = request.POST.get('id')
        track = request.POST.get('track')
        

        if data_type == 'album':
            userdata.tracks.remove(*userdata.tracks.all())
            tracks = Music.objects.filter(album__url=data_id)
            userdata.tracks.add(*tracks)
            userdata.last_track = track
            userdata.type_t = data_type
            userdata.save()
            return  HttpResponse(True)

        elif data_type == 'artist':
            userdata.tracks.remove(*userdata.tracks.all())
            tracks = Music.objects.filter(Q(artist__url=data_id) | Q(sub_artist__url=data_id)).distinct().order_by('-auditions')[:5]
            userdata.tracks.add(*tracks)
            userdata.last_track = track
            userdata.type_t = data_type
            userdata.save()
            return  HttpResponse(True)

        elif data_type == 'playlist':
            userdata.tracks.remove(*userdata.tracks.all())
            tracks = Playlist.objects.get(url=data_id)
            userdata.tracks.add(*tracks.tracks.all())
            userdata.last_track = track
            userdata.type_t = data_type
            userdata.save()
            return  HttpResponse(True)

        elif data_type == 'fav':
            userdata.tracks.remove(*userdata.tracks.all())
            tracks = FavoriteMusic.objects.filter(user=request.user).values_list('tracks', flat=True)
            userdata.tracks.add(*tracks)
            userdata.last_track = track
            userdata.type_t = data_type
            userdata.save()
            return  HttpResponse(True)

    return HttpResponse(False)




@login_required
def protected_media(request, filename):
    # print(request.headers['Range'])
    track = Music.objects.filter(url = filename).first()

    response = HttpResponse(track.audio_file.file, content_type='audio/mpeg')

    total_range = os.path.getsize('media/'+track.audio_file.name)
    total_range2 = total_range-1
    response['Content-Length'] = total_range

    response['Content-Range'] = f'bytes 0-{total_range2}/{total_range}'

    response['Accept-Range'] = 'bytes'
    response.status_code = 206

    return response




@login_required
def add_to_playlist(request, playlist_id, track_id):
    print(playlist_id, track_id)

    

    return HttpResponse(True)