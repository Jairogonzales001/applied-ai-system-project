from evaluate import EVALUATION_CASES, evaluate_case, run_evaluation


def test_all_evaluation_cases_pass():
    results = [
        evaluate_case(case)[0]
        for case in EVALUATION_CASES
    ]

    assert all(results)


def test_evaluation_summary():
    summary = run_evaluation()

    assert summary["total"] == len(EVALUATION_CASES)
    assert summary["passed"] == len(EVALUATION_CASES)
    assert summary["reliability_score"] == 100.0