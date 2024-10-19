from rest_framework import serializers
from .models import User, StockList, CustomUserManager
from rest_framework.response import Response
from .email_utils import send_mail
from datetime import date
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name','last_name','username','email','password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError('Invalid email address')
        if User.objects.filter(email=value).exists():
           raise serializers.ValidationError('Email already exists')
        return value
    
    def validate_password(self, value):
        if len(value)<8 :
            raise serializers.ValidationError('Password must be at least 8 characters')
        return value
    
    def validate_username(self, value):
        if not value or len(value)<3:
            raise serializers.ValidationError('Username must be at least 3 characters')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
    def create(self, validated_data):
        print("validated this: ",validated_data)
        user=User.objects.create_user(**validated_data)

        token=send_mail(user, 'Verify email for Stonky')
        user.email_verified_hash = token
        user.save()

        return user
        
class StockListSerializer(serializers.ModelSerializer):
    class Meta:
        model=StockList
        fields=['id','stock_name','stock_ticker','stock_sector', 'stock_industry','created_at','stock_market','stock_description', 'author',]
        extra_kwargs={
            "author":{"read_only":True},
            "stock_description": {'required': False},
            "stock_market": {'required': False},
            }

        def validate_stock_ticker(self, value):
            if not value:
                raise serializers.ValidationError('Stock ticker is required')
            if StockList.objects.filter(stock_ticker=value).exists():
                raise serializers.ValidationError('Stock already added')
            return value 
def custom_json_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO format
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')