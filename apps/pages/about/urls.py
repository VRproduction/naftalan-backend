from django.urls import path
from . import views


urlpatterns = [
   path('', views.AboutView.as_view(), name='about'),
   path('history/', views.HistoryView.as_view(), name='history'),
   path('treatment-page/', views.TreatmentPageView.as_view(), name='treatment'),
   path('treatment-category-list/', views.TreatmentCategoryView.as_view(), name='treatment-category'),
   path('treatment-list/', views.TreatmentListView.as_view(), name='treatment-list'),
   path('treatment-process-list/', views.TreatmentProcessListView.as_view(), name='treatment-process-list'),
]