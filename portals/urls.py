from django.urls import path
from . import views

app_name = 'portals'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('portal/create/', views.portal_create, name='portal_create'),
    path('portal/<int:portal_id>/update/', views.portal_update, name='portal_update'),
    path('portal/<int:portal_id>/delete/', views.portal_delete, name='portal_delete'),
    path('portal/<int:portal_id>/check/', views.portal_check_now, name='portal_check'),
    path('portal/<int:portal_id>/availability/', views.portal_availability, name='portal_availability'),
    path('portal/reorder/', views.portal_reorder, name='portal_reorder'),
]
