from django.urls import path
from finance_app import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", views.home, name="home"),
    path("transactions/", views.transactions_view, name="transactions"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(
        template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("goals/", views.goals_page, name="goals_page"),
    path("analytics/", views.analytics, name="analytics"),
    path("goals/toggle_active/<int:goal_id>/", views.toggle_active,
         name="toggle_active"),
    path("reports/", views.reports_view, name="reports"),
    path("reports/export_csv/", views.export_csv, name="export_csv"),
]
