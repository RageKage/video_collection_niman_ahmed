from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import Video
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower


# Create your views here.


def home(request):
    app_name = "Exercise Videos!"
    
    return render(request, 'video_collection/home.html', {'app_name': app_name})



def add_video(request):
    if request.method == 'POST': 
        form = VideoForm(request.POST) # form with the data from POST request
        if form.is_valid():
            try:
                form.save() # save the video
                messages.info(request, 'Video added successfully!')
                return redirect('video_list') # redirect to video_list page
            except ValidationError: # if the url is not a youtube video
                messages.warning(request, 'Invalid URL, must be a YouTube video.')
            except IntegrityError: # if the video_ID is not unique
                messages.warning(request, 'Video ID already exists.')
        else:
            messages.warning(request, 'Invalid form, please try again.')
            return render(request, 'video_collection/add_video.html', {'new_video_form': form})


    form = VideoForm() 
    return render(request, 'video_collection/add_video.html', {'new_video_form': form})


def video_list(request):
    
    search_form = SearchForm(request.GET) # get the search term from the form
    
    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']
        videos = Video.objects.filter(title__icontains=search_term).order_by(Lower('title')) # get videos that contain the search term
    
    else:
        search_term = SearchForm()
        videos = Video.objects.all().order_by(Lower('title')) 
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form, 'search_term': search_term})

def video_detail(request, video_pk):
    # get video details
    video = get_object_or_404(Video, pk=video_pk)
    return render(request, 'video_collection/video_detail.html', {'video': video})

def delete_video(request, video_pk):
    # delete video
    video = get_object_or_404(Video, pk=video_pk)
    if request.method == 'POST': 
        video.delete()
        messages.info(request, 'Video deleted successfully!')
        return redirect('video_list') # redirect to video_list page