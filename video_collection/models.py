from urllib import parse 
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True) # optional field
    video_ID= models.CharField(max_length=40, unique=True) 
    
    def save(self, *args, **kwargs):
        if not self.video_ID:
            if self.url.startswith('https://www.youtube.com/watch?v'): # checks if the url is a youtube video
                if '=' in self.url:
                    # splits the url by = and takes the first index, outputs ['https://www.youtube.com/watch?v', 'HNHu-beUzZM&list', 'WL&index', '5']

                    video_id_part = self.url.split('=')[1].split('&')[0]
                    # Check if the video_id_part is of a typical YouTube ID length
                    if len(video_id_part) != 11: # checks if the video_id_part is 11 characters long
                        raise ValidationError('Invalid URL, must be a YouTube video.')
                    self.video_ID = video_id_part
                else:
                    raise ValidationError('Invalid URL, must be a YouTube video.')
            else:
                raise ValidationError('Invalid URL, must be a YouTube video.')
            
        else:
            # error when video_ID is not unique
            raise ValidationError('Video ID already exists')
        super().save(*args, **kwargs)





    
    def __str__(self):
        return f'ID: {self.id} - Name: {self.title} - URL: {self.url} - Notes: {self.notes[:200]} - Video_ID: {self.video_ID}' # chuck the notes to the first 200 characters