from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('submit-lead/', views.submit_lead, name='submit_lead'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('brochure/', views.brochure, name='brochure'),
    path('download-brochure/', views.download_brochure, name='download_brochure'),
    path('blueprint/', views.blueprint, name='blueprint'),
    path('walkthrough/', views.walkthrough, name='walkthrough'),
    path('plots/', views.plots, name='plots'),
    path('api/popups/', views.get_popups, name='get_popups'),
    path('api/reviews/', views.all_reviews, name='all_reviews'),
    path('api/visitor-count/', views.visitor_count, name='visitor_count'),
    path('api/track-visit/', views.track_visit, name='track_visit'),
    path('api/plots/', views.api_plots, name='api_plots'),

    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/leads/', views.admin_leads, name='admin_leads'),
    path('admin-panel/leads/export/<str:format>/', views.export_leads, name='export_leads'),
    path('admin-panel/pricing/', views.admin_pricing, name='admin_pricing'),
    path('admin-panel/pricing/delete/<int:pk>/', views.admin_delete_flat_type, name='admin_delete_flat_type'),
    path('admin-panel/popups/', views.admin_popups, name='admin_popups'),
    path('admin-panel/popups/toggle/<int:pk>/', views.admin_toggle_popup, name='admin_toggle_popup'),
    path('admin-panel/popups/delete/<int:pk>/', views.admin_delete_popup, name='admin_delete_popup'),
    path('admin-panel/popups/reorder/', views.admin_reorder_popups, name='admin_reorder_popups'),
    path('admin-panel/visitors/', views.admin_visitors, name='admin_visitors'),
    path('admin-panel/profile/', views.admin_profile, name='admin_profile'),
    path('admin-panel/plots/', views.admin_plots, name='admin_plots'),
    path('admin-panel/plots/update/<int:villa_no>/', views.admin_plot_update, name='admin_plot_update'),
]
