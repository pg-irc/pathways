from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BlogPageConfig(AppConfig):
    name = 'content.blog_page'
    verbose_name = _('BlogPage')
