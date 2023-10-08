from django import forms

from gallery.models import Album, Photo


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class AlbumForm(forms.ModelForm):
    """
    Форма создания или редактирования фотоальбома в административной панели.
    """

    class Meta:
        model = Album
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            album: Album = self.instance
            self.fields["cover"].queryset = album.photo_set.all()
        else:
            self.fields["cover"].queryset = Photo.objects.none()


class UploadForm(forms.Form):
    """
    Форма для пакетной загрузки фотографий в альбом.
    """

    album = forms.ModelChoiceField(queryset=Album.objects.all(), label="Альбом")
    photos = MultipleFileField(label="Фотографии")
