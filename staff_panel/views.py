from django.shortcuts import render

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from music.models import *



from .forms import *

@staff_member_required
def main(request):
    artists = Artist.objects.all()
    albums = Album.objects.all()
    tracks = Music.objects.all()


    context = {
        'title': 'Beta panel',
        'artists': artists
        }
    return render(request, 'staff_panel/base.html', context)


@staff_member_required
def get_info(request):
    if request.method == 'POST':
        print(request.POST['data'])
        artist_id = request.POST['data']

        artists = Artist.objects.get(url = artist_id)
        albums = Album.objects.filter(artist__url = artist_id)
        tracks = Music.objects.filter(artist__url = artist_id)
        genres = GenresMusic.objects.all()

        form = ArtistForm(instance=artists)

        context = {
            'title': 'Beta panel',
            'artists': artists,
            'albums': albums,
            'tracks': tracks,
            'genres': genres,

            'form': form
            }
        return render(request, 'staff_panel/parts/form.html', context)