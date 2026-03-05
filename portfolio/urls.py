from django.urls import path # type: ignore
from . import views
from django.conf import settings
from django.conf.urls.static import static
from portfolio.views import ProjectDetailView,debug_contact
from .views import send_test_email

urlpatterns = [
    path('', views.PortfolioHomeView.as_view(), name='portfolio_home'),
    path('media/', views.MediaGalleryView.as_view(), name='media_gallery'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('admin/portfolio/contactmessage/<int:message_id>/send_test_email/', 
    send_test_email, 
    name='send_test_email'),
    path('debug-contact/', debug_contact, name='debug_contact'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)