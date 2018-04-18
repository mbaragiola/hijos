from django.urls import path

from hijos.users import views

app_name = 'users'
urlpatterns = [
    path(
        '',
        view=views.UserListView.as_view(),
        name='user-list'
    ),
    path(
        '~redirect/',
        view=views.UserRedirectView.as_view(),
        name='user-redirect'
    ),
    path(
        '<username>/',
        view=views.UserDetailView.as_view(),
        name='user-detail'
    )
]
