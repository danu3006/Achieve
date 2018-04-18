from rest_framework import serializers

from okr.models import *


class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='okr:user-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class GlobalObjectiveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='okr:globalobjective-detail')

    class Meta:
        model = GlobalObjective
        fields = ('url', 'created', 'quarter', 'objective')


class GlobalKeyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalKeyResult
        fields = ('created', 'objective', 'key_result')


class ObjectiveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='okr:objective-detail')

    class Meta:
        model = Objective
        fields = ('url', 'created', 'objective', 'global_key_result', 'user', 'percentage')


class KeyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('created', 'objective', 'result', 'percentage')


class TeamSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='okr:team-detail')

    class Meta:
        model = Team
        fields = ('url', 'created', 'name')


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('created', 'team', 'manager')


class IssueSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Issue
        fields = ('id', 'key', 'priority', 'status', 'summary', 'type', 'story_points', 'user')
