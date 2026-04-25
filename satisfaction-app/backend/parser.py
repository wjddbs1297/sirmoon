import pandas as pd
import re
from typing import Optional


SCORE_MAP = {
    "매우 동의함": 5,
    "동의함": 4,
    "보통": 3,
    "동의하지 않음": 2,
    "매우 동의하지 않음": 1,
    "매우동의함": 5,
    "동의하지않음": 2,
    "매우동의하지않음": 1,
}

GENDER_LABELS = {"남": "남", "여": "여", "남성": "남", "여성": "여", "male": "남", "female": "여"}


def _is_likert_column(series: pd.Series) -> bool:
    values = series.dropna().astype(str).str.strip()
    if len(values) == 0:
        return False
    matched = values.isin(SCORE_MAP.keys()).sum()
    return matched / len(values) >= 0.5


def _is_gender_column(col_name: str, series: pd.Series) -> bool:
    if re.search(r"성별|gender", str(col_name), re.IGNORECASE):
        return True
    values = series.dropna().astype(str).str.strip().str.lower()
    gender_tokens = {"남", "여", "남성", "여성", "male", "female"}
    matched = values.isin(gender_tokens).sum()
    return len(values) > 0 and matched / len(values) >= 0.7


def parse_xlsx(file_bytes: bytes) -> dict:
    import io
    raw = pd.read_excel(io.BytesIO(file_bytes), header=None)

    # Detect header format:
    # - Standard Google Forms: Row 0 = question text, Row 1+ = data
    # - Custom two-row format: Row 0 = meta names, Row 1 = question text, Row 2+ = data
    header_row = raw.iloc[0].fillna("").astype(str).str.strip()
    if len(raw) > 1:
        row1 = raw.iloc[1].fillna("").astype(str).str.strip()
        likert_hits = row1.isin(set(SCORE_MAP.keys())).sum()
        if likert_hits >= 2:
            # Standard single-header: row 0 is question text, row 1+ is data
            question_row = header_row
            data = raw.iloc[1:].reset_index(drop=True)
        else:
            # Two-row header: row 1 is question text, row 2+ is data
            question_row = row1
            data = raw.iloc[2:].reset_index(drop=True)
    else:
        question_row = header_row
        data = raw.iloc[1:].reset_index(drop=True)
    data.columns = range(len(data.columns))

    likert_cols = []
    gender_col: Optional[int] = None
    free_text_col: Optional[int] = None

    for idx in range(len(data.columns)):
        col_series = data[idx]
        col_header = header_row.iloc[idx] if idx < len(header_row) else ""
        q_text = question_row.iloc[idx] if idx < len(question_row) else ""

        if _is_gender_column(col_header, col_series) and gender_col is None:
            gender_col = idx
            continue

        if _is_likert_column(col_series):
            label = q_text if q_text and q_text.lower() not in ("nan", "") else col_header
            likert_cols.append({"col_idx": idx, "label": label})
        elif idx > 3 and free_text_col is None:
            is_free_header = re.search(r"자유|주관|의견|기타|free|comment", str(col_header), re.IGNORECASE)
            valid_vals = col_series.dropna().astype(str)
            mean_len = valid_vals.str.len().mean() if len(valid_vals) > 0 else 0
            if is_free_header or mean_len > 5:
                free_text_col = idx

    # Build responses list
    responses = []
    for _, row in data.iterrows():
        entry: dict = {}
        if gender_col is not None:
            raw_gender = str(row[gender_col]).strip()
            entry["gender"] = GENDER_LABELS.get(raw_gender, raw_gender)
        else:
            entry["gender"] = None

        scores = {}
        for q in likert_cols:
            raw_val = str(row[q["col_idx"]]).strip()
            score = SCORE_MAP.get(raw_val)
            scores[q["label"]] = score
        entry["scores"] = scores

        if free_text_col is not None:
            val = str(row[free_text_col]).strip()
            entry["free_text"] = val if val.lower() not in ("nan", "", "none") else None
        else:
            entry["free_text"] = None

        responses.append(entry)

    questions = [q["label"] for q in likert_cols]
    free_texts = [r["free_text"] for r in responses if r.get("free_text")]

    return {
        "questions": questions,
        "responses": responses,
        "free_texts": free_texts,
        "total_count": len(responses),
    }
