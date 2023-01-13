from django.shortcuts import render

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from music.models import *

@staff_member_required
def main(request):
    artists = Artist.objects.all()
    albums = Album.objects.all()
    tracks = Music.objects.all()

    context = {
        'title': 'Beta panel',
        'artists': artists,
        'albums': albums,
        'tracks': tracks
        }
    return render(request, 'staff_panel/base.html', context)