from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from FinanceTrackerAPI.settings import AUTH_USER_MODEL


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    username = None
    first_name = models.CharField(max_length=50, null=True, blank=True, unique=False)
    last_name = models.CharField(max_length=50, null=True, blank=True, unique=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Category(models.Model):
    TYPE_CHOICES = {
        '1': 'income',
        '2': 'expense',
    }
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'name')
