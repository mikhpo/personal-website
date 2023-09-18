from django import forms

from gallery.models import Album, Photo


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
