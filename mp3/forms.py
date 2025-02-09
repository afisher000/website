from django import forms

class SubmissionForm(forms.Form):
    url = forms.URLField(
        max_length=200, 
        label="URL", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
        )
    artist = forms.CharField(
        max_length=50, 
        label="Artist", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
        )
    name = forms.CharField(
        max_length=50, 
        label="Track Name", 
        widget=forms.TextInput(attrs={'class': 'form-control'}), 
        required=True
        )
