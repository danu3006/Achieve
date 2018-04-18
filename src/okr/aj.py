import warnings

from jira.client import JIRA

from .models import Issue


class AJ(object):
    """
        Connection handling for Achieve and JIRA.
    """

    def __init__(self):
        try:
            server = 'https://jira.cbs.europe.intranet:8081'
            options = {
                'server': server,
                'verify': False,
            }
            warnings.filterwarnings("ignore")
            self.jira = JIRA(options=options, basic_auth=('rb15jm', 'Apples11'))
        except Exception as e:
            self.jira = None
            print("Failed to connect to JIRA: %s" % e)

    @staticmethod
    def get_priority(priority):
        """ 11 => low, 12 => medium , 13 => high """
        if priority.lower() == 'low':
            return Issue.LOW
        elif priority.lower() == 'medium':
            return Issue.MEDIUM
        elif priority.lower() == 'Mandatory':
            return Issue.MANDATORY
        else:
            return Issue.HIGH

    @staticmethod
    def get_status(status):
        if status.lower() in ('done', 'resolved', 'closed'):
            return True
        else:
            return False

    @staticmethod
    def get_type(type_object):
        if type_object.strip().lower() == 'sub-task':
            return Issue.SUB_TASK
        elif type_object.strip().lower() == 'task':
            return Issue.TASK
        elif type_object.strip().lower() == 'incident':
            return Issue.INCIDENT
        else:
            return Issue.STORY
