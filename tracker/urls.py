from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import CategoryViewSet, TransactionViewSet, SummaryView, MonthlySummaryView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('summary/monthly', MonthlySummaryView.as_view(), name='summary-monthly'),
    path('summary/by-category', CategoryViewSet.as_view(), name='summary-by-category'),
]