from typing import Any
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
 

class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, email_verified_hash='', **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        if not username:
            raise ValueError("Username must be set")
        if not password:
            raise ValueError("Password must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, email_verified_hash=email_verified_hash, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, username=None, password=None, email_verified_hash='', **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('email_verified', False)
        return self._create_user(username, email, password, email_verified_hash, **extra_fields)

    def create_superuser(self, email=None, username=None, password=None, email_verified_hash='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verified', True)
        return self._create_user(username, email, password, email_verified_hash, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, blank=True, default='', unique=True)
    email=models.EmailField(blank=True, max_length=255, default='', unique=True)
    first_name=models.CharField(max_length=255, blank=True,default='')
    last_name=models.CharField(max_length=255, blank=True,default='')
    

    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)

    email_verified=models.BooleanField(default=False)
    email_verified_hash=models.CharField(max_length=255, blank=True, default='')

    date_joined=models.DateTimeField(default=timezone.now)

    last_login=models.DateTimeField(blank=True, null=True)  

    objects= CustomUserManager()

    USERNAME_FIELD='email'
    EMAIL_FIELD='email'
    REQUIRED_FIELDS=['username','first_name', 'last_name']

    class Meta:
        verbose_name='User'
        verbose_name_plural='Users'
    
    def get_full_name(self):
        return self.first_name+' '+self.last_name 
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

class StockList(models.Model):
    stock_name=models.CharField(max_length=100)  
    stock_ticker=models.CharField(max_length=100)  
    stock_industry=models.CharField(max_length=100)
    stock_sector=models.CharField(max_length=100)
    stock_market=models.CharField(max_length=100)
    stock_description=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey(User, on_delete=models.CASCADE, related_name='stocks')

    def __str__(self):
        return self.stock_name


