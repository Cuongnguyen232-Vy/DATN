# -*- coding: utf-8 -*-
"""
Script: Generate Formal Word Reports (.docx) for Thesis Chapters 1 & 2
PTIT Graduation Thesis Standard Format
Author: Nguyễn Mạnh Cường - B22DCCN099
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


def clean_xml_string(s):
    """Loại bỏ ký tự điều khiển XML không hợp lệ"""
    if not isinstance(s, str):
        return str(s)
    return "".join(c for c in s if ord(c) >= 32 or c in ("\t", "\n", "\r"))


def set_cell_background(cell, fill_hex):
    """Tô màu nền cho cell trong bảng"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề trong của cell (dxf)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def apply_ptit_page_setup(doc):
    """Thiết lập kích thước trang và căn lề chuẩn PTIT (Top: 2cm, Bottom: 2cm, Left: 3cm, Right: 2cm)"""
    for section in doc.sections:
        section.page_width = Inches(8.27)    # A4 Width: 21.0 cm
        section.page_height = Inches(11.69)  # A4 Height: 29.7 cm
        section.top_margin = Inches(0.79)    # 2.0 cm
        section.bottom_margin = Inches(0.79) # 2.0 cm
        section.left_margin = Inches(1.18)   # 3.0 cm
        section.right_margin = Inches(0.79)  # 2.0 cm

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG — KHOA CNTT 1")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.italic = True
        hrun.font.color.rgb = RGBColor(120, 120, 120)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Nguyễn Mạnh Cường (B22DCCN099) — Báo cáo tiến độ Khóa luận tốt nghiệp")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.italic = True
        frun.font.color.rgb = RGBColor(120, 120, 120)


def add_cover_box(doc, chapter_title):
    """Tạo khung bìa báo cáo tiến độ chuẩn PTIT"""
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG\nKHOA CÔNG NGHỆ THÔNG TIN 1\n")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(12)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(180, 0, 0)
    p_inst.paragraph_format.space_after = Pt(4)
    p_inst.paragraph_format.space_before = Pt(0)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("-------------------***-------------------")
    r_div.font.name = "Times New Roman"
    r_div.font.size = Pt(10)
    r_div.font.color.rgb = RGBColor(150, 150, 150)
    p_div.paragraph_format.space_after = Pt(18)

    p_rpt = doc.add_paragraph()
    p_rpt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rpt = p_rpt.add_run("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC")
    r_rpt.font.name = "Times New Roman"
    r_rpt.font.size = Pt(15)
    r_rpt.font.bold = True
    r_rpt.font.color.rgb = RGBColor(0, 32, 96)
    p_rpt.paragraph_format.space_after = Pt(6)

    p_chap = doc.add_paragraph()
    p_chap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_chap = p_chap.add_run(chapter_title)
    r_chap.font.name = "Times New Roman"
    r_chap.font.size = Pt(13.5)
    r_chap.font.bold = True
    r_chap.font.color.rgb = RGBColor(180, 0, 0)
    p_chap.paragraph_format.space_after = Pt(14)

    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    data = [
        ("Tên đề tài:", "Xây dựng hệ thống hỗ trợ ra quyết định giao dịch tài chính sử dụng dữ liệu chuỗi thời gian"),
        ("Sinh viên thực hiện:", "Nguyễn Mạnh Cường"),
        ("Mã sinh viên / Lớp:", "B22DCCN099   |   Lớp: D22CNPM02"),
        ("Ngành đào tạo:", "Công nghệ thông tin (Hệ Đại học chính quy 2022 - 2027)"),
        ("Giảng viên hướng dẫn:", "ThS. / TS. (Bộ môn Công nghệ Phần mềm)"),
    ]

    col_widths = [Inches(1.8), Inches(4.5)]
    for row_idx, (label, val) in enumerate(data):
        row = table.rows[row_idx]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = col_widths[0]
        c1.width = col_widths[1]

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        p0.paragraph_format.space_before = Pt(2)
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        r0.font.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_before = Pt(2)
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        if row_idx == 0:
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(0, 32, 96)

        set_cell_background(c0, "F8F9FA")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(14)
    p_loc.paragraph_format.space_after = Pt(20)
    r_loc = p_loc.add_run("Hà Nội — Năm học 2026")
    r_loc.font.name = "Times New Roman"
    r_loc.font.size = Pt(10.5)
    r_loc.font.italic = True
    r_loc.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_page_break()


def add_abbreviations_table(doc):
    """Thêm danh mục các ký hiệu và chữ viết tắt chuẩn PTIT"""
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("DANH MỤC CÁC KÝ HIỆU VÀ TỪ VIẾT TẮT")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(13)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0, 32, 96)

    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["STT", "Từ viết tắt", "Diễn giải tiếng Việt / Định nghĩa chuyên môn"]
    widths = [Inches(0.6), Inches(1.5), Inches(4.2)]

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].width = widths[i]
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.space_before = Pt(3)
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.bold = True
        set_cell_background(hdr_cells[i], "EAECEF")
        set_cell_margins(hdr_cells[i], top=80, bottom=80, left=100, right=100)

    abbr_data = [
        ("AI", "Artificial Intelligence — Trí tuệ nhân tạo"),
        ("ATR", "Average True Range — Độ biến động thực tế trung bình"),
        ("BiGRU", "Bidirectional Gated Recurrent Unit — Mạng nơ-ron hồi quy 2 chiều"),
        ("CNN", "Convolutional Neural Network — Mạng nơ-ron tích chập 1 chiều (1D-CNN)"),
        ("DCA", "Dollar-Cost Averaging — Chiến lược quản lý vốn trung bình giá"),
        ("DXY", "US Dollar Index — Chỉ số sức mạnh đồng Đô la Mỹ"),
        ("EA", "Expert Advisor — Robot phần mềm giao dịch tự động trên MetaTrader"),
        ("EMA", "Exponential Moving Average — Đường trung bình động hàm mũ"),
        ("FinBERT", "Financial Bidirectional Encoder Representations from Transformers"),
        ("IPC", "Inter-Process Communication — Cơ chế giao tiếp liên tiến trình"),
        ("KNN", "K-Nearest Neighbors — Thuật toán K láng giềng gần nhất"),
        ("MACD", "Moving Average Convergence Divergence — Chỉ báo hội tụ phân kỳ"),
        ("MDD", "Maximum Drawdown — Mức sụt giảm tài khoản tối đa"),
        ("MQL5", "MetaQuotes Language 5 — Ngôn ngữ lập trình hướng đối tượng trên MT5"),
        ("MT5", "MetaTrader 5 — Nền tảng giao dịch tài chính đa tài sản quốc tế"),
        ("MHA", "Multi-Head Attention — Cơ chế chú ý đa đầu"),
        ("NLP", "Natural Language Processing — Xử lý ngôn ngữ tự nhiên"),
        ("NFP", "Non-Farm Payrolls — Báo cáo việc làm phi nông nghiệp Mỹ"),
        ("OHLCV", "Open, High, Low, Close, Volume — Dữ liệu giá nến và khối lượng"),
        ("ROC", "Rate of Change — Chỉ báo tốc độ thay đổi giá"),
        ("RSI", "Relative Strength Index — Chỉ số sức mạnh tương đối"),
        ("VADER", "Valence Aware Dictionary and sEntiment Reasoner"),
        ("XAU/USD", "Tỷ giá Vàng giao ngay (Gold Spot) tính bằng Đô la Mỹ (USD)")
    ]

    for idx, (abbr, desc) in enumerate(abbr_data, 1):
        row = table.add_row()
        cells = row.cells
        cells[0].width = widths[0]
        cells[1].width = widths[1]
        cells[2].width = widths[2]

        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = cells[0].paragraphs[0].add_run(str(idx))
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)

        r1 = cells[1].paragraphs[0].add_run(abbr)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.bold = True

        r2 = cells[2].paragraphs[0].add_run(desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)

        bg = "FFFFFF" if idx % 2 == 1 else "F8F9FA"
        for c in cells:
            set_cell_background(c, bg)
            set_cell_margins(c, top=40, bottom=40, left=80, right=80)

    doc.add_page_break()


def format_body_paragraph(p, text, is_intro=False):
    """Định dạng đoạn văn chuẩn PTIT: Font Times 13pt, Giãn dòng 1.3, Thụt đầu dòng 1.0cm"""
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Inches(0.39)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\$[^\$]+\$)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(clean_xml_string(part[2:-2]))
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            run.font.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run = p.add_run(clean_xml_string(part[1:-1]))
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            run.font.italic = True
        elif part.startswith('$') and part.endswith('$'):
            math_content = part[1:-1]
            runs = parse_formula_to_runs(math_content)
            for m_text, is_sub, is_sup, is_italic, is_bold in runs:
                run = p.add_run(clean_xml_string(m_text))
                run.font.name = "Cambria Math"
                run.font.size = Pt(12)
                if is_sub:
                    run.font.subscript = True
                if is_sup:
                    run.font.superscript = True
                if is_italic:
                    run.font.italic = True
                if is_bold:
                    run.font.bold = True
        else:
            run = p.add_run(clean_xml_string(part))
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            if is_intro:
                run.font.italic = True


def format_heading(doc, text, level):
    """Định dạng các cấp tiêu đề chuẩn PTIT"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12 if level <= 2 else 8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Inches(0)

    clean_text = clean_xml_string(text)
    if level == 1:
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(clean_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 32, 96)
    elif level == 2:
        run = p.add_run(clean_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    elif level == 3:
        run = p.add_run(clean_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.italic = True
    elif level == 4:
        run = p.add_run(clean_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.italic = True
    return p


MATH_KEYWORDS = {
    'ReLU', 'Attention', 'softmax', 'LayerNorm', 'MultiHead', 'Sim', 'Sentiment',
    'Spacing', 'BaseSpacing', 'BaseLot', 'MaxLotLimit', 'BreakEven', 'Hedge',
    'Precision', 'Recall', 'Macro', 'Sharpe', 'Ratio', 'Drawdown', 'MDD', 'Equity',
    'High', 'Low', 'Close', 'OpenPrice', 'BUY', 'SELL', 'HOLD', 'XAU', 'USD',
    'Final', 'Attn', 'total', 'current', 'baseline', 'downside', 'tanh', 'max', 'min', 'log', 'exp',
    'Average', 'Gain', 'Loss', 'Score', 'SafeHaven', 'Netting', 'Hedging', 'TR', 'ATR', 'F1'
}


def clean_nested_frac(s):
    """Xử lý triệt để \\frac{A}{B} kể cả khi có ngoặc nhọn lồng nhau"""
    while r'\frac' in s:
        idx = s.find(r'\frac')
        start_num = s.find('{', idx)
        if start_num == -1:
            break
        depth = 0
        end_num = -1
        for i in range(start_num, len(s)):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    end_num = i
                    break
        if end_num == -1:
            break
            
        start_den = s.find('{', end_num)
        if start_den == -1:
            break
        depth = 0
        end_den = -1
        for i in range(start_den, len(s)):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    end_den = i
                    break
        if end_den == -1:
            break
            
        num = s[start_num+1:end_num].strip()
        den = s[start_den+1:end_den].strip()
        s = s[:idx] + f"({num}) / ({den})" + s[end_den+1:]
    return s


def clean_nested_sqrt(s):
    """Xử lý triệt để \\sqrt{A} kể cả khi có ngoặc nhọn lồng nhau"""
    while r'\sqrt' in s:
        idx = s.find(r'\sqrt')
        start = s.find('{', idx)
        if start == -1:
            break
        depth = 0
        end = -1
        for i in range(start, len(s)):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end == -1:
            break
        inner = s[start+1:end].strip()
        s = s[:idx] + f"√({inner})" + s[end+1:]
    return s


def parse_formula_to_runs(latex_str):
    """
    Phân tích chuỗi LaTeX thành danh sách các runs định dạng chuẩn cho Microsoft Word:
    (text, is_sub, is_sup, is_italic, is_bold)
    """
    s = str(latex_str).strip()

    # 0. Loại bỏ môi trường cases, aligned và text
    s = s.replace(r'\begin{cases}', '').replace(r'\end{cases}', '')
    s = s.replace(r'\begin{aligned}', '').replace(r'\end{aligned}', '')
    s = s.replace(r'\\', '\n')

    for _ in range(5):
        s = re.sub(r'\\(?:text|mathrm|mathbf)\s*\{([^{}]+)\}', r'\1', s)

    # Xử lý phân số và căn bậc hai trước khi thay thế ký hiệu
    s = clean_nested_frac(s)
    s = clean_nested_sqrt(s)

    # 1. Thay thế các toán tử và ký hiệu toán học
    replaces = [
        (r'\left(', '('), (r'\right)', ')'),
        (r'\left[', '['), (r'\right]', ']'),
        (r'\left|', '|'), (r'\right|', '|'),
        (r'\left.', ''), (r'\right.', ''),
        (r'\,', ' '), (r'\quad', '   '), (r'\qquad', '      '),
        (r'\times', ' × '), (r'\cdot', ' · '), (r'\odot', ' ⊙ '),
        (r'\sigma', 'σ'), (r'\alpha', 'α'), (r'\beta', 'β'), (r'\gamma', 'γ'),
        (r'\Delta', 'Δ'), (r'\tau', 'τ'), (r'\mathbb{E}', 'E'), (r'\mathbb{R}', 'ℝ'),
        (r'\approx', '≈'), (r'\ge', '≥'), (r'\le', '≤'), (r'\ne', '≠'),
        (r'\sum', '∑'), (r'\max', 'max'), (r'\min', 'min'),
        (r'\tanh', 'tanh'), (r'\log', 'log'), (r'\ln', 'ln'),
        (r'\tilde{h}', 'h̃'), (r'\tilde', '~'),
        (r'\hat{y}', 'ŷ'), (r'\hat', '^'),
        (r'\overrightarrow{h}', 'h⃗'), (r'\overleftarrow{h}', 'h⃖'), (r'\vec{h}', 'h⃗'),
        (r'\bar{p}', 'p̄'), (r'\bar{P}', 'P̄'), (r'\bar{Q}', 'Q̄'), (r'\bar{q}', 'q̄'),
        (r'\mathcal{L}', 'L'), (r'\|', '‖'),
    ]
    for p, r in replaces:
        s = s.replace(p, r)

    # Dọn dẹp lệnh LaTeX còn sót lại
    s = re.sub(r'\\[a-zA-Z]+', '', s)

    # 2. Tokenize với Subscript và Superscript
    token_pattern = re.compile(
        r'(?P<sub>_\{[^{}]+\}|_[a-zA-Z0-9]+)|'
        r'(?P<sup>\^\{[^{}]+\}|\^[a-zA-Z0-9]+)|'
        r'(?P<word>[a-zA-Z]+)|'
        r'(?P<other>[^a-zA-Z_\^]+)'
    )

    runs = []
    for m in token_pattern.finditer(s):
        if m.group('sub'):
            sub_val = m.group('sub')[1:]
            if sub_val.startswith('{') and sub_val.endswith('}'):
                sub_val = sub_val[1:-1]
            runs.append((sub_val, True, False, False, False))
        elif m.group('sup'):
            sup_val = m.group('sup')[1:]
            if sup_val.startswith('{') and sup_val.endswith('}'):
                sup_val = sup_val[1:-1]
            runs.append((sup_val, False, True, False, False))
        elif m.group('word'):
            word = m.group('word')
            if word in MATH_KEYWORDS:
                runs.append((word, False, False, False, False))
            elif len(word) == 1:
                runs.append((word, False, False, True, False))
            else:
                runs.append((word, False, False, False, False))
        elif m.group('other'):
            runs.append((m.group('other'), False, False, False, False))

    return runs


def clean_latex_formula(s):
    """Hàm tương thích ngược"""
    runs = parse_formula_to_runs(s)
    return "".join(r[0] for r in runs)


def add_math_formula(doc, formula_text, eq_number=None):
    """
    Thêm công thức toán học chuẩn quy cách đồ án tốt nghiệp PTIT:
    Sử dụng cơ chế Tab Stop (Center Tab ở 3.15 in, Right Tab ở 6.30 in)
    - Loại bỏ hoàn toàn Table để công thức tận dụng trọn vẹn bề ngang trang (6.30 inch)
    - Công thức KHÔNG BAO GIỜ bị ép co hẹp hay rớt dòng vụn vặt
    - Số công thức căn đều sát lề phải chuẩn IEEE/PTIT
    """
    if not formula_text or not formula_text.strip():
        return

    lines = [l.strip() for l in formula_text.split('\n') if l.strip()]
    if not lines:
        return

    for idx, line in enumerate(lines):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.space_before = Pt(3 if idx > 0 else 6)
        p.paragraph_format.space_after = Pt(3 if idx < len(lines) - 1 else 6)

        tab_stops = p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Inches(3.15), WD_TAB_ALIGNMENT.CENTER)
        tab_stops.add_tab_stop(Inches(6.30), WD_TAB_ALIGNMENT.RIGHT)

        p.add_run('\t')
        runs = parse_formula_to_runs(line)
        for text, is_sub, is_sup, is_italic, is_bold in runs:
            r = p.add_run(clean_xml_string(text))
            r.font.name = "Cambria Math"
            r.font.size = Pt(12)
            if is_sub:
                r.font.subscript = True
            if is_sup:
                r.font.superscript = True
            if is_italic:
                r.font.italic = True
            if is_bold:
                r.font.bold = True

        # Đánh số công thức ở dòng đầu tiên (hoặc dòng duy nhất)
        if eq_number and idx == 0:
            p.add_run('\t')
            r_num = p.add_run(eq_number)
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(12)


def add_image_figure(doc, img_path, caption, width_inch=5.5):
    """Chèn hình ảnh kèm chú thích chuẩn PTIT"""
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.first_line_indent = Inches(0)
        p_img.add_run().add_picture(img_path, width=Inches(width_inch))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        p_cap.paragraph_format.first_line_indent = Inches(0)
        rcap = p_cap.add_run(clean_xml_string(caption))
        rcap.font.name = "Times New Roman"
        rcap.font.size = Pt(11)
        rcap.font.bold = True
        rcap.font.italic = True


def parse_and_write_markdown(doc, md_file_path, chapter_num=1):
    """Phân tích Markdown và chuyển thành tài liệu Word chuẩn tắc"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    in_math_block = False
    math_buffer = []
    table_buffer = []
    formula_count = 0

    def flush_math():
        nonlocal math_buffer, formula_count
        if math_buffer:
            combined = "\n".join(math_buffer)
            formula_count += 1
            eq_num = f"({chapter_num}.{formula_count})"
            add_math_formula(doc, combined, eq_number=eq_num)
            math_buffer = []

    def flush_table():
        nonlocal table_buffer
        if not table_buffer:
            return
        rows_data = []
        for r_line in table_buffer:
            if re.match(r'^\|[\s\:\-]+(?:\|[\s\:\-]+)+\|$', r_line):
                continue
            cells = [c.strip() for c in r_line.strip('|').split('|')]
            if cells:
                rows_data.append(cells)
        table_buffer = []
        if not rows_data:
            return

        num_rows = len(rows_data)
        num_cols = max(len(r) for r in rows_data)
        tbl = doc.add_table(rows=num_rows, cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = True

        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                if c_idx >= num_cols:
                    break
                cell = tbl.rows[r_idx].cells[c_idx]
                set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.first_line_indent = Inches(0)
                if r_idx == 0:
                    set_cell_background(cell, "F0F4F8")
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    val_clean = val.replace('**', '')
                    run = p.add_run(clean_xml_string(val_clean))
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(10.5)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0, 32, 96)
                else:
                    if r_idx % 2 == 1:
                        set_cell_background(cell, "FFFFFF")
                    else:
                        set_cell_background(cell, "FBFBFB")
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    parts = re.split(r'(\*\*.*?\*\*)', val)
                    for part in parts:
                        if not part:
                            continue
                        if part.startswith('**') and part.endswith('**'):
                            r = p.add_run(clean_xml_string(part[2:-2]))
                            r.font.name = "Times New Roman"
                            r.font.size = Pt(10)
                            r.font.bold = True
                            r.font.color.rgb = RGBColor(0, 32, 96) if c_idx == 0 else RGBColor(0, 0, 0)
                        else:
                            r = p.add_run(clean_xml_string(part))
                            r.font.name = "Times New Roman"
                            r.font.size = Pt(10)

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(4)
        p_after.paragraph_format.first_line_indent = Inches(0)

    for line in lines:
        raw = line.strip()
        if not raw:
            flush_math()
            flush_table()
            continue

        if raw == '---':
            flush_math()
            flush_table()
            continue

        if raw.startswith('|') and raw.endswith('|'):
            flush_math()
            table_buffer.append(raw)
            continue
        else:
            flush_table()

        if in_code_block:
            if raw.startswith('```'):
                in_code_block = False
            else:
                p_code = doc.add_paragraph()
                p_code.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_code.paragraph_format.space_before = Pt(0)
                p_code.paragraph_format.space_after = Pt(0)
                p_code.paragraph_format.first_line_indent = Inches(0.2)
                run_c = p_code.add_run(clean_xml_string(line.rstrip()))
                run_c.font.name = "Consolas"
                run_c.font.size = Pt(8.5)
                run_c.font.color.rgb = RGBColor(60, 60, 60)
            continue

        if raw.startswith('```'):
            flush_math()
            in_code_block = True
            continue

        # Handling math formulas
        if raw == '$$':
            if in_math_block:
                in_math_block = False
                flush_math()
            else:
                flush_math()
                in_math_block = True
            continue

        if in_math_block:
            if raw.endswith('$$'):
                content = raw[:-2].strip()
                if content:
                    math_buffer.append(content)
                in_math_block = False
                flush_math()
            else:
                math_buffer.append(raw)
            continue

        if raw.startswith('$$'):
            if raw.endswith('$$') and len(raw) > 4:
                math_buffer.append(raw[2:-2].strip())
                continue
            else:
                flush_math()
                in_math_block = True
                content = raw[2:].strip()
                if content:
                    math_buffer.append(content)
                continue

        flush_math()

        if raw.startswith('![') and ']' in raw and '(' in raw and raw.endswith(')'):
            m = re.match(r'!\[(.*?)\]\((.*?)\)', raw)
            if m:
                caption = m.group(1).strip()
                img_path = m.group(2).strip()
                if not os.path.isabs(img_path):
                    img_path = os.path.normpath(os.path.join(os.path.dirname(md_file_path), img_path))
                add_image_figure(doc, img_path, caption, width_inch=5.2)
        elif raw.startswith('# '):
            format_heading(doc, raw[2:].strip(), 1)
        elif raw.startswith('## '):
            format_heading(doc, raw[3:].strip(), 2)
        elif raw.startswith('### '):
            format_heading(doc, raw[4:].strip(), 3)
        elif raw.startswith('#### '):
            format_heading(doc, raw[5:].strip(), 4)
        elif raw.startswith('*') and raw.endswith('*') and not raw.startswith('**'):
            p = doc.add_paragraph()
            format_body_paragraph(p, raw[1:-1].strip(), is_intro=True)
        elif raw.startswith('> '):
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Inches(0.2)
            run = p.add_run(clean_xml_string(raw[2:].strip()))
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.italic = True
            run.font.color.rgb = RGBColor(40, 40, 40)
        elif raw.startswith('- ') or raw.startswith('* '):
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.first_line_indent = Inches(-0.15)
            format_body_paragraph(p, "–  " + raw[2:].strip())
        elif re.match(r'^\d+\.\s', raw):
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.first_line_indent = Inches(0.2)
            format_body_paragraph(p, raw)
        else:
            p = doc.add_paragraph()
            format_body_paragraph(p, raw)

    flush_math()
    flush_table()


def safe_save(doc, target_path):
    """Lưu file Word an toàn, nếu file đang mở thì lưu file thay thế"""
    try:
        doc.save(target_path)
        print(f"[OK] Da tao thanh cong file: {target_path}")
    except PermissionError:
        alt_path = target_path.replace(".docx", "_moinhat.docx")
        doc.save(alt_path)
        print(f"[CANH BAO] File {os.path.basename(target_path)} dang duoc mo trong Word.")
        print(f"[OK] Da luu ban moi nhat vao file: {alt_path}")


def build_chapter_1():
    """Tạo file Word độc lập cho Chương 1"""
    doc = docx.Document()
    apply_ptit_page_setup(doc)
    add_cover_box(doc, "CHƯƠNG 1. TỔNG QUAN VỀ BÀI TOÁN")
    add_abbreviations_table(doc)

    md_p = r"c:\KLTNN\bao_cao\CHUONG_1_TONG_QUAN.md"
    parse_and_write_markdown(doc, md_p, chapter_num=1)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_1_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


def build_chapter_2():
    """Tạo file Word độc lập cho Chương 2"""
    doc = docx.Document()
    apply_ptit_page_setup(doc)
    add_cover_box(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG")
    add_abbreviations_table(doc)

    md_p = r"c:\KLTNN\bao_cao\CHUONG_2_CO_SO_LY_THUYET.md"
    parse_and_write_markdown(doc, md_p, chapter_num=2)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_2_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


def build_combined_1_and_2():
    """Tạo file gộp cả Chương 1 và Chương 2"""
    doc = docx.Document()
    apply_ptit_page_setup(doc)
    add_cover_box(doc, "BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP: CHƯƠNG 1 VÀ CHƯƠNG 2")
    add_abbreviations_table(doc)

    parse_and_write_markdown(doc, r"c:\KLTNN\bao_cao\CHUONG_1_TONG_QUAN.md", chapter_num=1)
    doc.add_page_break()
    parse_and_write_markdown(doc, r"c:\KLTNN\bao_cao\CHUONG_2_CO_SO_LY_THUYET.md", chapter_num=2)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_1_va_2_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


if __name__ == "__main__":
    build_chapter_1()
    build_chapter_2()
    build_combined_1_and_2()
