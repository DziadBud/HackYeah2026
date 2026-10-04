-- direct signups from an innovation page have no problem report
ALTER TABLE test_signups ALTER COLUMN problem_report_id DROP NOT NULL;
