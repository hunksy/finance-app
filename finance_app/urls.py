from django.urls import path
from finance_app import views

urlpatterns = [
    path("", views.home, name="home"),
]
