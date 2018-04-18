# vim: set fileencoding=utf-8 :
from django.contrib import admin

from . import models

admin.site.site_header = 'Achieve Administration'


class QuarterAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'name', 'start_date', 'end_date')
    list_filter = ('created', 'start_date', 'end_date')
    search_fields = ('name',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'name')
    list_filter = ('created',)
    search_fields = ('name',)


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'team', 'manager')
    list_filter = ('created', 'team', 'manager')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'slug',
        'last_updated',
        'email',
        'coins',
        'gems',
        'karma',
        'energy',
        'xp',
        'rights',
        'user',
        'team',
    )
    list_filter = ('created', 'last_updated', 'user', 'team')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'key',
        'priority',
        'status',
        'summary',
        'type',
        'story_points',
        'user',
    )
    list_filter = ('created', 'status', 'user')


class GlobalObjectiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'objective', 'quarter', 'user')
    list_filter = ('created', 'quarter', 'user')


class GlobalKeyResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'objective', 'key_result', 'percentage')
    list_filter = ('created', 'objective')


class ObjectiveAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'global_key_result',
        'user',
        'objective',
        'percentage',
    )
    list_filter = ('created', 'global_key_result', 'user')


class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'objective',
        'result',
        'manual_bar',
        'percentage',
    )
    list_filter = ('created', 'objective', 'manual_bar')
    raw_id_fields = ('jira_issues',)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'public', 'type', 'user', 'data')
    list_filter = ('created', 'public', 'user')


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.Quarter, QuarterAdmin)
_register(models.Team, TeamAdmin)
_register(models.Manager, ManagerAdmin)
_register(models.Profile, ProfileAdmin)
_register(models.Issue, IssueAdmin)
_register(models.GlobalObjective, GlobalObjectiveAdmin)
_register(models.GlobalKeyResult, GlobalKeyResultAdmin)
_register(models.Objective, ObjectiveAdmin)
_register(models.Result, ResultAdmin)
_register(models.Activity, ActivityAdmin)
