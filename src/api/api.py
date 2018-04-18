from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class UserViewSet(viewsets.ModelViewSet):
    """ List all Users """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class GlobalObjectiveViewSet(viewsets.ModelViewSet):
    queryset = GlobalObjective.objects.all()
    serializer_class = GlobalObjectiveSerializer


class GlobalKeyResultViewSet(viewsets.ModelViewSet):
    queryset = GlobalKeyResult.objects.all()
    serializer_class = GlobalKeyResultSerializer


class ObjectiveViewSet(viewsets.ModelViewSet):
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer


class KeyResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = KeyResultSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


class UserTeamAdd(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, team_id, username, format=None):
        user = self.get_object(username=username)
        team_object = Team.objects.get(id=team_id)
        if user.profile.team != team_object:
            user.profile.team = team_object
        user.save()

        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @api_view(['DELETE'])
    def delete(self, request, team_id, username, format=None):
        user = self.get_object(username=username)
        user.profile.team = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
