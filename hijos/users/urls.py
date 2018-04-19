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
        '<username>/',
        view=views.UserDetailView.as_view(),
        name='user-detail'
    ),
    path(
        'lodges/',
        view=views.LodgesList.as_view(),
        name='lodge-list'
    ),
    path(
        'lodges/<pk>/',
        view=views.LodgeDetailView.as_view(),
        name='lodge-detail'
    ),
    path(
        'lodges/<pk>/affiliations/',
        view=views.AffiliationsByLodgeList.as_view(),
        name='affiliations-list'
    ),
    path(
        'affiliations/<pk>/',
        view=views.AffiliationDetailView.as_view(),
        name='affiliation-detail'
    )
]
