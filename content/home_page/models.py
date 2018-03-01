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
