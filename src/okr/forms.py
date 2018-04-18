import datetime

from django import forms

from .context_processors import get_current_quarter
from .models import Objective, GlobalKeyResult, Result, Profile, Manager, GlobalObjective, Issue


class ObjectiveFormCurrent(forms.ModelForm):
    class Meta:
        model = Objective
        fields = ('global_key_result', 'objective')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # check user's team. find manager. get managers gobalobjectives. get managers global keyresults
        users_team = Profile.objects.get(user=self.user).team
        manager = Manager.objects.get(team=users_team).manager
        global_obj_s = GlobalObjective.objects.filter(user=manager, created__year=datetime.datetime.now().year,
                                                      quarter=get_current_quarter())
        queryset = None

        for g_obj in global_obj_s:
            if queryset:
                queryset = GlobalKeyResult.objects.filter(objective=g_obj) | queryset
            else:
                queryset = GlobalKeyResult.objects.filter(objective=g_obj)

        self.fields['global_key_result'].queryset = queryset


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ('objective', 'result', 'manual_bar', 'jira_issues')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.objective = kwargs.pop('objective', None)
        super().__init__(*args, **kwargs)
        queryset = Objective.objects.filter(user=self.user)
        self.fields['objective'].queryset = queryset
        self.initial['objective'] = self.objective.id
        self.fields['jira_issues'].queryset = Issue.objects.filter(user=self.user)
