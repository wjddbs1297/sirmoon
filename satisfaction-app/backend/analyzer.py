from typing import Optional


CHOICE_LABELS = ["매우 동의하지 않음", "동의하지 않음", "보통", "동의함", "매우 동의함"]
CHOICE_SCORES = [1, 2, 3, 4, 5]
POSITIVE_SCORES = {4, 5}


def _freq_table(values: list[Optional[int]]) -> dict:
    valid = [v for v in values if v is not None]
    total = len(valid)
    freq = {s: 0 for s in CHOICE_SCORES}
    for v in valid:
        if v in freq:
            freq[v] += 1
    rows = []
    for score, label in zip(CHOICE_SCORES, CHOICE_LABELS):
        count = freq[score]
        ratio = round(count / total * 100, 1) if total else 0.0
        rows.append({"label": label, "score": score, "count": count, "ratio": ratio})
    avg = round(sum(valid) / total, 2) if total else 0.0
    positive_rate = round(sum(1 for v in valid if v in POSITIVE_SCORES) / total * 100, 1) if total else 0.0
    return {"rows": rows, "avg": avg, "positive_rate": positive_rate, "total": total}


def analyze(parsed: dict) -> dict:
    responses = parsed["responses"]
    questions = parsed["questions"]
    total = parsed["total_count"]

    # Gender distribution
    gender_counts: dict[str, int] = {}
    for r in responses:
        g = r.get("gender") or "미기재"
        gender_counts[g] = gender_counts.get(g, 0) + 1

    gender_stats = {
        g: {"count": c, "ratio": round(c / total * 100, 1) if total else 0.0}
        for g, c in gender_counts.items()
    }

    # Per-question stats
    question_stats = []
    all_scores: list[float] = []
    all_positive: list[bool] = []

    for q in questions:
        values = [r["scores"].get(q) for r in responses]
        stats = _freq_table(values)
        question_stats.append({"question": q, **stats})
        valid_vals = [v for v in values if v is not None]
        all_scores.extend(valid_vals)
        all_positive.extend([v in POSITIVE_SCORES for v in valid_vals])

    overall_avg = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0
    overall_positive_rate = round(sum(all_positive) / len(all_positive) * 100, 1) if all_positive else 0.0

    male_count = gender_counts.get("남", 0)
    female_count = gender_counts.get("여", 0)

    return {
        "total": total,
        "male_count": male_count,
        "female_count": female_count,
        "gender_stats": gender_stats,
        "overall_avg": overall_avg,
        "overall_positive_rate": overall_positive_rate,
        "question_stats": question_stats,
        "questions": questions,
    }
