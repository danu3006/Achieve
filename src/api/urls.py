from django.urls import path, include
from rest_framework import routers

from . import api

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'global/objectives', api.GlobalObjectiveViewSet)
router.register(r'global/keyresults', api.GlobalKeyResultViewSet)
router.register(r'objectives', api.ObjectiveViewSet)
router.register(r'keyresults', api.KeyResultViewSet)
router.register(r'teams', api.TeamViewSet)
router.register(r'managers', api.ManagerViewSet)

urlpatterns = [

    # API
    path('', include(router.urls), name='index'),

    # team-detail.html
    path('team/<int:team_id>/add/<str:username>/', api.UserTeamAdd.as_view(), name='team-user-add'),

]
