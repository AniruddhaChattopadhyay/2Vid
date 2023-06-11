from django import forms
   
# creating a form 
class ProcessFromURLForm(forms.Form):
   
    url = forms.CharField(label='URL')
    English = forms.BooleanField(label='English', required=False)
    Hindi = forms.BooleanField(label='Hindi', required=False)
    Bengali = forms.BooleanField(label='Bengali', required=False)