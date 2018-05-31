from django.urls import path

from hijos.users import views

app_name = 'users'
urlpatterns = [
    path(
        'users/',
        view=views.UserListView.as_view(),
        name='user-list'
    ),
    path(
        'users/add/',
        view=views.UserCreateView.as_view(),
        name='user-create'
    ),
    path(
        'users/<username>/',
        view=views.UserDetailView.as_view(),
        name='user-detail'
    ),
    path(
        'lodges/',
        view=views.LodgesList.as_view(),
        name='lodge-list'
    ),
    path(
        'lodges/<int:pk>/',
        view=views.LodgeDetailView.as_view(),
        name='lodge-detail'
    ),
    path(
        'lodges/<int:pk>/affiliations/',
        view=views.AffiliationsByLodgeList.as_view(),
        name='affiliation-list'
    ),
    path(
        'affiliations/<int:pk>/',
        view=views.AffiliationDetailView.as_view(),
        name='affiliation-detail'
    ),
    path(
        'affiliations/add/',
        view=views.AffiliationCreateView.as_view(),
        name='affiliation-create'
    )
]
