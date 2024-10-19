from django.urls import path
from .views import StockListCreate, StockListDelete

urlpatterns=[
    path('stocklist/',StockListCreate.as_view(),name='stock-list'),
    path('stock/delete/<int:pk>/',StockListDelete.as_view(),name='stock-delete'),
]