from django.urls import path
from app.util import views

urlpatterns = [
    # Position 관련 URL
    path('positions/', views.PositionListView.as_view(), name='position-list'),  # 목록 및 생성
    path('positions/<int:pk>/', views.PositionDetailView.as_view(), name='position-detail'),  # 조회, 수정(PATCH), 삭제

    # Language 관련 URL
    path('languages/', views.LanguageListView.as_view(), name='language-list'),  # 목록 및 생성
    path('languages/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),  # 조회, 수정(PATCH), 삭제

    # Stack 관련 URL
    path('stacks/', views.StackListView.as_view(), name='stack-list'),  # 목록 및 생성
    path('stacks/<int:pk>/', views.StackDetailView.as_view(), name='stack-detail'),  # 조회, 수정(PATCH), 삭제

    # Design 관련 URL
    path('designs/', views.DesignListView.as_view(), name='design-list'),  # 목록 및 생성
    path('designs/<int:pk>/', views.DesignDetailView.as_view(), name='design-detail'),  # 조회, 수정(PATCH), 삭제
]