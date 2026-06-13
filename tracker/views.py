from django.db.models import Sum, Q
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .pagination import TransactionCursorPagination
from django.db.models.functions import TruncMonth

from tracker.models import Category, Transaction
from tracker.serializers import UserSerializer, RegisterSerializer, CategorySerializer, TransactionSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["date", "amount", "created_at"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('category').order_by('-date')

    def get_serializer_class(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        transactions = Transaction.objects.filter(user=self.request.user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lt=end_date)

        totals = transactions.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expense=Sum('amount', filter=Q(type='expense'))
        )

        total_income = totals['total_income'] or 0.0
        total_expense = totals['total_expense'] or 0.0
        net_balance = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'filters_applied': {
                'start_date': start_date,
                'end_date': end_date,
            }
        })

class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        transactions = Transaction.objects.filter(user=self.request.user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lt=end_date)

        monthly = (transactions.annotate(month=TruncMonth('date')).values('month').annotate(
            income=Sum('amount', filter=Q(type='income')),
            expense=Sum('amount', filter=Q(type='expense'))
        ).order_by('-month'))

        data = [{
            'month': entry['month'].strftime('%Y-%m'),
            'income': entry['income'] or 0,
            'expenses': entry['expenses'] or 0,
            'net': (entry['income'] or 0) - (entry['expenses'] or 0),
        } for entry in monthly ]
        return Response(data)

class CategorySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=self.request.user)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lt=end_date)

        by_category = transactions.values('category__name', 'type').annotate(total=Sum('amount')).order_by('-total')

        data = [{
            'category': entry['category__name'] or 'Uncategorized',
            'type': entry['type'],
            'total': entry['total'] or 0,
        } for entry in by_category ]