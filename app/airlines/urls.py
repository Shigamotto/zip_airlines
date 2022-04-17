from django.urls import path

from . import views

app_name = 'airlines'

urlpatterns = [
    path('', views.AirplaneCreateAPIView.as_view(), name='create'),
    path('list/', views.AirlineAPIView.as_view(), name='list'),
    path('list/<airplane_id>/', views.AirplaneUpdateApiView.as_view(), name='detail'),
]
