from django import forms
from .models import Comment

class NewCommentForm(forms.ModelForm):
    '''
    Форма создания нового комментария к статье.
    '''
    content = forms.CharField(label ="", widget = forms.Textarea( 
        attrs ={ 
            'class':'form-control', 
            'placeholder':'Оставить комментарий', 
            'rows':4,
        })) 

    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(NewCommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = ""