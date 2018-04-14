from allauth.account import views as allauth
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('hijos.users.urls', namespace='users')),
    url(r'^accounts/login/$', allauth.login, name='account_login'),
    url(r'^accounts/logout/$', allauth.logout, name='account_logout'),
    # redirect signup to login
    url(r'^accounts/signup/$', allauth.login, name='account_signup'),
    url(
        r'^accounts/password/change/$',
        allauth.password_change,
        name='account_change_password'
    ),
    url(
        r'^accounts/password/set/$',
        allauth.password_set,
        name='account_set_password'
    ),
    url(
        r'^accounts/inactive/$',
        allauth.account_inactive,
        name='account_inactive'
    ),
    url(r"^email/$", allauth.email, name="account_email"),
    url(
        r"^confirm-email/$",
        allauth.email_verification_sent,
        name="account_email_verification_sent"
    ),
    url(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        allauth.confirm_email,
        name="account_confirm_email"
    ),

    # Your stuff: custom urls includes go here


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
