import json

from api.serializers import IssueSerializer
from .aj import AJ
from .models import Issue


class Poker:

    def __init__(self, team):
        self.jira_con = AJ()
        self.team = team
        self.users = team.team_user_set
        self.issues = []
        self.CARD_0 = 0
        self.CARD_0_5 = 0.5
        self.CARD_1 = 1
        self.CARD_3 = 3
        self.CARD_5 = 5
        self.CARD_8 = 8
        self.CARD_13 = 13
        self.CARD_20 = 20
        self.CARD_40 = 40
        self.CARD_100 = 100

    def get_jira_issues(self):

        # TODO: Augment JQL to incorporate SCRUM teams
        jql = "project = 'SUM'"

        object_list = self.jira_con.jira.search_issues(jql)
        issues = []

        for o in object_list:
            # TODO: Complete arguments
            issue, created = Issue.objects.get_or_create(key=o.key, defaults={})
            issues.append(issue)

        self.issues = issues
        return IssueSerializer(self.issues, many=True).data

    def assign_story_points(self, issue, card_value):

        if issue in self.issues:
            issue.story_points = card_value
            issue.save()

        return json.dumps({'request': 'success'})
