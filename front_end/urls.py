from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import render


def jh(request):
    return render(request, 'jh.html')


urlpatterns = [
    url(r'^$', jh, name='jh'),
    url(r'^admin/', admin.site.urls),
    url(r'^blog/', include(('blog.urls', 'blog'), namespace='blog')),
]
