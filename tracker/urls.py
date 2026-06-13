from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import CategoryViewSet, TransactionViewSet, SummaryView, MonthlySummaryView, RegisterView, ProfileView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/profile', ProfileView.as_view(), name='profile'),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('summary/monthly', MonthlySummaryView.as_view(), name='summary-monthly'),
    path('summary/by-category', CategoryViewSet.as_view(), name='summary-by-category'),
]