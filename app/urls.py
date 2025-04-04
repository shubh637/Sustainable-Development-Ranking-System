from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login_view, name="login"),  
    path("register/", views.register, name="register"),
    path("logout/",views.logout_view,name='logout'),
    path("index/", views.index, name="index"),
    path("page/<str:page_name>/", views.dynamic_page, name="dynamic_page"),
    path("carbon_calculator/", views.carbon_calculator, name="carbon_calculator"), 
    path("calculate_eevta_score/", views.eevta_calculator, name="calculate_eevta_score"), 
    path("energy_calculator/", views.energy_calculator, name="energy_calculator"),
    path("waste_calculator/", views.waste_calculator, name="waste_calculator"),
    path("sustainability_calculator/", views.calculate_sustainability_score, name="sustainability_calculator"),
    path("dashboard/", views.sustainability_dashboard, name="dashboard"),
    path('history/', views.calculation_history, name='history'),
]
