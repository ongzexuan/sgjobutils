from sgjobutils.transform import Transformer, JobsbankTransformer

HEADERS = [
        'source_id',
        'title',
        'uen',
        'company_name',
        'minimum_qualification',
        'experience_level',
        'minimum_years_experience',
        'salary_max',
        'salary_min',
        "salary_avg",
        'ssoc',
        'date_posted',
        'date_expire',
        'date_last_seen',
        'source',
        'description']


def test_health():
    return True


def test_transformer_init_empty_row():
    d = Transformer.init_empty_row()
    for i, k in enumerate(d.keys()):
        assert HEADERS[i] == k


def test_jobsbank_transformer_init_empty_row():
    d = JobsbankTransformer.init_empty_row()
    for i, k in enumerate(d.keys()):
        assert HEADERS[i] == k