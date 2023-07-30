from django import forms 
from .models import Account

class RegisterationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'password',
        'class':'form-control',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm password'
    }))





    class Meta:
        model = Account
        fields = ['first_name','last_name', 'phone_number','email','password','confirm_password']






    def __init__(self, *args, **kwargs):
        super(RegisterationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



    
        


    

