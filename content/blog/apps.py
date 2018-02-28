from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BlogConfig(AppConfig):
    name = 'content.blog'
    verbose_name = _('Blog')
