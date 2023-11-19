from django import forms

from .models import Video



class VideoForm(forms.ModelForm): # 
    class Meta:
        model = Video
        fields = ('title', 'url', 'notes')
        

class SearchForm(forms.Form):
    search_term = forms.CharField()