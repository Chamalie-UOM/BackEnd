from django.urls import path, include
from .views import *
 
urlpatterns = [
    path('upload', FileUploadView.as_view()),
    path('recommend', RecommendView.as_view()),
    path('preprocess', PreprocessView.as_view()),
    path('getNewick', TreeGenerationView.as_view())


]
