from collections import OrderedDict
from .industry import get_industry_mapping
from .common import (clean_html,
                     clean_non_ascii,
                     get_education,
                     get_lowest_qualification,
                     get_minimum_years_experience,
                     get_minimum_experience_level,
                     is_engineering)
from .money import get_money_from_single_word
from .jobsbank import get_top_skills, sort_skills


class Transformer:
    """
    Abstract class for transforming data from source data format to standard data format.
    The list of headers is defined below. Specifically:

    source_id - unique id (primary key) of source platform, usually a uuid
    title - job title (preferably a lemmatized version)
    uen - UEN number of company offering job, can be None
    company_name - company corresponding to UEN. Listed because not all platforms provide
        UEN information, so this is a fallback. Can be None
    minimum_qualification - minimum education qualification level. Can be None
    experience_level - experience level required for this job. To distinguish between entry and
        non-entry level jobs for now. Empty value is None
    minimum_years_experience - minimum number of years of experience required for this job.
        Empty value is 0
    salary_max - upper bound of salary advertised in dollars. Empty value is 0
    salary_min - lower bound of salary advertised in dollars (could be the same as max)
    salary_avg - mean of the max and min salary
    ssoc - SSOC code number of the job, if available. Can be None
    date_posted - date job was posted in YYYY-MM-DD format. Can be None
    date_expire - date job will expire in YYYY-MM-DD format. Can be None
    date_last_seen - date this job was last scraped
    source - string indicating the source of the data
    description - string containing the full job description
    """

    # Row headers
    HEADERS = [
        'source_id',
        'title',
        'uen',
        'company_name',
        'minimum_qualification',
        'experience_level',
        'minimum_years_experience',
        'num_vacancies',
        'salary_max',
        'salary_min',
        "salary_avg",
        'ssoc',
        'date_posted',
        'date_expire',
        'date_last_seen',
        'source',
        'description',
        'is_engineering',
        'is_employment_agency',
        'is_gig',
        'top_skill_1',
        'top_skill_2',
        'top_skill_3',
        'top_skill_4',
        'top_skill_5'
        ]

    # Experience level
    VALID_EXPERIENCE_LEVELS = ['entry', 'executive', 'manager', 'professional']

    @classmethod
    def init_empty_row(cls):
        """
        Initialize an empty row with headers corresponding to the standard interface.
        Row is an OrderedDict with keys inserted in correct order
        :return: an OrderedDict with the default values of
        """
        row = OrderedDict()
        for header in cls.HEADERS:
            row[header] = None

        # Custom field defaults
        row['minimum_years_experience'] = 0
        row['salary_max'] = 0
        row['salary_min'] = 0
        row['salary_avg'] = 0
        row['ssoc'] = 0
        row['is_engineering'] = False
        row['is_employment_agency'] = False
        row['is_gig'] = False
        row['top_skill_1'] = 0
        row['top_skill_2'] = 0
        row['top_skill_3'] = 0
        row['top_skill_4'] = 0
        row['top_skill_5'] = 0

        return row

    @classmethod
    def map_position(cls, position):
        """
        Abstract method.
        Maps a position string from the source to an option in the standard list
        :param position: position string defined in source
        :return: position string defined in standard
        """
        pass

    @classmethod
    def transform_row(cls, row):
        """
        Abstract method.
        Takes a single job entry from the input source and transforms the input
        into the standard format, stored in an OrderedDict, with the headers
        as defined in the standard list in this class
        :param row: single entry from source, usually a dictionary (no restriction)
        :return: an OrderedDict with the relevant fields filled in from the input
        """
        pass


class JobsbankTransformer(Transformer):

    # Experience Levels
    ENTRY_LEVEL = ['Fresh/entry level', 'Non-executive', 'Executive', 'Junior Executive']
    EXECUTIVE = ['Senior Executive']
    MANAGER = ['Manager', 'Middle Management', 'Senior Management']
    PROFESSIONAL = ['Professional']

    @classmethod
    def map_position(cls, position):
        if position in cls.ENTRY_LEVEL:
            return 'entry'
        if position in cls.EXECUTIVE:
            return 'executive'
        if position in cls.MANAGER:
            return 'manager'
        if position in cls.PROFESSIONAL:
            return 'professional'

        # Default catch all
        return 'manager'

    @classmethod
    def transform_row(cls, row, skill_count):

        new_row = cls.init_empty_row()

        # Process description for downstream work
        # Jobsbank has two separate description fields, so concatenate them
        first_description = clean_non_ascii(clean_html(row.get('description', "")))
        second_description = clean_non_ascii(clean_html(row.get('otherRequirements', "")))
        description = '{} {}'.format(first_description, second_description)

        # Get source_id
        new_row['source_id'] = row['uuid']

        # Get title
        new_row['title'] = row['title']

        # Get uen and company_name
        posted_company = row.get('postedCompany', None)
        if posted_company:
            new_row['uen'] = posted_company.get('uen', None)
            new_row['company_name'] = posted_company.get('name', None)

        # Get minimum qualification
        new_row['minimum_qualification'] = 'None'
        new_row['minimum_qualification'] = get_lowest_qualification(get_education(description))

        # Get salary
        salary = row.get('salary', None)
        if salary:
            maximum = salary.get('maximum', None)
            minimum = salary.get('minimum', None)
            if maximum and minimum:
                new_row['salary_max'] = maximum
                new_row['salary_min'] = minimum
                new_row['salary_avg'] = (maximum + minimum) / 2

        # Get minimum years experience
        new_row['minimum_years_experience'] = row['minimumYearsExperience']
        if not isinstance(new_row['minimum_years_experience'], int):
            new_row['minimum_years_experience'] = get_minimum_years_experience(description)

        # Get experience level
        positions = [cls.map_position(entry['position']) for entry in row['positionLevels']]
        minimum_experience_level = get_minimum_experience_level(positions)

        if minimum_experience_level == 'entry' and new_row['minimum_years_experience'] >= 3:
            minimum_experience_level = 'executive'
        elif minimum_experience_level == 'entry' and new_row['salary_avg'] > 5000:
            minimum_experience_level = 'executive'

        new_row['experience_level'] = minimum_experience_level

        # Get number of vacancies
        new_row['num_vacancies'] = row.get('numberOfVacancies', 1)

        # Get SSOC
        new_row['ssoc'] = row.get('ssocCode', None)

        # Get dates
        new_row['date_posted'] = row['metadata']['originalPostingDate']
        new_row['date_expire'] = row['metadata']['expiryDate']
        new_row['date_last_seen'] = row['metadata']['expiryDate'] # have to be manually updated

        # Set source
        new_row['source'] = 'jobsbank'

        # Get description
        new_row['description'] = description

        # Get is engineering
        new_row['is_engineering'] = 1 if is_engineering(row['title'], description) else 0

        new_row['is_employment_agency'] = 1 if row['metadata']['isPostedOnBehalf'] else 0

        new_row['is_gig'] = 0 #TODO: Implement

        # Handle skills
        skills = get_top_skills(sort_skills(row['skills'], skill_count), 5)
        new_row['top_skill_1'] = skills[0]['id']
        new_row['top_skill_2'] = skills[1]['id']
        new_row['top_skill_3'] = skills[2]['id']
        new_row['top_skill_4'] = skills[3]['id']
        new_row['top_skill_5'] = skills[4]['id']

        return new_row


class FastjobsTransformer(Transformer):

    @classmethod
    def map_position(cls, position):
        pass


    @classmethod
    def transform_row(cls, row):

        new_row = cls.init_empty_row()

        description = row.get('description', '')

        new_row['source_id'] = row['identifier']['value']

        new_row['title'] = row['title']

        new_row['uen'] = row.get('uen', 'none')

        if row.get('hiringOrganization', None) and row['hiringOrganization'].get('name', None):
            new_row['company_name'] = row['hiringOrganization']['name']
        else:
            new_row['company_name'] = ''

        new_row['minimum_qualification'] = get_lowest_qualification(get_education(description))

        new_row['minimum_years_experience'] = get_minimum_years_experience(description)

        new_row['num_vacancies'] = 1 # Default assume one job posting is 1 vacancy

        new_row['experience_level'] = 'none'

        # Salary
        if row.get('baseSalary', None):
            new_row['salary_min'] = row['baseSalary']['value']['value']
            new_row['salary_max'] = row['baseSalary']['value']['value']
            new_row['salary_avg'] = row['baseSalary']['value']['value']
        elif row.get('min_salary', None):
            new_row['salary_min'] = row['min_salary']
            new_row['salary_max'] = row['min_salary']
            new_row['salary_avg'] = row['min_salary']

        # Date information
        new_row['date_posted'] = row['posted_on']
        new_row['date_expire'] = row['expiring_on']

        new_row['source'] = 'fastjobs'

        new_row['description'] = description

        # Get is engineering
        new_row['is_engineering'] = 1 if is_engineering(row['title'], description) else 0

        new_row['is_employment_agency'] = 0 #TODO: Implement

        new_row['is_gig'] = 0 #TODO: Implement

        # Handle skills

        return new_row


class JobscentralTransformer(Transformer):

    jobscentral_education = {
        'drin14': 'diploma',            # diploma
        'dr32': 'degree',               # bachelor's/honors
        'drucdr': 'degree',             # master's/phd
        'drite': 'ITE',                 # ITE
        'dral': 'diploma',              # 'a' levels
        'drnol': 'primary/secondary'    # 'o'/'n' levels
    }

    jobscentral_experience = {
        '0': 'entry',       # 'Entry Level'
        '1': 'manager',     # 'Experienced'
        '2': 'manager',     # 'Manager'
        '3': 'manager',     # 'Senior Manager'
        '4': 'executive',   # 'Top Management'
        '5': 'entry'        # 'Student Job'
    }

    @classmethod
    def clean_text(cls, description):
        return description.replace('&rsquo;', "'")\
                          .replace('&hellip;', '.')\
                          .replace('&nbsp;', ' ')\
                          .replace('&amp;', '&')

    @classmethod
    def get_education(cls, educational_string):
        strings = educational_string.split(',')
        educational_strings = []
        for string in strings:
            ed = cls.jobscentral_education.get(string, None)
            if ed:
                educational_strings.append(ed)
        return educational_strings

    @classmethod
    def get_experience(cls, position_string):
        strings = position_string.split(',')
        experience_strings = []
        for string in strings:
            pos = cls.jobscentral_experience.get(string, None)
            if pos:
                experience_strings.append(pos)
        return pos

    @classmethod
    def get_money(cls, money_string):
        money_parts = money_string.split('-')
        if len(money_parts) == 2:
            low = int(money_parts[0].strip().replace(',', ''))
            high = int(money_parts[1].strip().split(' ')[0].split('.')[0].replace(',', ''))
            print(low, high)
            return low, high

        elif len(money_parts) == 1:
            val = int(money_parts[0].strip().replace(',', ''))
            return val, val

        else:
            return 0, 0

    @classmethod
    def map_position(cls, position):
        pass

    @classmethod
    def transform_row(cls, row):

        new_row = cls.init_empty_row()

        description = '{} {}'.format(row.get('jobDescription', ''), row.get('companyProfiles', ''))
        description = clean_non_ascii(cls.clean_text(clean_html(description)))

        new_row['source_id'] = row['id']

        new_row['title'] = row['jobTitle']

        new_row['uen'] = 'none' # No UEN for JobsCentral, need backfill

        new_row['company_name'] = row['company']

        new_row['minimum_qualification'] = get_lowest_qualification(cls.get_education(row['qualification']))

        new_row['minimum_years_experience'] = get_minimum_years_experience(description)

        new_row['experience_level'] = get_minimum_experience_level(cls.get_experience(row['position']))

        new_row['num_vacancies'] = 1  # Default assume one job posting is 1 vacancy

        sal_low, sal_high = 0, 0
        if row['payHighLow'].isdigit():
            sal_low, sal_high = cls.get_money(row['payHighLow'])
        new_row['salary_min'] = sal_low
        new_row['salary_max'] = sal_high
        new_row['salary_avg'] = int((sal_high + sal_low) / 2)

        new_row['date_posted'] = row['postDate'].split('T')[0]
        new_row['date_expire'] = row['endDate'].split('T')[0]

        new_row['source'] = 'jobscentral'

        new_row['description'] = description

        # Only use description information so that company information is not inside
        new_row['is_engineering'] = 1 if is_engineering(row['jobTitle'], row.get('jobDescription', '')) else 0

        new_row['is_employment_agency'] = 1 if len(row.get('eaLicenceNo', '')) > 0 else 0

        new_row['is_gig'] = 0  # TODO: Implement

        return new_row
