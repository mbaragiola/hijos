from django.urls import path

from hijos.treasure import views

app_name = 'treasure'
urlpatterns = [
    path(
        'lodge/<pk>/lodgeaccounts/',
        view=views.LodgeAccountsByLodgeList.as_view(),
        name='lodgeaccount-list'
    ),
    path(
        'lodgeaccounts/<pk>/',
        view=views.LodgeAccountDetailView.as_view(),
        name='lodgeaccount-detail'
    ),
    path(
        'lodge/<pk>/periods/',
        view=views.PeriodsByLodgeList.as_view(),
        name='period-list'
    ),
    path(
        'periods/<pk>/',
        view=views.PeriodDetailView.as_view(),
        name='period-detail'
    ),
    path(
        'lodge/<pk>/invoices/',
        view=views.InvoicesByLodgeList.as_view(),
        name='invoice-list'
    ),
    path(
        'invoices/<pk>/',
        view=views.InvoiceDetailView.as_view(),
        name='invoice-detail'
    ),
    path(
        'lodge/<pk>/deposits/',
        view=views.DepositsByLodgeList.as_view(),
        name='deposit-list'
    ),
    path(
        'deposits/<pk>/',
        view=views.DepositDetailView.as_view(),
        name='deposit-detail'
    ),
    path(
        'lodge/<pk>/charges/',
        view=views.ChargesByLodgeList.as_view(),
        name='charge-list'
    ),
    path(
        'charges/<pk>/',
        view=views.ChargeDetailView.as_view(),
        name='charge-detail'
    ),
    path(
        'lodge/<pk>/grandlodgedeposits/',
        view=views.GrandLodgeDepositsByLodgeList.as_view(),
        name='grandlodgedeposit-list'
    ),
    path(
        'grandlodgedeposits/<pk>/',
        view=views.GrandLodgeDepositDetailView.as_view(),
        name='grandlodgedeposit-detail'
    ),
]
