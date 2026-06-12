from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User as UserModel, Category, Transaction
from django.core.exceptions import ValidationError as DjangoValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'email', 'first_name', 'last_name')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'confirm_password')

    def validate_email(self, email):
        if UserModel.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already registered')
        return email

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return password

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': 'Password does not match'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return UserModel.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name', ''),
        )

class CategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Category
        fields = ('id', 'name', 'type', 'created_at')
        read_only_fields = ('id', 'created_at')

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'id',
            'category',
            'category_name',
            'amount',
            'type',
            'description',
            'date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def validate_amount(self, amount):
        if amount < 0:
            raise serializers.ValidationError('Amount must be greater than 0')
        return amount

    def validate_category(self, category):
        request = self.context.get('request')
        if category and category.user != request.user:
            raise serializers.ValidationError('Category can not be changed')
        return category