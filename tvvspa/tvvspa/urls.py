"""tvvspa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .settings import MEDIA_ROOT, MEDIA_URL
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from . import views
from django.contrib.auth.views import LoginView, LogoutView

#    path('accounts/login/', LoginView),
#    path('accounts/logout/', LogoutView),
#    url(r'^login/$', LoginView.as_view(template_name='registration/login.html'), name='login'),

urlpatterns = [
    path('admin/', admin.site.urls, name='Admin', kwargs=None),
    path('graphql/', GraphQLView.as_view(graphiql=True), name='GraphQL', kwargs=None),
    path('login/', view=LoginView.as_view(), name='Login', kwargs=None),
    path('current_datetime/', view=views.current_datetime, name='Now', kwargs=None),
    path('app/', view=views.AppView.as_view(), name='App', kwargs=None),
    path('player/', view=views.PlayerView.as_view(), name='Player', kwargs=None),
    path('', view=views.IndexView.as_view(), name='index', kwargs=None),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings

def response_error_handler(request, exception=None):
    return HttpResponse('Error handler content', status=403)


def permission_denied_view(request):
    raise PermissionDenied

urlpatterns += [
    path('403/', permission_denied_view),
]

handler403 = response_error_handler

# ROOT_URLCONF must specify the module that contains handler403 = ...
@override_settings(ROOT_URLCONF=__name__)
class CustomErrorHandlerTests(SimpleTestCase):

    def test_handler_renders_template_response(self):
        response = self.client.get('/403/')
        # Make assertions on the response here. For example:
        self.assertContains(response, 'Error handler content', status_code=403)

