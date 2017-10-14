"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

# v1/polls/
#   GET
#   POST
# v1/polls/<id>/
#   GET
#   PUT
#   DELETE
# v1/polls/<id>/choices/
#   GET
#   POST
# v1/polls/<id>/choices/<id>/
#   GET
#   PUT
#   DELETE
# v1/polls/<id>/choices/<id>/vote/
#   POST

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^v1/forms/polls/', include('polls.urls')),
    url(r'^v1/', include('polls.api')),
    url(r'^admin/', admin.site.urls),
]
