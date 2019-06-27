import re
import string

from .constants import Constants
from .money import get_money

# Constants for education
PRIMARY = "primary"
SECONDARY = "secondary"
PRIMARY_SECONDARY = "primary/secondary"
ITE = "ITE"
DIPLOMA = "diploma"
DEGREE = "degree"
NO_EDUCATION = "none"

# Constants for experience level
ENTRY = "entry"
MANAGER = "manager"
PROFESSIONAL = "professional"
EXECUTIVE = "executive"
NO_EXPERIENCE = "none"

PRINTABLE = set(string.printable)

def get_education_anchor(description_tokens, anchor):

    complements = ["responsibilit", "duties", "role", "contact", "function", "requirement", "emphasis", "purpose"]

    for i, token in enumerate(description_tokens):
        if anchor in token:

            # print(" ".join(description_tokens))
            # print("")
            
            count = 0
            left_bound = i - 2 if (i - 2 > 0) else 0
            right_bound = i + 3 if (i + 3 <= len(description_tokens)) else len(description_tokens)
            for j in range(left_bound, right_bound):
                for complement in complements:
                    if complement in description_tokens[j]:
                        count += 1
                        break

            if count == 0:
                return True
            else:
                return False

    return False



def get_education(description):
    """
    Extracts the education qualification requirements from job description
    Sometimes extracts false positives due to simple methodology

    :param description: text string of the description
    :return: a list containing values in the set {primary, secondary, ITE, diploma, degree}
    """

    qualifications = []

    description_lower = description.lower()
    description_tokens = description_lower.split()

    # Use anchor method to reduce false positives
    if get_education_anchor(description_tokens, "primary"):
        qualifications.append(PRIMARY)

    # Use anchor method to reduce false positives
    if get_education_anchor(description_tokens, "secondary"):
        qualifications.append(SECONDARY)

    if "ITE" in description or "NITEC" in description:
        qualifications.append(ITE)

    if "diploma" in description_lower:
        qualifications.append(DIPLOMA)

    if "degree" in description_lower or "college" in description_lower:
        qualifications.append(DEGREE)

    return qualifications


def get_highest_qualification(qualifications):
    """
    Returns the highest qualification in a list

    :param qualifications: list containing qualifications
    :return: highest academic qualification in list
    """

    if not qualifications:
        return NO_EDUCATION

    if DEGREE in qualifications:
        return DEGREE
    elif DIPLOMA in qualifications:
        return DIPLOMA
    elif ITE in qualifications:
        return ITE
    elif PRIMARY_SECONDARY in qualifications:
        return PRIMARY_SECONDARY
    elif SECONDARY in qualifications:
        return SECONDARY
    elif PRIMARY in qualifications:
        return PRIMARY

    return NO_EDUCATION


def get_lowest_qualification(qualifications):
    """
    Returns the minimum qualification in a list

    :param qualifications: list containing qualifications
    :return: minimum academic qualification in list
    """

    if not qualifications:
        return NO_EDUCATION

    if PRIMARY_SECONDARY in qualifications:
        return PRIMARY_SECONDARY
    elif PRIMARY in qualifications:
        return PRIMARY
    elif SECONDARY in qualifications:
        return SECONDARY
    elif ITE in qualifications:
        return ITE
    elif DIPLOMA in qualifications:
        return DIPLOMA
    elif DEGREE in qualifications:
        return DEGREE

    return NO_EDUCATION


def num_from_string(num_string):
    """
    Given a string name of a number, return the number in integer form
    Returns 0 if not a number

    :param num_string: string of number from 0 to 9
    :return: integer representing the number, 0 if not num string
    """

    nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    strings = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

    try:
        index = strings.index(num_string)
        return nums[index]

    # Not in list
    except ValueError as e:
        return 0


def get_minimum_experience_level(levels):

    if not levels:
        return NO_EXPERIENCE

    if ENTRY in levels:
        return ENTRY
    if MANAGER in levels:
        return MANAGER
    if PROFESSIONAL in levels:
        return PROFESSIONAL
    if EXECUTIVE in levels:
        return EXECUTIVE

    return NO_EXPERIENCE


def get_minimum_years_experience(description):
    """
    Returns the minimum number of years of experienced required in a job description

    :param description: text string of job description
    :return: integer indicating number of years of experience, 0 if none required
    """

    def get_last_space_from_pos(start_pos):
        last_pos = start_pos - 1
        while (last_pos >= 0 and not description_lower[last_pos].isspace()):
            last_pos -= 1
        return last_pos + 1

    description_lower = description.lower()
    pos = description_lower.find("year experience")
    if pos < 0:
        pos = description_lower.find("years experience")
    
    # Failed to find anchor, no experience required then
    if pos <= 0: # = for defensive programming
        return 0

    # Grab string containing quantity
    prev = description_lower[pos - 1]
    num = ""
    last_pos = get_last_space_from_pos(pos - 1)
    if prev.isspace():
        num = description[last_pos: pos - 1]
    else:
        num = description[last_pos: pos]

    # Process string
    if len(num) == 1:
        if num.isdigit():
            return int(num)
        else:
            return 1    # default return
    else:
        # number in range
        if "-" in num:
            parts = num.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return (int(parts[0]) + int(parts[1])) / 2.0
            else:
                return 1    # default return

        # number written in string form?
        else:
            return num_from_string(num)


def is_shift(description):
    """
    Determines if a description is indicative of shift work.
    Finds the anchor word 'shift' and looks in a 7 word window for indicative words
    Otherwise, if the count of 'shift' is at least 2, return positive

    :param description: text string of job description
    :return: boolean indicating shift work or not
    """

    description_lower = description.lower()
    tokens = description_lower.split()

    fuzzy_anchors = ["shifts", "rotat", "work", "time", "closing", "night", "morning", "duties", "start", "end", "based", "throughout", "team", "roster", "transport", "timing", "allowance", "hour", "each", "split", "depending"]
    end_anchors = ["am", "pm"] 
    count = 0

    for i, token in enumerate(tokens):
        if "shift" in token:
            count += 1
            left_bound = i - 3 if (i - 3 > 0) else 0
            right_bound = i + 4 if (i + 4 <= len(tokens)) else len(tokens)

            # Look for positive indicative anchor word for shift work
            for anchor in fuzzy_anchors:
                for j in range(left_bound, right_bound):
                    if anchor in tokens[j]:
                        return True
            for anchor in end_anchors:
                for j in range(left_bound, right_bound):
                    if tokens[j].endswith(anchor):
                        return True

            # If at least 2 mentions
            if count >= 2:
                return True

    return False


def get_salary(description, minimum=0):
    """
    Given a text description of a job, extract the salary amount if it exists
    If multiple instances of a salary are present, or if the salary is present
    in a range, returns the mean value

    :param description: text string of job description
    :return: integer amount indicating the salary, returns 0 if not found
    """

    MAGIC_WINDOW_SIZE = 5
    description_lower = description.lower()
    tokens = description_lower.split()

    amounts = []
    for i, token in enumerate(tokens):
        if not "salary" in token:
            continue

        left_bound = i - MAGIC_WINDOW_SIZE if (i - MAGIC_WINDOW_SIZE > 0) else 0
        right_bound = i + 1 + MAGIC_WINDOW_SIZE if (i + 1 + MAGIC_WINDOW_SIZE <= len(tokens)) else len(tokens)

        for j in range(left_bound, right_bound):
            amt = get_money(tokens[j])
            amt2 = -1
            if amt < 0:
                continue

            if j + 2 < right_bound:
                amt2 = get_money(tokens[j + 2])

            if amt2 < 0:
                amounts.append(amt)
            else:
                amounts.append(int((amt + amt2) / 2.0))
            break

    # Average over all extracted salary amounts
    amounts = [amt for amt in amounts if amt >= minimum]
    if not amounts:
        return 0
    else:
        return sum(amounts) // len(amounts)


def clean_non_ascii(text):
    if not text:
        return text
    return "".join(filter(lambda x: x in PRINTABLE, text)).strip()


def clean_html(html):
    if not html:
        return html
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', html)
    cleantext = " ".join(cleantext.split())
    return cleantext


def is_engineering(title, description):

    def in_list(description, l):
        for token in l:
            if token in description:
                return True
        return False

    requisites = ['engine', 'technic', 'mechanic', 'chemical', 'aero', 'electronic', 'logistic']
    title_requisites = ['engine', 'technic', 'mechanic', 'chemical', 'aero', 'electronic', 'logistic', 'process']
    anti_requisites = ['software engine']
    title = title.lower()
    description = description.lower()

    # Check anti-requisites
    if in_list(title, anti_requisites):
        return False
    if in_list(description, anti_requisites):
        return False

    # Check requisites
    if in_list(title, title_requisites):
        return True
    if in_list(description, requisites):
        return True

    return False
