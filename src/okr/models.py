from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models as models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import localtime, now
from django_extensions.db import fields as extension_fields


def get_current_quarter():
    quarters = Quarter.objects.all()
    this_current_quarter = None

    for quarter in quarters:
        if quarter.start_date <= localtime(now()).date() <= quarter.end_date:
            this_current_quarter = quarter

    return this_current_quarter


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile_save = Profile(user=instance, name=instance.username)
        profile_save.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Quarter(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    name = models.CharField(max_length=10)
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')

    class Meta:
        verbose_name = 'Quarter'
        verbose_name_plural = 'Quarters'

    def __str__(self):
        return str(self.created.year) + self.name


class Team(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def total_members(self):
        return len(Profile.objects.filter(team=self))

    def get_members(self):
        return Profile.objects.filter(team=self)

    def get_manager(self):
        return Manager.objects.get(team=self)


class Manager(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{manager} - {team}'.format(manager=self.manager, team=self.team)


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Fields
    name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    email = models.EmailField(blank=True)
    coins = models.IntegerField(default=0)
    gems = models.IntegerField(default=0)
    karma = models.IntegerField(default=0)
    energy = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal('100.0'))
    xp = models.IntegerField(default=0, verbose_name='Experience')
    rights = models.IntegerField(default=0, verbose_name='Character Rights')

    # Relationship Fields
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='team_user_set', default=None, blank=True, null=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.slug

    def get_objectives(self):
        return Objective.objects.filter(user=self.user,
                                        global_key_result__objective__quarter=get_current_quarter())

    def get_percentage(self):
        total_objectives = len(self.get_objectives())
        total_percentage = 0

        if total_objectives > 0:
            for objective in self.get_objectives():
                total_percentage += objective.percentage

            return round(total_percentage / total_objectives, 2)

        return 0

    def has_jira_issues_connected(self):
        count = 0
        number_of_key_results = 0
        for objective in self.get_objectives():
            for keyresult in objective.get_key_results():
                number_of_key_results += 1
                if len(keyresult.jira_issues.all()) == 0:
                    count += 1
        return not count == number_of_key_results

    def is_manager(self):
        return Manager.objects.filter(manager=self.user).exists()

    def get_managed_teams(self):
        return Manager.objects.filter(manager=self.user)

    def is_manager_of(self, team):
        return Manager.objects.filter(manager=self.user, team=team).exists()

    def get_title(self):
        title = ''

        if self.rights == 0:
            title = 'Normal'

        if self.is_manager():
            title = 'Manager'

        return title


class Issue(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    MANDATORY = 'Mandatory'

    TASK = 'Task'
    SUB_TASK = 'Sub-Task'
    STORY = 'Story'
    INCIDENT = 'Incident'

    PRIORITY = (
        (LOW, LOW),
        (MEDIUM, MEDIUM),
        (HIGH, HIGH),
        (MANDATORY, MANDATORY)
    )

    TYPE = (
        (TASK, TASK),
        (SUB_TASK, SUB_TASK),
        (STORY, STORY),
        (INCIDENT, INCIDENT),
    )

    key = models.CharField(max_length=50)
    priority = models.CharField(max_length=10, choices=PRIORITY, default=LOW)
    status = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE, default=TASK)
    story_points = models.IntegerField(default=0, verbose_name='Story Points')

    user = models.ForeignKey(User, default=None, null=True, related_name='user_issue_set', on_delete=models.CASCADE)

    def __str__(self):
        return '{key} - {summary}'.format(key=self.key, summary=self.summary)

    def get_linked_key_results(self):
        return Result.objects.filter(jira_issues__key__contains=self.key)

    def tmp_status(self):
        if self.summary:
            return False
        return True


class GlobalObjective(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objective = models.TextField(help_text="This is the overall objective eg. Be ITRIC Compliant.")
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Global Objective'
        verbose_name_plural = 'Global Objectives'

    def __str__(self):
        return u'{q} - {obj}'.format(q=self.quarter.name, obj=self.objective)

    def get_key_results(self):
        objects = GlobalKeyResult.objects.filter(objective=self)
        return objects

    def get_absolute_url(self):
        return reverse('okr:globalobjective-list')

    def get_key(self):
        obj_id = ''
        if len(str(self.id)) <= 3:
            for i in range(1, 3 - len(str(self.id)) + 1):
                obj_id += str(0)

        obj_id += str(self.id)
        return 'GOKR-' + str(obj_id)


class GlobalKeyResult(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objective = models.ForeignKey(GlobalObjective, on_delete=models.CASCADE)
    key_result = models.TextField(verbose_name='Key Result')
    percentage = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Global Key Result'
        verbose_name_plural = 'Global Key Results'

    def __str__(self):
        return u'%s' % self.key_result

    def get_user_objectives(self):
        return Objective.objects.filter(global_key_result=self)

    def calculate_percentage(self):
        total_objectives = len(self.get_user_objectives())
        total_percentage = 0

        if total_objectives > 0:
            for objective in self.get_user_objectives():
                total_percentage += objective.percentage
            self.percentage = round(total_percentage / total_objectives, 2)
            self.save()

        return True

    def get_unique_list_of_related_users(self):
        unique_users = []
        for objective in self.get_user_objectives():
            if not objective.user in unique_users:
                unique_users.append(objective.user)

        return unique_users

    def get_key(self):
        obj_id = ''
        if len(str(self.id)) <= 3:
            for i in range(1, 3 - len(str(self.id)) + 1):
                obj_id += str(0)

        obj_id += str(self.id)
        return 'GRST-' + str(obj_id)


class Objective(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    global_key_result = models.ForeignKey(GlobalKeyResult, on_delete=models.CASCADE, related_name='okr',
                                          verbose_name='Global Key Result')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='objective_set')
    objective = models.TextField(help_text="This is your objective you would like to submit.")
    percentage = models.FloatField(default=0)

    class Meta:
        verbose_name = 'User Objective'
        verbose_name_plural = 'User Objectives'

    def __str__(self):
        return u'{user} - {objective}'.format(user=self.user.username, objective=self.objective)

    def get_key_results(self):
        objects = Result.objects.filter(objective=self)
        return objects

    def calculate_percentage(self):
        total_key_results = len(self.get_key_results())
        total_percentage = 0

        if total_key_results > 0:
            for result in self.get_key_results():
                total_percentage += result.percentage
            self.percentage = round(total_percentage / total_key_results, 2)
            self.save()
        return True

    def is_complete(self):
        status = False
        if len(self.get_key_results()) > 0:
            status = True
            for key_result in self.get_key_results():
                status = status and key_result.is_complete()

        return status

    def get_key(self):
        obj_id = ''
        if len(str(self.id)) <= 3:
            for i in range(1, 3 - len(str(self.id)) + 1):
                obj_id += str(0)

        obj_id += str(self.id)
        return 'OKR-' + str(obj_id)


class Result(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    result = models.TextField(help_text="This is your key result related to your objective.")
    jira_issues = models.ManyToManyField(Issue, blank=True, verbose_name='JIRA Issues')
    manual_bar = models.BooleanField(default=False, verbose_name='Manual Progress Bar',
                                     help_text=' If you select this, DO NOT select any jira_issues.')
    percentage = models.FloatField(default=0)

    class Meta:
        verbose_name = 'User Key Result'
        verbose_name_plural = 'User Key Results'

    def __str__(self):
        return u'{user} - {result}'.format(user=self.objective.user.username, result=self.result)

    def tokenize(self):
        return self.result.lower().split(' ')

    def is_complete(self):
        if self.percentage == 100:
            return True
        return False

    def calculate_percentage(self):
        total_issues = len(self.jira_issues.all())
        completed = 0

        if total_issues > 0:
            for issue in self.jira_issues.all():
                if issue.status:
                    completed += 1
            self.percentage = round(completed / total_issues, 2) * 100

        self.save()

        return True

    def get_issues_as_string(self):
        string = ''
        if len(self.jira_issues.all()) == 0:
            return ''
        for issue in self.jira_issues.all():
            string += str(issue.id) + ','

        string = string[:-1]
        return string

    def get_percentage(self):
        return int(self.percentage)

    def get_key(self):
        obj_id = ''
        if len(str(self.id)) <= 3:
            for i in range(1, 3 - len(str(self.id)) + 1):
                obj_id += str(0)

        obj_id += str(self.id)
        return 'RST-' + str(obj_id)


class Activity(models.Model):
    MODIFIED_OBJECTIVE = 'Modified Objective'
    MODIFIED_KEY_RESULT = 'Modified Key Result'
    DELETED_OBJECTIVE = 'Deleted Objective'
    DELETED_KEY_RESULT = 'Deleted Key Result'
    CREATED_OBJECTIVE = 'Created Objective'
    CREATED_KEY_RESULT = 'Created Key Result'
    COMPLETED_OBJECTIVE = 'Completed Objective'
    COMPLETED_KEY_RESULT = 'Completed Key Result'
    COMPLETED_JIRA = 'Completed JIRA issue.'

    ACTIVITY_TYPES = (
        (MODIFIED_OBJECTIVE, MODIFIED_OBJECTIVE),
        (MODIFIED_KEY_RESULT, MODIFIED_KEY_RESULT),
        (DELETED_OBJECTIVE, DELETED_OBJECTIVE),
        (DELETED_KEY_RESULT, DELETED_KEY_RESULT),
        (CREATED_OBJECTIVE, CREATED_OBJECTIVE),
        (CREATED_KEY_RESULT, CREATED_KEY_RESULT),
        (COMPLETED_OBJECTIVE, COMPLETED_OBJECTIVE),
        (COMPLETED_KEY_RESULT, COMPLETED_KEY_RESULT),
        (COMPLETED_JIRA, COMPLETED_JIRA),
    )

    created = models.DateTimeField(auto_now_add=True, editable=False)

    public = models.BooleanField(default=True)
    type = models.CharField(max_length=100, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return str(self.type)


class Poker(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)

    value = models.FloatField(max_length=4)
    issue = models.ForeignKey(Issue, related_name='poker_issues', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='poker_users', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Poker Play'
        verbose_name_plural = 'Poker Plays'

    def get_value(self):
        return self.value

    def get_story(self):
        return self.issue

    def get_message(self):
        return '{user} voted {value} for story {issue}'.format(user=self.user.first_name, value=self.value,
                                                               issue=self.issue.key)

    def __str__(self):
        return '{message}'.format(message=self.get_message())
