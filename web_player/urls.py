from django.contrib import admin
from django.urls import path
from music import views
import recent.views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('W8HldoTIbNRQ3Jrm/', admin.site.urls),


    path('', views.loginuser, name='loginuser'),
    path('signup/', views.signupuser, name='signupuser'),
    path('logout/', views.logoutuser, name='logoutuser'),
    
    path('search/', views.search_result, name='search'),

    path('preferences/', views.preferences, name='preferences'),
    path('profile/', views.profile, name='me'),
    path('datacloud/', views.datacloud, name='datacloud'),
    path('music/sync/', views.sync, name='sync'),


    path('favorite_music/', views.favorite_music, name='favorite_music'),
    path('artist/<author_id>', views.author, name='author'),
    path('album/<album_id>', views.album, name='album'),
    path('playlist/<playlist_id>', views.playlist, name='playlist'),

    path('application/manage/<track_id>&<classname>', views.manage_track_user, name='manage_track_user'),
    path('application/manage/playlist/<playlist_id>&<track_id>', views.add_to_playlist, name='add_to_playlist'),


    path('music/get_favorite', views.get_liked, name='get_liked'),

    path('music/<filename>', views.protected_media, name='protected_media'),


    path('recent/', recent.views.recent, name='recent'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)