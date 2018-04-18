from django.urls import path

from . import progress
from . import views

app_name = 'okr'

urlpatterns = [

    # Singular Paths
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('test/', views.TestView.as_view(), name='test'),
    path('poker/', views.PokerView.as_view(), name='poker'),
    path('how-to/', views.GuideView.as_view(), name='guide'),
    path('progress/<int:kr_id>/type/<str:type>/', progress.update_progress, name='progress'),

    # Global Objective
    path('global/objective/add/', views.GlobalObjectiveCreate.as_view(), name='globalobjective-add'),
    path('global/objective/list/', views.GlobalObjectiveList.as_view(), name='globalobjective-list'),
    path('global/objective/<int:pk>/detail/', views.GlobalObjectiveDetail.as_view(), name='globalobjective-detail'),
    path('global/objective/<int:pk>/', views.GlobalObjectiveUpdate.as_view(), name='globalobjective-update'),
    path('global/objective/<int:pk>/delete/', views.GlobalObjectiveDelete.as_view(), name='globalobjective-delete'),

    # Global Key Result
    path('global/objective/<int:gobj_id>/result/add/', views.GlobalKeyResultCreate.as_view(),
         name='globalkeyresult-add'),
    path('global/objective/result/<int:pk>/', views.GlobalKeyResultUpdate.as_view(), name='globalkeyresult-update'),
    path('global/objective/result/<int:pk>/delete/', views.GlobalKeyResultDelete.as_view(),
         name='globalkeyresult-delete'),

    # Objective
    path('objective/add/', views.ObjectiveCreate.as_view(), name='objective-add'),
    path('objective/list/', views.ObjectiveList.as_view(), name='objective-list'),
    path('objective/<int:pk>/detail/', views.ObjectiveDetail.as_view(), name='objective-detail'),
    path('objective/<int:pk>/', views.ObjectiveUpdate.as_view(), name='objective-update'),
    path('objective/<int:pk>/delete/', views.ObjectiveDelete.as_view(), name='objective-delete'),

    # Key Result
    path('objective/<int:objective_id>/result/add/', views.KeyResultCreate.as_view(), name='keyresult-add'),
    path('objective/result/<int:pk>/', views.KeyResultUpdate.as_view(), name='keyresult-update'),
    path('objective/result/<int:pk>/delete/', views.KeyResultDelete.as_view(), name='keyresult-delete'),

    # Team
    path('team/add/', views.TeamCreate.as_view(), name='team-add'),
    path('team/list/', views.TeamList.as_view(), name='team-list'),
    path('team/<int:pk>/detail/', views.TeamDetail.as_view(), name='team-detail'),
    path('team/<int:pk>/', views.TeamUpdate.as_view(), name='team-update'),
    path('team/<int:pk>/delete/', views.TeamDelete.as_view(), name='team-delete'),

    # User
    path('user/<int:pk>/detail/', views.TeamDetail.as_view(), name='user-detail'),
    path('user/<int:pk>/', views.TeamUpdate.as_view(), name='user-update'),

    # Issue
    path('issue/list/', views.IssueList.as_view(), name='issue-list'),
    path('issue/add/', views.IssueCreate.as_view(), name='issue-add'),
    path('issue/<int:pk>/detail/', views.IssueDetail.as_view(), name='issue-detail'),
    path('issue/<int:pk>/delete/', views.IssueDelete.as_view(), name='issue-delete'),

    # Reports
    path('reports/', views.ReportView.as_view(), name='report'),
    path('reports/GRST/<int:pk>/', views.ReportGlobalKeyResultDetail.as_view(), name='report-gkr-detail'),
    path('reports/user/<int:pk>/', views.ReportUserDetail.as_view(), name='report-user-detail'),

]
