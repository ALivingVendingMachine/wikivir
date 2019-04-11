from django.urls import path
from . import views

urlpatterns = [
    # basic stuff
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    # samples
    path('sample/<str:sampleHash>', views.sampleView, name='sampleView'),
    path('sampleNotFound/<str:sampleHash>', views.sampleNotFound, name='sampleNotFound'),
    # adversary tactics and techniques & common knowledge, thanks MITRE for the cool
    # acronym
    path('att/<str:topic>', views.topicView, name='topicView'),
    path('topicNotFound/<str:topic>', views.topicNotFound, name='topicNotFound'),
    path('api/sample/<str:sampleHash>', views.apiSample, name='apiSample'),
    path('addtag/sample/<str:sampleHash>', views.addTag, name='addTag'),
    path('edit/sample/<str:sampleHash>/<str:mod>', views.editSample, name='editSample'),
    path('edit/topic/<str:topic>', views.editTopic, name='editTopic'),
    #path('debug/<str:topic>', views.debug, name='debug'),
]
