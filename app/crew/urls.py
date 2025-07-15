from django.urls import path
from app.crew import views

urlpatterns = [
    path("projects/", views.ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", views.ProjectDetailAPIView.as_view(), name="project-detail"),
    path("projects/<int:pk>/update/", views.ProjectUpdateAPIView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteAPIView.as_view(), name="project-delete"),
    # 북마크 관련 URL
    path("projects/<int:project_id>/bookmark", views.bookmark_manage, name="bookmark-manage"),
]
