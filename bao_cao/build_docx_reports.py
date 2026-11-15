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
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
            cleaned_math = clean_latex_formula(part[1:-1])
            run = p.add_run(clean_xml_string(cleaned_math))
            run.font.name = "Cambria Math"
            run.font.size = Pt(12)
            run.font.italic = True
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


def clean_latex_formula(s):
    """Chuyển đổi mã nguồn LaTeX sang công thức toán Unicode rõ ràng, đẹp mắt cho Word"""
    s = str(s).strip()
    
    # 0. Pre-clean environments and special operators
    s = s.replace(r'\begin{cases}', '').replace(r'\end{cases}', '')
    s = s.replace(r'\begin{aligned}', '').replace(r'\end{aligned}', '')
    s = s.replace('&', '  :  ')
    s = s.replace(r'\rightarrow', ' → ').replace(r'\leftarrow', ' ← ')
    s = s.replace(r'\mathcal{L}', 'L').replace(r'\mathbb{E}', 'E')

    # 1. Clean \text{...}
    for _ in range(5):
        prev = s
        s = re.sub(r'\\text\s*\{([^{}]+)\}', r'\1', s)
        if s == prev:
            break

    # 2. Convert subscripts/superscripts
    s = re.sub(r'_\{([^{}]+)\}', r'_(\1)', s)
    s = re.sub(r'\^\{([^{}]+)\}', r'^(\1)', s)

    # 3. Clean inner math commands
    for _ in range(5):
        prev = s
        s = re.sub(r'\\sqrt\s*\{([^{}]+)\}', r'√(\1)', s)
        if s == prev:
            break

    s = re.sub(r'\\vec\s*\{([^{}]+)\}', r'\1_thuận', s)
    s = re.sub(r'\\overrightarrow\s*\{([^{}]+)\}', r'\1_thuận', s)
    s = re.sub(r'\\overleftarrow\s*\{([^{}]+)\}', r'\1_nghịch', s)
    s = re.sub(r'\\tilde\s*\{([^{}]+)\}', r'~\1', s)
    s = re.sub(r'\\hat\s*\{([^{}]+)\}', r'\1^', s)
    s = re.sub(r'\\bar\s*\{([^{}]+)\}', r'\1_bar', s)

    # 4. Clean \frac
    for _ in range(4):
        s = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'[\1] / [\2]', s)

    # 5. Remove brackets
    s = s.replace(r'\left(', '(').replace(r'\right)', ')')
    s = s.replace(r'\left[', '[').replace(r'\right]', ']')
    s = s.replace(r'\left|', '|').replace(r'\right|', '|')
    s = s.replace(r'\left.', '').replace(r'\right.', '')
    s = s.replace(r'\left', '').replace(r'\right', '')

    # 6. Greek & Math symbols
    table = [
        (r'\times', ' × '),
        (r'\cdot', ' · '),
        (r'\odot', ' ⊙ '),
        (r'\alpha', 'α'),
        (r'\beta', 'β'),
        (r'\gamma', 'γ'),
        (r'\sigma', 'σ'),
        (r'\Delta', 'Δ'),
        (r'\ge', '≥'),
        (r'\le', '≤'),
        (r'\ne', '≠'),
        (r'\approx', '≈'),
        (r'\in', '∈'),
        (r'\mathbb{R}', 'ℝ'),
        (r'\mathbb R', 'ℝ'),
        (r'\sum', '∑'),
        (r'\max', 'max'),
        (r'\min', 'min'),
        (r'\tanh', 'tanh'),
        (r'\quad', '   '),
        (r'\qquad', '      '),
        (r'\dots', '...'),
        (r'\|', ' ‖ '),
        (r'\%', '%'),
        (r'\pm', '±'),
        (r'\tau', 'τ'),
        (r'\\', '\n'),
    ]
    for p, r in table:
        s = s.replace(p, r)

    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace('{', '').replace('}', '')
    s = re.sub(r'[ \t]+', ' ', s)
    lines = [line.strip() for line in s.split('\n') if line.strip()]
    return clean_xml_string('\n'.join(lines))


def add_math_formula(doc, formula_text):
    """Thêm hộp công thức toán được đóng khung trang trọng, căn giữa trang"""
    cleaned = clean_latex_formula(formula_text)
    if not cleaned:
        return

    lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
    if not lines:
        return

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.rows[0].cells[0]
    cell.width = Inches(5.8)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=80, bottom=80, left=150, right=150)

    for idx, line in enumerate(lines):
        p = cell.paragraphs[0] if idx == 0 else cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)

        run = p.add_run(line)
        run.font.name = "Cambria Math"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 32, 96)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)
    p_after.paragraph_format.first_line_indent = Inches(0)


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

    def flush_math():
        nonlocal math_buffer
        if math_buffer:
            combined = "\n".join(math_buffer)
            add_math_formula(doc, combined)
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

        if raw.startswith('# '):
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

    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\system_architecture_diagram.png", "Hình 1.1: Sơ đồ kiến trúc tổng thể Hệ thống hỗ trợ ra quyết định giao dịch tài chính VQuant", width_inch=5.2)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_1_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


def build_chapter_2():
    """Tạo file Word độc lập cho Chương 2"""
    doc = docx.Document()
    apply_ptit_page_setup(doc)
    add_cover_box(doc, "CHƯƠNG 2. CƠ SỞ KIẾN THỨC VÀ CÔNG NGHỆ ÁP DỤNG")
    add_abbreviations_table(doc)

    md_p = r"c:\KLTNN\bao_cao\CHUONG_2_CO_SO_LY_THUYET.md"
    parse_and_write_markdown(doc, md_p, chapter_num=2)

    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\feature_importance_analysis.png", "Hình 2.1: Phân tích độ quan trọng của 24 đặc trưng kỹ thuật tài chính", width_inch=5.5)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\ai_training_pipeline.png", "Hình 2.2: Luồng tiền xử lý và huấn luyện mô hình CNN-BiGRU-Attention", width_inch=5.5)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\dca_grid_mechanism.png", "Hình 2.3: Nguyên lý thuật toán quản lý vốn lưới ma trận co giãn theo biến động ATR", width_inch=5.0)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_2_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


def build_combined_1_and_2():
    """Tạo file gộp cả Chương 1 và Chương 2"""
    doc = docx.Document()
    apply_ptit_page_setup(doc)
    add_cover_box(doc, "BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP: CHƯƠNG 1 VÀ CHƯƠNG 2")
    add_abbreviations_table(doc)

    parse_and_write_markdown(doc, r"c:\KLTNN\bao_cao\CHUONG_1_TONG_QUAN.md", chapter_num=1)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\system_architecture_diagram.png", "Hình 1.1: Sơ đồ kiến trúc tổng thể Hệ sinh thái Giao dịch tự động VQuant", width_inch=5.2)

    doc.add_page_break()

    parse_and_write_markdown(doc, r"c:\KLTNN\bao_cao\CHUONG_2_CO_SO_LY_THUYET.md", chapter_num=2)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\feature_importance_analysis.png", "Hình 2.1: Phân tích độ quan trọng của 24 đặc trưng kỹ thuật tài chính", width_inch=5.5)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\ai_training_pipeline.png", "Hình 2.2: Luồng tiền xử lý và huấn luyện mô hình CNN-BiGRU-Attention", width_inch=5.5)
    add_image_figure(doc, r"c:\KLTNN\bao_cao\hinh_anh\dca_grid_mechanism.png", "Hình 2.3: Nguyên lý thuật toán quản lý vốn lưới ma trận co giãn theo biến động ATR", width_inch=5.0)

    out_p = r"c:\KLTNN\bao_cao\BaoCao_Chuong_1_va_2_NguyenManhCuong_B22DCCN099.docx"
    safe_save(doc, out_p)


if __name__ == "__main__":
    build_chapter_1()
    build_chapter_2()
    build_combined_1_and_2()
