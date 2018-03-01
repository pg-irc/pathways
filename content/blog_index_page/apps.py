from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BlogIndexPageConfig(AppConfig):
    name = 'content.blog_index_page'
    verbose_name = _('BlogIndexPage')
