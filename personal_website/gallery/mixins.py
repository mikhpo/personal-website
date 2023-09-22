from gallery.models import Album, Tag


class GalleryContentMixin(object):
    """
    Миксин для добавления в контекст запроса списка альбомов и тегов галереи.
    """

    def get_context_data(self, **kwargs):
        context = super(GalleryContentMixin, self).get_context_data(**kwargs)
        context["albums"] = Album.published.all()
        context["tags"] = Tag.objects.all()
        return context
