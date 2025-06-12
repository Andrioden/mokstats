from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from mokstats import ajax, views

admin.autodiscover()


""" LIST OF PATTERNS """
urlpatterns = [
    path('', views.index),
    path('players/<int:pid>/', views.player),
    path('players/', views.players),
    path('matches/<int:mid>/', views.match),
    path('matches/', views.matches),
    path('stats/', views.stats),
    path('stats/best-results/', views.stats_best_results),
    path('stats/worst-results/', views.stats_worst_results),
    path('stats/top-rounds/', views.stats_top_rounds),
    path('stats/biggest-match-sizes/', views.stats_biggest_match_sizes),
    path('rating/', views.rating),
    path('rating/description/', views.rating_description),
    path('activity/', views.activity),
    # AJAX CALLS
    path('ajax/last_playerlist/', ajax.last_playerlist),
    path('ajax/clear_cache/', ajax.clear_cache),
    # ADMIN PAGES
    path("admin/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
