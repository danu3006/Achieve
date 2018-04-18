from .aj import AJ
from .models import *


def update_issues():
    # initiate class and variables
    jira_con = AJ()
    issues_key = []
    start_from = 0
    end_at = 49

    # get all issue key's as a list
    for issue in Issue.objects.filter(status=False):
        issues_key.append(issue.key)

    # total number of issues is greater than dynamic starting point
    while len(issues_key) >= start_from:

        # construct jql with issue key's as jira_string
        jql = "project = 'SUM' and issuekey in ({jira_string})".format(
            jira_string=','.join(issues_key[start_from:end_at]))

        # execute jql and return data as python objects
        object_list = jira_con.jira.search_issues(jql)

        for issue in object_list:
            item = Issue.objects.get(key=issue.key)

            try:
                item.user = User.objects.get(username=issue.fields.assignee.name)
            except (AttributeError, User.DoesNotExist) as e:
                print('Error:', item.key, 'username')

            try:
                item.priority = jira_con.get_priority(issue.fields.priority.name)
            except AttributeError:
                item.priority = jira_con.get_priority('low')
                print('Error:', item.key, 'priority')

            try:
                if jira_con.get_status(issue.fields.status.name) and not item.status:
                    Activity.objects.create(type=Activity.COMPLETED_JIRA, user=item.user, data=item.key)
                item.status = jira_con.get_status(issue.fields.status.name)
            except AttributeError:
                item.status = False
                print('Error:', item.key, 'status')

            try:
                item.type = jira_con.get_type(issue.fields.issuetype.name)
            except AttributeError:
                item.type = jira_con.get_type('task')
                print('Error:', item.key, 'type')

            try:
                item.summary = issue.fields.summary
            except AttributeError:
                item.summary = 'No Summary Pulled!'
                print('Error:', item.key, 'summary')

            # TODO: Fix static data for issues.
            item.story_points = 3
            item.coin_value = 0

            # save issue
            item.save()

            print('Updated {issue}'.format(issue=issue.key), '--', issue.fields.status.name)

        # new start and end positions
        start_from = end_at
        end_at += 49

        print('-------------------- COMPLETED-------------------')


def update_percentages():
    for result in Result.objects.all():
        result.calculate_percentage()

    for objective in Objective.objects.all():
        objective.calculate_percentage()

    for result in GlobalKeyResult.objects.all():
        result.calculate_percentage()


def one_time_progress_update():
    for result in Result.objects.all():
        if len(result.jira_issues.all()) == 0:
            result.manual_bar = True
        result.percentage = 0
        result.save()
