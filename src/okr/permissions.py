def is_manager_or_staff(user):
    return True if user.profile.is_manager() or user.is_staff else False


def is_manager_or_staff_or_in_team(user, team):
    return True if user.profile.is_manager() or user.is_staff or user.profile.team == team else False


def is_manager_of_team_or_staff(user, team):
    return True if user.profile.is_manager_of(team) or user.is_staff else False


def is_owner_of_objective(user, objective):
    return True if objective.user == user or user.is_staff else False


def is_owner_of_key_result(user, key_result):
    return True if key_result.objective.user == user or user.is_staff else False


def is_owner_of_issue(user, issue):
    return True if issue.user == user or user.is_staff else False
