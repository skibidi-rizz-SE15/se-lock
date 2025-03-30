from django.urls import path
from django.contrib import admin
from qr_app.views import generate_qr, log_data

urlpatterns = [
    path("", generate_qr, name="generate_qr"),
    path("admin/", admin.site.urls),
    path("api/log_data/", log_data, name="log_data"),
]