import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date


PIE_COLORS = ["#3A86FF", "#52B788", "#F9C74F", "#F4845F", "#E63946"]
COMMENT_BG = colors.HexColor("#F0F4FF")
COMMENT_BORDER = colors.HexColor("#3A86FF")
OVERALL_BORDER = colors.HexColor("#1A3A8F")
HEADER_BG = colors.HexColor("#3A86FF")
CARD_BG = colors.HexColor("#F8FAFF")

_FONT_REGISTERED = False
_FONT_NAME = "NanumGothic"


def _register_font():
    global _FONT_REGISTERED, _FONT_NAME
    if _FONT_REGISTERED:
        return
    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("NanumGothic", path))
            pdfmetrics.registerFont(TTFont("NanumGothicBold", path.replace("NanumGothic.ttf", "NanumGothicBold.ttf") if os.path.exists(path.replace("NanumGothic.ttf", "NanumGothicBold.ttf")) else path))
            _FONT_NAME = "NanumGothic"
            _FONT_REGISTERED = True
            return
    _FONT_NAME = "Helvetica"
    _FONT_REGISTERED = True


def _get_mpl_font():
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return fm.FontProperties(fname=p)
    return fm.FontProperties()


def _make_pie_chart(labels: list, sizes: list, title: str, width_mm: float = 70) -> io.BytesIO:
    mpl_font = _get_mpl_font()
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    if not filtered:
        filtered = [("데이터 없음", 1)]
    fl, fs = zip(*filtered)
    clrs = PIE_COLORS[: len(fl)]
    wedges, texts, autotexts = ax.pie(
        fs,
        labels=None,
        colors=clrs,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        startangle=90,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for t in autotexts:
        t.set_fontproperties(mpl_font)
        t.set_fontsize(8)
        t.set_color("white")
        t.set_fontweight("bold")
    ax.legend(
        wedges,
        fl,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=min(3, len(fl)),
        prop=mpl_font,
        fontsize=7,
        frameon=False,
    )
    ax.set_title(title, fontproperties=mpl_font, fontsize=9, pad=8)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", transparent=False)
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_bar_chart(questions: list[str], avgs: list[float]) -> io.BytesIO:
    mpl_font = _get_mpl_font()
    n = len(questions)
    fig_h = max(3.0, n * 0.45 + 1.0)
    fig, ax = plt.subplots(figsize=(7.0, fig_h))
    short_labels = [q[:20] + "…" if len(q) > 20 else q for q in questions]
    bars = ax.barh(short_labels, avgs, color="#3A86FF", edgecolor="white", height=0.6)
    ax.set_xlim(0, 5.5)
    ax.axvline(x=5, color="#E63946", linestyle="--", linewidth=0.8, alpha=0.6)
    for bar, val in zip(bars, avgs):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontproperties=mpl_font, fontsize=8)
    ax.set_xlabel("평균 점수 (5점 만점)", fontproperties=mpl_font, fontsize=9)
    ax.tick_params(axis="y", labelsize=8)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(mpl_font)
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(mpl_font)
    ax.set_title("문항별 평균 점수 한눈에 보기", fontproperties=mpl_font, fontsize=11, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _styles():
    _register_font()
    f = _FONT_NAME
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontName=f, fontSize=20, textColor=colors.white, leading=26, spaceAfter=4, alignment=1),
        "subtitle": ParagraphStyle("subtitle", fontName=f, fontSize=11, textColor=colors.white, leading=14, alignment=1),
        "section": ParagraphStyle("section", fontName=f, fontSize=13, textColor=colors.HexColor("#1A3A8F"), leading=18, spaceBefore=14, spaceAfter=6, fontWeight="bold"),
        "body": ParagraphStyle("body", fontName=f, fontSize=9, textColor=colors.HexColor("#333333"), leading=14),
        "comment": ParagraphStyle("comment", fontName=f, fontSize=9, textColor=colors.HexColor("#1A3A8F"), leading=14),
        "overall": ParagraphStyle("overall", fontName=f, fontSize=10, textColor=colors.HexColor("#0D1F5C"), leading=16),
        "free_item": ParagraphStyle("free_item", fontName=f, fontSize=8, textColor=colors.HexColor("#555555"), leading=12, leftIndent=6),
        "card_val": ParagraphStyle("card_val", fontName=f, fontSize=16, textColor=colors.HexColor("#1A3A8F"), leading=20, alignment=1, fontWeight="bold"),
        "card_label": ParagraphStyle("card_label", fontName=f, fontSize=8, textColor=colors.HexColor("#666666"), leading=10, alignment=1),
    }


def _comment_box(text: str, style_map: dict, is_overall: bool = False) -> Table:
    border_color = OVERALL_BORDER if is_overall else COMMENT_BORDER
    style_key = "overall" if is_overall else "comment"
    prefix = "💡 총평  " if is_overall else "💬 AI 분석  "
    cell = Paragraph(f"<b>{prefix}</b>{text}", style_map[style_key])
    t = Table([[cell]], colWidths=[155 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COMMENT_BG),
        ("BOX", (0, 0), (-1, -1), 1.5, border_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COMMENT_BG]),
    ]))
    return t


def _freq_table_flowable(rows: list, style_map: dict) -> Table:
    header = [
        Paragraph("<b>구분</b>", style_map["body"]),
        Paragraph("<b>빈도</b>", style_map["body"]),
        Paragraph("<b>비율</b>", style_map["body"]),
    ]
    data = [header]
    for r in rows:
        data.append([
            Paragraph(r["label"], style_map["body"]),
            Paragraph(str(r["count"]), style_map["body"]),
            Paragraph(f"{r['ratio']}%", style_map["body"]),
        ])
    t = Table(data, colWidths=[75 * mm, 25 * mm, 25 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE8FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FF")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _gender_table_flowable(gender_stats: dict, style_map: dict) -> Table:
    header = [
        Paragraph("<b>성별</b>", style_map["body"]),
        Paragraph("<b>빈도</b>", style_map["body"]),
        Paragraph("<b>비율</b>", style_map["body"]),
    ]
    data = [header]
    for g, s in gender_stats.items():
        data.append([
            Paragraph(g, style_map["body"]),
            Paragraph(str(s["count"]), style_map["body"]),
            Paragraph(f"{s['ratio']}%", style_map["body"]),
        ])
    t = Table(data, colWidths=[75 * mm, 25 * mm, 25 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE8FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FF")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_pdf(
    program_name: str,
    program_purpose: str,
    program_goal: str,
    stats: dict,
    ai_comments: dict,
    free_texts: list[str],
) -> bytes:
    _register_font()
    s = _styles()
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    story = []

    # ── Header Banner ──────────────────────────────────────────────
    header_data = [[
        Paragraph(f"만족도 조사 분석 보고서", s["title"]),
    ]]
    header_table = Table(header_data, colWidths=[174 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 3 * mm))

    sub_data = [[
        Paragraph(f"{program_name}  |  작성일: {date.today().strftime('%Y년 %m월 %d일')}  |  총 응답자: {stats['total']}명", s["subtitle"])
    ]]
    sub_table = Table(sub_data, colWidths=[174 * mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1A3A8F")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 6 * mm))

    # ── Summary Cards ─────────────────────────────────────────────
    story.append(Paragraph("■ 핵심 지표 요약", s["section"]))
    card_items = [
        ("총 참가자", f"{stats['total']}명"),
        ("남학생", f"{stats['male_count']}명"),
        ("여학생", f"{stats['female_count']}명"),
        ("전체 평균", f"{stats['overall_avg']}점"),
        ("긍정응답률", f"{stats['overall_positive_rate']}%"),
    ]
    card_cells = []
    for label, val in card_items:
        cell = Table(
            [[Paragraph(val, s["card_val"])], [Paragraph(label, s["card_label"])]],
            colWidths=[30 * mm],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#AABFFF")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        card_cells.append(cell)
    card_row = Table([card_cells], colWidths=[34 * mm] * 5)
    card_row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
    story.append(card_row)
    story.append(Spacer(1, 6 * mm))

    # ── Bar chart overview ─────────────────────────────────────────
    story.append(Paragraph("■ 문항별 평균 점수", s["section"]))
    questions = stats["questions"]
    avgs = [q["avg"] for q in stats["question_stats"]]
    bar_buf = _make_bar_chart(questions, avgs)
    bar_img = Image(bar_buf, width=165 * mm, height=None)
    bar_img.drawHeight = bar_img.drawWidth * (max(3.0, len(questions) * 0.45 + 1.0) / 7.0)
    story.append(bar_img)
    story.append(Spacer(1, 6 * mm))

    # ── Gender ────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDE8FF")))
    story.append(Paragraph("■ 성별 분포", s["section"]))
    gender_stats = stats["gender_stats"]
    glabels = list(gender_stats.keys())
    gsizes = [gender_stats[g]["count"] for g in glabels]
    pie_buf = _make_pie_chart(glabels, gsizes, "성별 분포")
    pie_img = Image(pie_buf, width=60 * mm, height=55 * mm)
    g_table_flow = _gender_table_flowable(gender_stats, s)
    gender_row = Table(
        [[pie_img, g_table_flow]],
        colWidths=[68 * mm, 106 * mm],
    )
    gender_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([gender_row]))
    story.append(Spacer(1, 4 * mm))

    # ── Per-question sections ─────────────────────────────────────
    q_comments = ai_comments.get("question_comments", {})
    for i, q_stat in enumerate(stats["question_stats"], 1):
        q = q_stat["question"]
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDE8FF")))
        story.append(Paragraph(f"■ 문항 {i}: {q}", s["section"]))

        labels = [r["label"] for r in q_stat["rows"]]
        sizes = [r["count"] for r in q_stat["rows"]]
        pie_buf = _make_pie_chart(labels, sizes, f"문항 {i}")
        pie_img = Image(pie_buf, width=60 * mm, height=55 * mm)
        freq_flow = _freq_table_flowable(q_stat["rows"], s)

        stat_row = Table(
            [[pie_img, freq_flow]],
            colWidths=[68 * mm, 106 * mm],
        )
        stat_row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))

        avg_text = Paragraph(
            f"평균 점수: <b>{q_stat['avg']}점</b> / 5점 만점 &nbsp;&nbsp; 긍정응답률: <b>{q_stat['positive_rate']}%</b>",
            s["body"],
        )
        comment_text = q_comments.get(q, f"평균 점수 {q_stat['avg']}점으로 긍정적인 반응을 보였습니다.")
        comment_box = _comment_box(comment_text, s)

        story.append(KeepTogether([stat_row, Spacer(1, 2 * mm), avg_text, Spacer(1, 3 * mm), comment_box, Spacer(1, 4 * mm)]))

    # ── Free text ─────────────────────────────────────────────────
    if free_texts:
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDE8FF")))
        story.append(Paragraph("■ 자유응답 목록", s["section"]))
        for idx, ft in enumerate(free_texts, 1):
            story.append(Paragraph(f"{idx}. {ft}", s["free_item"]))
            story.append(Spacer(1, 1 * mm))
        story.append(Spacer(1, 3 * mm))
        ft_comment = ai_comments.get("free_text_comment", "자유응답을 통해 다양한 의견이 수집되었습니다.")
        story.append(_comment_box(ft_comment, s))
        story.append(Spacer(1, 4 * mm))

    # ── Overall summary ───────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=2, color=OVERALL_BORDER))
    story.append(Paragraph("■ 전체 총평", s["section"]))
    overall_text = ai_comments.get("overall_comment", f"전체 평균 {stats['overall_avg']}점으로 프로그램이 긍정적으로 평가되었습니다.")
    story.append(_comment_box(overall_text, s, is_overall=True))

    doc.build(story)
    buf.seek(0)
    return buf.read()
