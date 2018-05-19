from allauth.account import views as allauth
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from hijos.users.views import LodgesList

urlpatterns = [
    path(
        '',
        view=LodgesList.as_view(),
        name='home'
    ),

    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),

    # User management
    path('users/', include('hijos.users.urls', namespace='users')),
    path('accounts/login/', allauth.login, name='account_login'),
    path('accounts/logout/', allauth.logout, name='account_logout'),
    # redirect signup to login
    path('accounts/signup/', allauth.login, name='account_signup'),
    path(
        'accounts/password/change/',
        allauth.password_change,
        name='account_change_password'
    ),
    path(
        'accounts/password/set/',
        allauth.password_set,
        name='account_set_password'
    ),
    path(
        'accounts/inactive/',
        allauth.account_inactive,
        name='account_inactive'
    ),
    path('email/', allauth.email, name='account_email'),

    path('treasure/', include('hijos.treasure.urls', namespace='treasure')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path('400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        path('403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ]
