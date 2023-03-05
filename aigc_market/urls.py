from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload_page, name='upload'),
    path('register_doc', views.register_aigc, name='register_doc'),
    path('market', views.marketplace, name='marketplace'),
    path('my_creations', views.my_creations, name='my_creations')
]
