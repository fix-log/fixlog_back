from django.urls import path
from . import views

urlpatterns = [
    path("projects/", views.ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", views.ProjectDetailAPIView.as_view(), name="project-detail"),
    path("projects/<int:pk>/update/", views.ProjectUpdateAPIView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteAPIView.as_view(), name="project-delete"),
    path("projects/<int:project_id>/apply/", views.ProjectApplyAPIView.as_view(), name="project-apply"),
    path("projects/<int:project_id>/applicants/", views.ProjectApplicantsAPIView.as_view(), name="project-applicants"),
]
