from collections import OrderedDict
from .industry import get_industry_mapping
from .common import (clean_html,
                     clean_non_ascii,
                     get_education,
                     get_lowest_qualification,
                     get_minimum_years_experience,
                     get_minimum_experience_level,
                     is_engineering)


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
        'is_engineering'
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
    def transform_row(cls, row):

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

        return new_row


    class JobscentralTransformer(Transformer):

        @classmethod
        def get_education(cls, educational_string):
            strings = educational_string.split(',')
            educational_strings = []
            if 'drnol' in strings:
                educational_strings.append()

        @classmethod
        def map_position(cls, position):
            pass

        @classmethod
        def transform_row(cls, row):

            new_row = cls.init_empty_row()

            description = row.get('jobDescription', '')
            description = clean_non_ascii(clean_html(description))

            new_row['source_id'] = row['id']

            new_row['title'] = row['jobTitle']

            new_row['uen'] = 'none' # No UEN for JobsCentral

            new_row['company_name'] = row['company']

            new_row['minimum_qualification'] = get_lowest_qualification(get_education(description))

            new_row['minimum_years_experience'] = get_minimum_years_experience(description)

            new_row['experience_level'] = 'none'

