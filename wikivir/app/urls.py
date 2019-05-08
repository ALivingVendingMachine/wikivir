from django.urls import path
from django.contrib.auth import views as auth_views
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
    path('att', views.allTopics, name='allTopics'),
    path('att/<str:topic>', views.topicView, name='topicView'),
    path('topicNotFound/<str:topic>', views.topicNotFound, name='topicNotFound'),
    # API
    path('api/sample/getAllHashes', views.apiSampleGetAll, name='apiSampleGetAll'),
    path('api/sample/<str:sampleHash>', views.apiSample, name='apiSample'),
    path('api/topic/<str:topic>', views.apiTopic, name='apiTopic'),
    # Editors
    path('edit/sample/<str:sampleHash>/<str:mod>', views.editSample, name='editSample'),
    path('edit/topic/<str:topic>', views.editTopic, name='editTopic'),
    #path('debug/<str:topic>', views.debug, name='debug'),
    # User management
    path('register', views.register, name='register'),
    path('login', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', views.logoutView, name='logout'),
]
