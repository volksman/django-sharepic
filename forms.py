from django import forms
from sharepic.models import ClientImage

class ClientImageModelForm(forms.ModelForm):
    
    class Meta:
        model = ClientImage
        exclude = ['client','num_views']
        
class AuthForm(forms.Form):
    email = forms.EmailField(max_length=255)