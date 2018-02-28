from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index


class HomePage(Page):
    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]


class BlogIndexPage(Page):
    parent_page_types = []
    subpage_types = ['BlogPage']

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context['blog_entries'] = BlogPage.objects.child_of(self).live()
        return context


class BlogPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname='full title')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])
    date = models.DateField('Post date')
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
        ImageChooserPanel('feed_image'),
    ]

    parent_page_types = ['BlogIndexPage']
    subpage_types = []
