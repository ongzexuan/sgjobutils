import csv
import os

from sgjobutils.industry import get_industry_mapping

def test_health():
    return True


def test_specified_ssic():
    return True

    # TEST_FILE = 'industry_mappings.csv'
    # EXCEPTION_LIST = ['26114', '26115', '26125', '25131', '25139', '26511', '26512', '26513', '27102', '27103', '27104', '27109', '28111', '28121', '28122', '28129', '28150', '28161', '28162', '28169', '28191', '28192', '28193', '28194', '28195', '28196', '28199', '28210', '28221', '28222', '28224', '28229']
    # filepath = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), TEST_FILE)
    #
    # with open(filepath, 'r') as f:
    #     csv_reader = csv.reader(f, delimiter=',')
    #     line_count = 0
    #
    #     for row in csv_reader:
    #         line_count += 1
    #
    #         # Skip headers
    #         if line_count == 1:
    #             continue
    #
    #         sector = row[0]
    #         industry = row[1]
    #         subindustry = row[2]
    #         ssic2010 = row[3]
    #         ssic2015 = row[4]
    #         ssic = ssic2015 if ssic2015 else ssic2010
    #
    #         if ssic in EXCEPTION_LIST:
    #             continue
    #
    #         assert (ssic, get_industry_mapping(ssic)) == (ssic, (sector, industry, subindustry))
    #
    # return True


    # assert get_industry_mapping('58110') == ('Services', 'Infocomm Media', 'Media & Digital Entertainment')
    # assert get_industry_mapping('74192') == ('Services', 'Infocomm Media', 'Media & Digital Entertainment')
    # assert get_industry_mapping('59131') == ('Services', 'Infocomm Media', 'Media & Digital Entertainment')
    # assert get_industry_mapping('46435') == ('Services', 'Infocomm Media', 'ICP')
    # assert get_industry_mapping('26115') == ('Manufacturing', 'Clean Energy', 'Clean Energy')
    # assert get_industry_mapping('27901') == ('Manufacturing', 'Clean Energy', 'Clean Energy')