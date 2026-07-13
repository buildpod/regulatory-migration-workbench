import unittest

from app.quality import analyse_csv, parse_csv


SAMPLE = """application_id,product_name,approval_date,owner
APP-001,Cardiovex,2026-03-15,Regulatory
APP-001,Cardiovex,2026-03-15,Regulatory
 APP-002 ,Cardiovex,not-a-date,
"""


class QualityTests(unittest.TestCase):
    def test_parse_csv_strips_headers_and_values(self):
        headers, rows = parse_csv(" application_id , status\n APP-001 , Active\n")
        self.assertEqual(headers, ["application_id", "status"])
        self.assertEqual(rows[0], {"application_id": "APP-001", "status": "Active"})

    def test_analysis_reports_duplicates_missing_values_and_invalid_dates(self):
        result = analyse_csv(SAMPLE, "sample.csv")
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(len(result["duplicates"]), 1)
        issue_types = {issue["issue_type"] for issue in result["issues"]}
        self.assertIn("duplicate-candidate", issue_types)
        self.assertIn("missing-values", issue_types)
        self.assertIn("invalid-date", issue_types)
        self.assertEqual(len(result["fair_assessment"]), 4)

    def test_source_hash_is_stable_for_same_content(self):
        first = analyse_csv(SAMPLE, "one.csv")
        second = analyse_csv(SAMPLE, "two.csv")
        self.assertEqual(first["source_sha256"], second["source_sha256"])

    def test_analysis_separates_normalized_duplicate_candidates(self):
        result = analyse_csv("id,name\n1,Alpha\n 1 , alpha \n", "likely.csv")
        self.assertEqual(result["duplicates"][0]["kind"], "likely")


if __name__ == "__main__":
    unittest.main()
