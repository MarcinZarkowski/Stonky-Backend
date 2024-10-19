from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from .models import User, StockList
from .serializers import UserSerializer, StockListSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .email_utils import send_mail
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from rest_framework.decorators import api_view, permission_classes
import environ
import requests
import yfinance as yf
from .technical_indicators import *
from sklearn.preprocessing import MinMaxScaler
from .ML_models import load_1day_model
from datetime import datetime, timedelta
import json
from .get_stock_data import *

from .serializers import custom_json_serializer
from django.conf import settings
import threading

def start_chat(stock):
    url = settings.API_URL
    payload = {
        "stock": stock,
        "key": settings.KEY,
    }

    def post_request():
        try:
            if not url or not payload["key"]:
                print("Missing URL or API key")
                return
            
            print(f'Sending request to: {url}/start-chat with payload: {payload}')
            response = requests.post(f'{url}/start-chat', json=payload)
            response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx, 5xx)
            print(f'Response received: {response.status_code}')
            
        except requests.exceptions.RequestException as e:
            print(f"Error during POST request: {e}")

    # Start a new thread to run the post_request function
    thread = threading.Thread(target=post_request)
    thread.start()


@api_view(['POST'])
def chat_with_RAG(request):
    data = json.loads(request.body.decode('utf-8'))
    url=settings.API_URL
    payload={
       "prompt":data.get('query'),
        "ticker":data.get('ticker'),
        "key":settings.KEY,
    }
    try:
        response=requests.post(f'{url}/ask', json=payload )
        
        response=response.json()
        print(response.get("message"))
        print(len(response))
        return Response(response)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return JsonResponse({'status': 'failed', 'error': 'Error occured.'})



    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stock_pred(request, ticker):
    # Run start_chat asynchronously
    start_chat(ticker)
    
    stock_ticker = yf.Ticker(ticker)
    stock = stock_ticker.history(period='max')

    if len(stock) == 0:
        return JsonResponse({'status': 'failed', 'message': 'API error occurred or Ticker not found.'})
    if len(stock) < 60: 
        return JsonResponse({'status': 'failed', 'message': 'Not enough data available.'})
   
    # Feature scaling and stock indicator calculations
    scaler = MinMaxScaler()
    stock = MA_Bollinger(stock, 20)
    stock = ROC(stock)
    stock = MACD(stock)
    stock = Stochastic_Oscillator(stock)
    stock = ATR(stock)
    stock = OBV(stock)
    stock = RSI(stock)

    stock = stock.dropna()

    index_dates = [stock.index[i].strftime('%Y-%m-%d') for i in range(60, stock.shape[0])]

    stock = scaler.fit_transform(stock)

    # Prepare dataset for prediction
    data_set = []
    actual_val = []
    for i in range(60, stock.shape[0]):
        data_set.append(stock[i - 60:i])
        actual_val.append(stock[i][0])

    last_60_days = [stock[(len(stock)) - 60:len(stock)]]
    data_set = np.array(data_set)
    actual_val = np.array(actual_val)
    last_60_days = np.array(last_60_days)

    if data_set.shape[0] != actual_val.shape[0] or data_set.shape[1] != 60 or data_set.shape[2] != 18:
        return JsonResponse({'status': 'failed', 'message': 'Data processing error.'})

    # Load model and predict
    model = load_1day_model()
    predicted = model.predict(data_set)
    next_day_prediction = model.predict(last_60_days)

    scale = 1 / scaler.scale_[0]

    predicted = predicted * scale
    actual_val = actual_val * scale
    next_day_prediction = next_day_prediction * scale

    average_deviance = np.mean(np.abs(predicted - actual_val))

    prediction_results = [
        {"time": index_dates[i], "value": float(predicted[i][0])}
        for i in range(len(predicted))
    ]
    actual_results = [
        {"time": index_dates[i], "value": float(actual_val[i])}
        for i in range(len(actual_val))
    ]

    today = datetime.now()
    next_day = today + timedelta(days=1)
    next_day_prediction = {
        "time": next_day.strftime('%Y-%m-%d'), 
        "value": float(next_day_prediction[0][0])
    }

    response = {
        "predictions": prediction_results,
        "actuals": actual_results,
        "next_day_prediction": next_day_prediction,
        "average_deviance": average_deviance
    }

    return JsonResponse(response)
    
@csrf_protect
@ensure_csrf_cookie
def change_password(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'failed', 'message': 'Method not allowed'}, status=405)
    
    token = request.GET.get('token')
    try:
        # Parse JSON body
        data = json.loads(request.body)
        password = data.get('password')

        if not password:
            return JsonResponse({'status': 'failed', 'message': 'Password is required'}, status=400)

        user = User.objects.get(email_verified_hash=token, email_verified=True)
        user.set_password(password)
        user.email_verified_hash = ""
        user.save()

        return JsonResponse({'status': 'success', 'message': 'Password changed successfully'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Invalid token, your password was already changed.'}, status=400)
    
@ensure_csrf_cookie    
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


def validate_reset_request(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'failed', 'message': 'Method not allowed'}, status=405)

    email= request.GET.get('email')
    if not email:
        return JsonResponse({'status': 'failed', 'message': 'Email not provided'}, status=400)
    else:
        if '@' not in email:
            return JsonResponse({'status': 'failed', 'message': 'Invalid email address'}, status=400)
        try:
            user = User.objects.get(email=email)
            token=send_mail(user,'Stonky password reset' )
            user.email_verified_hash = token
            user.save()
            return JsonResponse({'status':'success', 'message': 'Check your inbox for instructions'})

        except User.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Email/User not found'}, status=400)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stock(request, query):
    print(f"Received query: {query}") 

    user=request.user
    if not query or not user:
        return JsonResponse({'status': 'failed', 'message': 'Invalid request'}, status=400)
     
    arr1=StockList.objects.filter(author=user, stock_name__icontains=query)
    arr2=StockList.objects.filter(author=user, stock_ticker__icontains=query)
    longer=arr1 if len(arr1) > len(arr2) else arr2
    
    
    serialized=StockListSerializer(longer, many=True)
    print(serialized.data)
    
    return  Response(serialized.data)

def validate_email_token(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'failed', 'message': 'Method not allowed'}, status=405)
    
    token = request.GET.get('token')
    
    if not token:
        return JsonResponse({'status': 'failed', 'message': 'Token not provided'}, status=400)
    
    try:
        user = User.objects.get(email_verified_hash=token, email_verified=False)
        user.email_verified = True
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Email verified successfully'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Invalid or expired token'}, status=400)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

     

        email = request.data.get('email')  
        password = request.data.get('password')
        print(email, password)

        if not email or '@' not in email:
            return Response({'detail': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            return Response({'detail': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=email, password=password)
        
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.email_verified:
            user.delete()
            return Response(
                {'detail': 'Email was not verified. Account has been deleted. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = super().post(request, *args, **kwargs)
        return response

class StockListCreate(generics.ListCreateAPIView):
    serializer_class = StockListSerializer
    permission_classes=[IsAuthenticated]
  
    def get_queryset(self):
        user = self.request.user
        return StockList.objects.filter(author=user)

    def perform_create(self, serializer):
        def get_market(ticker):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Check if 'exchange' key is available in the info dictionary
                exchange = info.get('exchange', 'Unknown')

                if 'NYSE' in exchange:
                    return 'NYSE'
                elif 'NASDAQ' in exchange:
                    return 'NASDAQ'
                elif 'AMEX' in exchange:
                    return 'AMEX'
                else:
                    return 'Other'
            except Exception as e:
                print(f"Error: {e}")
                return 'Error'
            
        user = self.request.user
        stock_name = serializer.validated_data['stock_name']
        stock_ticker = serializer.validated_data['stock_ticker']

        # Check if the stock already exists in the user's list
        if StockList.objects.filter(author=user, stock_name=stock_name, stock_ticker=stock_ticker).exists():
            return JsonResponse({'status': 'failed', 'message': 'Stock is already in your list.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch additional stock information
        stock_info = yf.Ticker(stock_ticker)
        stock_description = stock_info.info.get('longBusinessSummary', 'Description not available')
    
        stock_market = stock_info.info.get('exchange', 'Market information not available')
        market_mapping = {
            "NYQ": "NYSE",
            "NGM": "NASDAQ",
            "NMS": "NASDAQ"
        }

        if stock_market in market_mapping:
            stock_market = market_mapping.get(stock_market)
        else:
            print(f"Unknown market: {stock_market}")
            stock_market = get_market(stock_ticker)
            print(f"Unknown market: {stock_market}")
        

        # Save the stock with additional information
        serializer.save(
            author=user,
            stock_description=stock_description,
            stock_market=stock_market
        )


class StockListDelete(generics.DestroyAPIView):
    
    serializer_class=StockListSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        user=self.request.user
        return StockList.objects.filter(author=user)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]





