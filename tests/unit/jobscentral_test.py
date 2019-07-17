import os
import json

from sgjobutils.transform import JobscentralTransformer

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

SOURCE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/json'


def test_health():
    assert True


def test_transformer_init_empty_row():
    d = JobscentralTransformer.init_empty_row()
    for i, k in enumerate(d.keys()):
        assert HEADERS[i] == k


def test_transform():
    filename = 'sample_job_jobscentral.json'
    with open('{}/{}'.format(SOURCE_FOLDER, filename), 'r') as f:
        data = json.load(f)
        transformed_row = JobscentralTransformer.transform_row(data)

        # Assert data is correctly transformed
        assert transformed_row['source_id'] == 'J3T5YM6K0G1J9F80JDX'
        assert transformed_row['title'] == 'Apple Genius - Technical Customer Service'
        assert transformed_row['uen'] == 'none'
        assert transformed_row['company_name'] == 'Apple Inc.'
        assert transformed_row['minimum_qualification'] == 'ITE'
        assert transformed_row['experience_level'] == 'manager'
        assert transformed_row['minimum_years_experience'] == 0
        assert transformed_row['num_vacancies'] == 1
        print(data['payHighLow'])
        assert transformed_row['salary_min'] == 1000
        assert transformed_row['salary_max'] == 3000
        assert transformed_row['salary_avg'] == 2000
        assert transformed_row['ssoc'] == 0
        assert transformed_row['date_posted'] == '2019-06-25'
        assert transformed_row['date_expire'] == '2019-07-11'
        assert transformed_row['date_last_seen'] is None
        assert transformed_row['source'] == 'jobscentral'
        assert transformed_row['description'] is not None
        assert transformed_row['is_engineering'] == 1
        assert transformed_row['is_employment_agency'] == 0
        assert transformed_row['is_gig'] == 0


def test_get_money():

    money_string = "3,000 - 5,600 SGD / Month"
    low, high = JobscentralTransformer.get_money(money_string)
    assert low == 3000
    assert high == 5600

    money_string = "123 - 321 SGD / Month"
    low, high = JobscentralTransformer.get_money(money_string)
    assert low == 123
    assert high == 321

    money_string = "3,000 - 5,000 SGD / Hour"
    low, high = JobscentralTransformer.get_money(money_string)
    assert low == 3000
    assert high == 5000

    money_string = "20 - 50 SGD / Month"
    low, high = JobscentralTransformer.get_money(money_string)
    assert low == 20
    assert high == 50
