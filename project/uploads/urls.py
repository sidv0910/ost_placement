from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="Home"),
    path('uploadDropDown/', views.uploadUsingDropDown, name="UploadDropDown"),
    path('uploadFolderLocation/', views.uploadUsingFolderLocation, name="UploadFolderLocation"),
    path('download/', views.downloadFile, name="Download"),
]