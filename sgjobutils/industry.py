import csv
import os


def get_mapping_dict(filename):

    d2010 = {}
    d2015 = {}
    with open(filename, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0

        for row in csv_reader:
            line_count += 1

            # Skip headers
            if line_count == 1:
                continue

            sector = row[0]
            industry = row[1]
            subindustry = row[2]

            ssic2010 = row[3]
            ssic2015 = row[4]

            if ssic2010:
                d2010[ssic2010] = (sector, industry, subindustry)
            if ssic2015:
                d2015[ssic2015] = (sector, industry, subindustry)

    return d2010, d2015


def get_backup_mapping_dict(filename):

    mapping = {}
    with open(filename, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0

        for row in csv_reader:
            line_count += 1

            # Skip headers
            if line_count == 1:
                continue

            key = row[0].strip()
            sector = row[1]
            industry = row[2]
            subindustry = row[3]

            mapping[key] = (sector, industry, subindustry)

    return mapping

# Load mapping
MAPPING_FILE = 'industry_mappings.csv'
dir_path = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), MAPPING_FILE)
d2010, d2015 = get_mapping_dict(dir_path)


# Load backup mapping
BACKUP_MAPPING_FILE = 'industry_mapping_fallback.csv'
dir_path = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), BACKUP_MAPPING_FILE)
backup_mapping = get_backup_mapping_dict(dir_path)


def get_industry_mapping(ssic):
    if len(ssic) == 4:
        ssic = '0' + ssic

    res = d2015.get(ssic, None)
    if res:
        return res
    res = d2010.get(ssic, None)
    if res:
        return res
    key = ssic[0:2]
    res = backup_mapping.get(key, (None, None, None))
    return res