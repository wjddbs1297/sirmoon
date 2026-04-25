import os
import json
import anthropic
from typing import Optional

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    return _client


def _default_comments(stats: dict, questions: list[str], free_texts: list[str]) -> dict:
    question_comments = {}
    for q_stat in stats["question_stats"]:
        q = q_stat["question"]
        avg = q_stat["avg"]
        pr = q_stat["positive_rate"]
        question_comments[q] = (
            f"해당 문항의 평균 점수는 {avg}점(5점 만점)이며, "
            f"긍정 응답률은 {pr}%입니다. "
            f"참여자들의 전반적인 반응이 긍정적으로 나타났습니다."
        )

    free_text_comment = (
        f"총 {len(free_texts)}건의 자유응답이 수집되었습니다. "
        "참여자들은 프로그램에 대해 다양한 의견을 제시하였으며, "
        "전반적으로 긍정적인 경험을 공유하였습니다. "
        "수집된 의견은 향후 프로그램 개선에 반영될 예정입니다."
    )

    overall_comment = (
        f"전체 평균 점수는 {stats['overall_avg']}점(5점 만점)이며, "
        f"긍정 응답률은 {stats['overall_positive_rate']}%로 나타났습니다. "
        f"총 {stats['total']}명의 참여자가 설문에 응답하였습니다. "
        "본 프로그램은 전반적으로 참여자들에게 긍정적인 경험을 제공한 것으로 평가됩니다."
    )

    return {
        "question_comments": question_comments,
        "free_text_comment": free_text_comment,
        "overall_comment": overall_comment,
    }


def generate_comments(
    program_name: str,
    program_purpose: str,
    program_goal: str,
    stats: dict,
    free_texts: list[str],
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _default_comments(stats, stats["questions"], free_texts)

    questions_summary = []
    for q_stat in stats["question_stats"]:
        questions_summary.append(
            f'- 문항: "{q_stat["question"]}" | 평균: {q_stat["avg"]}점 | 긍정응답률: {q_stat["positive_rate"]}%'
        )

    free_text_sample = "\n".join(f"  - {t}" for t in free_texts[:20]) if free_texts else "없음"

    prompt = f"""다음은 프로그램 만족도 설문 결과입니다. 분석 코멘트를 JSON으로 작성해 주세요.

프로그램명: {program_name}
프로그램 목적: {program_purpose}
프로그램 목표: {program_goal}

전체 응답자: {stats['total']}명 (남: {stats['male_count']}명, 여: {stats['female_count']}명)
전체 평균: {stats['overall_avg']}점 / 전체 긍정응답률: {stats['overall_positive_rate']}%

문항별 결과:
{chr(10).join(questions_summary)}

자유응답 샘플 (최대 20건):
{free_text_sample}

아래 JSON 형식으로만 응답해 주세요. 각 코멘트는 한국어, 긍정적 톤으로 작성하고 구체적인 수치를 포함하세요.

{{
  "question_comments": {{
    "<문항텍스트>": "<2~3문장 코멘트>",
    ...
  }},
  "free_text_comment": "<3~4문장 자유응답 요약>",
  "overall_comment": "<3~4문장 전체 총평>"
}}"""

    try:
        client = _get_client()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        return json.loads(raw)
    except Exception:
        return _default_comments(stats, stats["questions"], free_texts)
