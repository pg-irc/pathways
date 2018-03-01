from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class HomePageConfig(AppConfig):
    name = 'content.home_page'
    verbose_name = _('HomePage')
