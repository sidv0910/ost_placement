from django import forms

class UploadForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True, 'accept':'.pdf, .docx, .doc, .rtf'}))

class FolderUploadForm(forms.Form):
    folder = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Folder Location', 'class':'form-control'}))