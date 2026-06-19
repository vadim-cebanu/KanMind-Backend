from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskCreateView.as_view(), name='task-create'),
    path('tasks/assigned-to-me/', views.TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', views.TasksReviewingView.as_view(), name='tasks-reviewing'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', views.CommentDeleteView.as_view(), name='comment-delete'),
]

