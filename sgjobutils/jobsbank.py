from operator import itemgetter


def sort_skills(skills, skill_count):
    """
    Given a list of skills, sort them by their confidence level
    in descending order. Cleans up irrelevant skills
    :param skills: list of skill objects, each with a confidence value
    :return: sorted list of skills, with irrelevant fields removed
    """

    skill_count = [n + 1 for n in skill_count]  # Fix divide by zero errors
    new_skills = [{'id': skill['id'],
                   'skill': skill['skill'],
                   'confidence': skill['confidence'] / skill_count[skill['id']]}
                  for skill in skills]
    return sorted(new_skills, key=itemgetter('confidence'), reverse=True)


def get_top_skills(skills, n):
    """
    Given a sorted list of skills sorted in descending order, return the top n
    :param skills: sorted list of skills in descending order
    :param n: some integer
    :return: top n skills
    """
    if n < 0:
        return []
    elif n > len(skills):
        return skills
    else:
        return skills[:n]


def filter_skills(skills):
    pass