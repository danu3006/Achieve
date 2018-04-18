from braces.views import LoginRequiredMixin, UserPassesTestMixin, AnonymousRequiredMixin
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, RedirectView, TemplateView,
                                  UpdateView)

from .context_processors import get_current_quarter
from .cron import update_percentages
from .forms import ObjectiveFormCurrent, ResultForm
from .models import (GlobalKeyResult, GlobalObjective, Objective, Result, Team,
                     User, Manager, Issue, Poker)
from .permissions import is_manager_or_staff, is_manager_of_team_or_staff, is_owner_of_objective, \
    is_owner_of_key_result, is_owner_of_issue


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'okr/includes/index.html'
    login_url = reverse_lazy('okr:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.profile.team:
                return redirect('okr:objective-list')
            else:
                return redirect('okr:welcome')
        else:
            return redirect('okr:login')


class TestView(TemplateView):
    template_name = 'okr/includes/index.html'
    login_url = reverse_lazy('okr:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            update_percentages()
        return super().dispatch(request, *args, **kwargs)


class WelcomeView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = 'okr/includes/welcome.html'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return False if user.profile.team else True

    def post(self, request):
        is_manager = request.POST.get('is_manager')
        if request.POST.get('team_on_list') == 'negative':
            team_name = request.POST.get('team_name')
        else:
            team_name = request.POST.get('team_on_list')

        team, created = Team.objects.get_or_create(name=team_name)
        request.user.profile.team = team
        request.user.profile.save()
        if is_manager == 'true':
            manager, created_manager = Manager.objects.get_or_create(
                manager=request.user, team=team)

        return redirect('okr:index')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'all_teams': Team.objects.all(),
        })

        return context


class LoginView(AnonymousRequiredMixin, FormView):
    template_name = 'okr/includes/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('okr:index')
    authenticated_redirect_url = reverse_lazy('okr:index')
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
        })

        return context

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.success_url

        if self.request.user.profile.is_manager():
            redirect_to = reverse_lazy('okr:team-list')

        return redirect_to


class LogoutView(RedirectView):
    url = reverse_lazy('okr:index')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class GlobalObjectiveCreate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/globalobjective_create.html'
    model = GlobalObjective

    fields = ['objective', 'quarter']
    success_message = 'Global Objective successfully added.'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_or_staff(user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('okr:globalobjective-list')


class GlobalObjectiveList(LoginRequiredMixin, ListView):
    template_name = 'okr/includes/globalobjective_list.html'
    model = GlobalObjective
    login_url = reverse_lazy('okr:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        years = [2018, 2017]
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        context.update({
            'years': years,
            'quarters': quarters,
            'object_list': GlobalObjective.objects.filter(user=self.request.user)
        })
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.team:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('okr:welcome')


class GlobalObjectiveDetail(LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/globalobjective_detail.html'
    model = GlobalObjective
    login_url = reverse_lazy('okr:login')


class GlobalObjectiveUpdate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'okr/includes/globalobjective_update.html'
    model = GlobalObjective
    fields = ['objective', 'quarter']
    success_message = 'Global Objective successfully updated.'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object().user.profile.team)

    def get_success_url(self, **kwargs):
        return reverse_lazy('okr:globalobjective-detail', args=(self.object.id,))


class GlobalObjectiveDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/globalobjective_confirm_delete.html'
    model = GlobalObjective
    success_url = reverse_lazy('okr:globalobjective-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object().user.profile.team)


class GlobalKeyResultCreate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/globalkeyresult_create.html'
    model = GlobalKeyResult
    fields = ['objective', 'key_result']
    success_message = 'Global Key Result successfully added.'
    login_url = reverse_lazy('okr:login')
    global_objective = None
    object = None

    def test_func(self, user):
        return is_manager_or_staff(user)

    def dispatch(self, request, *args, **kwargs):
        self.global_objective = get_object_or_404(
            GlobalObjective, pk=self.kwargs['gobj_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'global_objective': self.global_objective,
        })
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.initial['objective'] = self.global_objective.pk
        return form

    def form_valid(self, form):
        self.object = form
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('okr:globalobjective-detail', kwargs={'pk': self.object.objective.id})


class GlobalKeyResultUpdate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'okr/includes/globalkeyresult_update.html'
    model = GlobalKeyResult
    fields = ['key_result']
    success_message = 'Global Key Result successfully updated.'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object().objective.user.profile.team)

    def get_success_url(self, **kwargs):
        return reverse_lazy('okr:globalobjective-detail', args=(self.object.objective.id,))


class GlobalKeyResultDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/globalkeyresult_confirm_delete.html'
    model = GlobalKeyResult
    success_url = reverse_lazy('okr:globalobjective-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object().objective.user.profile.team)


class ObjectiveCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/objective_create.html'
    form_class = ObjectiveFormCurrent
    model = Objective
    success_message = 'Objective successfully added.'
    login_url = reverse_lazy('okr:login')
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('okr:objective-detail', kwargs={'pk': self.object.id})


class ObjectiveList(LoginRequiredMixin, ListView):
    template_name = 'okr/includes/objective_list.html'
    model = Objective
    login_url = reverse_lazy('okr:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_list_incomplete': Objective.objects.filter(user=self.request.user, percentage__lt=100),
            'object_list_complete': Objective.objects.filter(user=self.request.user, percentage=100),
            'incomplete_percentage': 100 - self.request.user.profile.get_percentage(),
        })
        return context


class ObjectiveDetail(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/objective_detail.html'
    model = Objective
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_objective(user, self.get_object())


class ObjectiveUpdate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'okr/includes/objective_update.html'
    model = Objective
    form_class = ObjectiveFormCurrent
    success_message = 'Objective successfully updated.'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_objective(user, self.get_object())

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('okr:objective-detail', args=(self.object.id,))


class ObjectiveDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/objective_confirm_delete.html'
    model = Objective
    success_url = reverse_lazy('okr:objective-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_objective(user, self.get_object())


class KeyResultCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/keyresult_create.html'
    success_message = 'Key Result successfully added.'
    login_url = reverse_lazy('okr:login')
    form_class = ResultForm
    object = None
    objective = None

    def dispatch(self, request, *args, **kwargs):
        self.objective = get_object_or_404(
            Objective, pk=kwargs['objective_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'objective': self.objective,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'objective': self.objective,
        })
        return kwargs

    def form_valid(self, form):
        self.object = form
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.POST.get('manual_bar') and request.POST.get('jira_issues'):
            messages.error(
                request, 'ERROR: You cannot select both manual progress bar and JIRA issue(s).')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not request.POST.get('manual_bar') and not request.POST.get('jira_issues'):
            messages.error(
                request, 'ERROR: You MUST select either a manual progress bar or a JIRA issue(s).')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('okr:objective-detail', kwargs={'pk': self.object.objective.id})


class KeyResultUpdate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'okr/includes/keyresult_update.html'
    model = Result
    fields = ['result', 'manual_bar', 'jira_issues']
    success_message = 'Key Result successfully updated.'
    login_url = reverse_lazy('okr:login')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['jira_issues'].queryset = Issue.objects.filter(
            user=self.request.user)
        return form

    def test_func(self, user):
        return is_owner_of_key_result(user, self.get_object())

    def post(self, request, *args, **kwargs):
        if request.POST.get('manual_bar') and request.POST.get('jira_issues'):
            messages.error(
                request, 'ERROR: You cannot select both manual progress bar and JIRA issue(s).')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not request.POST.get('manual_bar') and not request.POST.get('jira_issues'):
            messages.error(
                request, 'ERROR: You MUST select either a manual progress bar or a JIRA issue(s).')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        return super().post(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy('okr:objective-detail', args=(self.object.objective.id,))


class KeyResultDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/keyresult_confirm_delete.html'
    model = Result
    success_url = reverse_lazy('okr:objective-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_key_result(user, self.get_object())


class TeamCreate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/team_create.html'
    model = Team
    fields = ['name']
    success_message = 'Team successfully added.'
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_or_staff(user)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('okr:team-list')


class TeamList(UserPassesTestMixin, LoginRequiredMixin, ListView):
    template_name = 'okr/includes/team_list.html'
    model = Team
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_or_staff(user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = []
        for team in Team.objects.all():
            if not self.request.user.profile.is_manager_of(team):
                teams.append(team)

        context.update({
            'object_list': teams
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        # messages.success(request, 'Server was added successfully.')
        return super().dispatch(request, *args, **kwargs)


class TeamDetail(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/team_detail.html'
    model = Team
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': User.objects.filter(is_staff=False)
        })
        return context


class TeamUpdate(UserPassesTestMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'okr/includes/team_update.html'
    model = Team
    fields = ['name']
    success_message = 'Team successfully updated.'
    login_url = reverse_lazy('okr:login')
    redirect_unauthenticated_users = reverse_lazy('okr:index')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object())

    def get_success_url(self, **kwargs):
        return reverse_lazy('okr:team-detail', args=(self.object.id,))


class TeamDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/team_confirm_delete.html'
    model = Team
    success_url = reverse_lazy('okr:team-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_manager_of_team_or_staff(user, self.get_object())


class GuideView(LoginRequiredMixin, TemplateView):
    template_name = 'okr/includes/guide.html'
    login_url = reverse_lazy('okr:login')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class IssueCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'okr/includes/issue_create.html'
    model = Issue
    fields = ['key']
    success_message = 'Issue successfully added.'
    login_url = reverse_lazy('okr:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issues = [issue.key for issue in Issue.objects.all()]
        context.update({
            'issues': ','.join(issues),
        })
        return context

    def form_valid(self, form):
        if not form.instance.key.startswith('SUM-'):
            form.instance.key = 'SUM-' + form.instance.key

        # if Issue.objects.get(key=form.instance.key) in Issue.objects.all():
        #     messages.error(self.request, 'Issue already exists!')
        #     return self.get_success_url()

        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('okr:issue-add')


class IssueList(LoginRequiredMixin, ListView):
    template_name = 'okr/includes/issue_list.html'
    model = Issue
    login_url = reverse_lazy('okr:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_list_complete': Issue.objects.filter(user=self.request.user, status=True),
            'object_list_incomplete': Issue.objects.filter(user=self.request.user, status=False),
        })
        return context


class IssueDetail(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/issue_detail.html'
    model = Issue
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_issue(user, self.get_object())


class IssueDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    template_name = 'okr/includes/issue_confirm_delete.html'
    model = Issue
    success_url = reverse_lazy('okr:issue-list')
    login_url = reverse_lazy('okr:login')

    def test_func(self, user):
        return is_owner_of_issue(user, self.get_object())


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'okr/includes/report.html'
    login_url = reverse_lazy('okr:login')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'global_objectives': GlobalObjective.objects.filter(
                user=self.request.user.profile.team.get_manager().manager,
                quarter=get_current_quarter()
            )
        })
        return context


class ReportGlobalKeyResultDetail(LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/report_globalkr_detail.html'
    login_url = reverse_lazy('okr:login')
    model = GlobalKeyResult

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = []
        for objective in Objective.objects.filter(user__profile__team=self.request.user.profile.team):
            if objective.global_key_result.id == self.get_object().id:
                if objective.user not in users:
                    users.append(objective.user)
        context.update({
            'users': users,
            'objectives': Objective.objects.filter(user__profile__team=self.request.user.profile.team)
        })
        return context


class ReportUserDetail(LoginRequiredMixin, DetailView):
    template_name = 'okr/includes/report_user_detail.html'
    login_url = reverse_lazy('okr:login')
    model = User

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = []
        for objective in Objective.objects.filter(user__profile__team=self.request.user.profile.team):
            if objective.global_key_result.id == self.get_object().id:
                if objective.user not in users:
                    users.append(objective.user)
        context.update({
            'users': users,
            'objectives': Objective.objects.filter(user__profile__team=self.request.user.profile.team)
        })
        return context


# def pokers(request):
#     return render_to_response('okr/includes/poker.html', {'poker': Poker.objects.all()})
#
#
# def poker(request, poker_id=1):
#     return render_to_response('okr/includes/poker.html', {'poker': Poker.objects.get(id=poker_id)})


class PokerView(LoginRequiredMixin, TemplateView):
    template_name = 'okr/includes/poker.html'
    model = Poker
    fields = ['name', 'cardpicked', 'story', 'message', 'user']
    success_message = 'Great.'
    login_url = reverse_lazy('okr:login')

    def post(self, request):
        p = request.POST
        print(request)
        Poker.objects.create(
            name=p['username'], cardpicked=p['cardpicked'], story=p['storyname'], message=p['message'])
        return render(request, 'okr/includes/poker.html')

    def get(self, request):
        data = Poker.objects.all()
        print(data)
        return TemplateResponse(request, 'okr/includes/poker.html', {"data": data})

    # def poker_update_result(self):
    #     obj = Poker.objects.create(val=1)
    #     Poker.objects.filter(pk=obj.pk).update(val=F('val') + 1)
    #     # At this point obj.val is still 1, but the value in the database
    #     # was updated to 2. The object's updated value needs to be reloaded
    #     # from the database.
    #     obj.refresh_from_db()
    #     self.assertEqual(obj.val, 2)

    # def get(self, request):
    #     # g = request.GET
    #     # Poker.objects.filter(name="Pedro")
    #     # print(request)
    #     message = not Poker.objects.filter(message="")
    #     return render(message, 'okr/includes/poker.html')

    # def get(self, request):
    #     g = request.GET
    #     print(request)
    #     # Poker.objects.create(message=g['message'])
    #     # request.POST.get('message', False)
    #     return render(request, 'okr/includes/poker.html')

    # def get(self, request):
    #     message = request.POST.get("message")
    #     return render('Hello %s' % message, 'okr/includes/poker.html')

    # def insert_name(request):
    #     poker_instance_name = Poker.objects.create(name="test")
    #     return poker_instance_name
    #
    # def insert_cardpicked(request):
    #     poker_instance_cardpicked = Poker.objects.create(cardpicked="69")
    #     return poker_instance_cardpicked
    #
    # def insert_story(request):
    #     poker_instance_story = Poker.objects.create(story="420")
    #     return poker_instance_story

    @requires_csrf_token
    def my_view(request):
        c = {}
        # ...
        return render(request, 'okr/includes/poker.html', c)
