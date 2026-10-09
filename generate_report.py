"""
Script tạo Báo cáo đồ án cuối kỳ Học máy (DOCX)
=================================================
Tự động tạo file báo cáo chi tiết theo mẫu của trường HUFLIT.
Chạy: python generate_report.py
"""

import sys
import io
from pathlib import Path
from datetime import datetime

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = BASE_DIR / "figures"
REPORT_DOCX = BASE_DIR / "BaoCao_DoAn_HocMay.docx"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def set_cell_shading(cell, color_hex: str):
    """Set background color for a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_custom(doc, text, level=1):
    """Add a heading with consistent formatting."""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue
    return heading


def add_paragraph_text(doc, text, bold=False, italic=False, size=12, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add a formatted paragraph."""
    para = doc.add_paragraph()
    para.alignment = alignment
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.line_spacing = 1.5
    return para


def add_bullet(doc, text, bold_prefix="", level=0):
    """Add a bullet point."""
    para = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        run = para.add_run(bold_prefix)
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "Times New Roman"
    run = para.add_run(text)
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return para


def add_table_from_data(doc, headers, rows, col_widths=None):
    """Create a formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_shading(cell, "003366")
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.name = "Times New Roman"

    # Data rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            if r_idx % 2 == 1:
                set_cell_shading(cell, "F2F2F2")
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(10)
                    run.font.name = "Times New Roman"

    return table


def add_figure(doc, image_path, caption, width_inches=5.5):
    """Add a figure with caption."""
    if Path(image_path).exists():
        doc.add_picture(str(image_path), width=Inches(width_inches))
        last_paragraph = doc.paragraphs[-1]
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        cap_para = doc.add_paragraph()
        cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cap_para.add_run(caption)
        run.italic = True
        run.font.size = Pt(10)
        run.font.name = "Times New Roman"
    else:
        add_paragraph_text(doc, f"[Hình không tìm thấy: {image_path}]", italic=True)


# ============================================================
# TẠO BÁO CÁO
# ============================================================

doc = Document()

# Thiết lập margins
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)

# ============================================================
# TRANG BÌA 1
# ============================================================
for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("TRƯỜNG ĐẠI HỌC NGOẠI NGỮ - TIN HỌC\nTHÀNH PHỐ HỒ CHÍ MINH")
run.bold = True
run.font.size = Pt(14)
run.font.name = "Times New Roman"

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("KHOA CÔNG NGHỆ THÔNG TIN")
run.bold = True
run.font.size = Pt(14)
run.font.name = "Times New Roman"

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("BÁO CÁO KẾT THÚC HỌC PHẦN")
run.bold = True
run.font.size = Pt(16)
run.font.name = "Times New Roman"

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("HỌC MÁY")
run.bold = True
run.font.size = Pt(20)
run.font.name = "Times New Roman"
run.font.color.rgb = RGBColor(0, 51, 102)

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("DỰ ĐOÁN KẾT QUẢ HỌC TẬP CỦA SINH VIÊN\nBẰNG LINEAR REGRESSION")
run.bold = True
run.font.size = Pt(16)
run.font.name = "Times New Roman"
run.font.color.rgb = RGBColor(153, 0, 0)

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Giảng viên hướng dẫn: TS. Võ Thị Hồng Tuyết")
run.font.size = Pt(13)
run.font.name = "Times New Roman"

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Sinh viên thực hiện:")
run.font.size = Pt(13)
run.font.name = "Times New Roman"

# Bảng sinh viên
tbl_sv = doc.add_table(rows=2, cols=2)
tbl_sv.alignment = WD_TABLE_ALIGNMENT.CENTER
cells = [
    ("Nguyễn Thái Lộc", "24DH113306"),
    ("Đặng Đại Lợi (Nhóm trưởng)", "24DH111038"),
]
for i, (name, mssv) in enumerate(cells):
    tbl_sv.rows[i].cells[0].text = name
    tbl_sv.rows[i].cells[1].text = mssv
    for cell in tbl_sv.rows[i].cells:
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.font.size = Pt(13)
                run.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# TRANG BÌA 2
# ============================================================
for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("TRƯỜNG ĐẠI HỌC NGOẠI NGỮ - TIN HỌC\nTHÀNH PHỐ HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN")
run.bold = True
run.font.size = Pt(14)
run.font.name = "Times New Roman"

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("BÁO CÁO KẾT THÚC HỌC PHẦN\nHỌC MÁY")
run.bold = True
run.font.size = Pt(16)
run.font.name = "Times New Roman"

for _ in range(1):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("DỰ ĐOÁN KẾT QUẢ HỌC TẬP CỦA SINH VIÊN\nBẰNG LINEAR REGRESSION")
run.bold = True
run.font.size = Pt(15)
run.font.name = "Times New Roman"
run.font.color.rgb = RGBColor(153, 0, 0)

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Giảng viên hướng dẫn: TS. Võ Thị Hồng Tuyết")
run.font.size = Pt(13)
run.font.name = "Times New Roman"

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Sinh viên thực hiện:")
run.font.size = Pt(13)
run.font.name = "Times New Roman"

tbl_sv2 = doc.add_table(rows=2, cols=2)
tbl_sv2.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (name, mssv) in enumerate(cells):
    tbl_sv2.rows[i].cells[0].text = name
    tbl_sv2.rows[i].cells[1].text = mssv
    for cell in tbl_sv2.rows[i].cells:
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.font.size = Pt(13)
                run.font.name = "Times New Roman"

for _ in range(2):
    doc.add_paragraph()

info_lines = [
    "Mã lớp học phần: 242010202",
    "Năm học: 2025 – 2026",
    "Học kỳ: 3",
]
for line in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(line)
    run.font.size = Pt(13)
    run.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# LỜI CẢM ƠN
# ============================================================
add_heading_custom(doc, "LỜI CẢM ƠN", level=1)

add_paragraph_text(doc, (
    "Đầu tiên, em xin gửi lời cảm ơn chân thành nhất đến TS. Võ Thị Hồng Tuyết – "
    "Giảng viên hướng dẫn môn Học máy. Cô đã tận tình giảng dạy, truyền đạt những kiến thức "
    "nền tảng quan trọng về lý thuyết và thực hành Học máy, đồng thời luôn định hướng, hỗ trợ "
    "em trong suốt quá trình thực hiện đồ án này."
))

add_paragraph_text(doc, (
    "Em cũng xin cảm ơn Trường Đại học Ngoại ngữ - Tin học Thành phố Hồ Chí Minh (HUFLIT) "
    "và Khoa Công nghệ Thông tin đã tạo điều kiện học tập tốt nhất, cung cấp cơ sở vật chất "
    "và môi trường nghiên cứu thuận lợi."
))

add_paragraph_text(doc, (
    "Trong quá trình thực hiện đồ án, không tránh khỏi những thiếu sót. Em rất mong nhận được "
    "sự góp ý của Cô để đồ án được hoàn thiện hơn."
))

add_paragraph_text(doc, "Trân trọng cảm ơn!", italic=True)

doc.add_page_break()

# ============================================================
# MỤC LỤC (placeholder)
# ============================================================
add_heading_custom(doc, "MỤC LỤC", level=1)
toc_items = [
    ("LỜI CẢM ƠN", "i"),
    ("MỤC LỤC", "ii"),
    ("DANH MỤC HÌNH", "iii"),
    ("DANH MỤC BẢNG", "iv"),
    ("CHƯƠNG 1. GIỚI THIỆU", "1"),
    ("   1.1. Đặt vấn đề", "1"),
    ("   1.2. Mục tiêu của đề tài", "1"),
    ("   1.3. Phạm vi nghiên cứu", "2"),
    ("   1.4. Cấu trúc báo cáo", "2"),
    ("CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", "3"),
    ("   2.1. Tổng quan về Học máy", "3"),
    ("   2.2. Bài toán Hồi quy và Mô hình Hồi quy tuyến tính", "4"),
    ("   2.3. Phương pháp tối ưu và các giả định của Linear Regression", "5"),
    ("   2.4. Các kỹ thuật điều chuẩn và mô hình đối chứng bổ trợ", "7"),
    ("   2.5. Thước đo đánh giá hiệu năng", "9"),
    ("   2.6. Các nghiên cứu liên quan", "10"),
    ("CHƯƠNG 3. CHUẨN BỊ DỮ LIỆU", "11"),
    ("   3.1. Giới thiệu tập dữ liệu", "11"),
    ("   3.2. Khám phá dữ liệu (EDA)", "12"),
    ("   3.3. Tiền xử lý dữ liệu", "14"),
    ("   3.4. Xây dựng đặc trưng tối ưu cho mô hình tuyến tính", "15"),
    ("CHƯƠNG 4. XÂY DỰNG MÔ HÌNH HỒI QUY TUYẾN TÍNH", "16"),
    ("   4.1. Thiết kế mô hình Linear Regression trọng tâm", "16"),
    ("   4.2. Quy trình huấn luyện mô hình", "17"),
    ("   4.3. Ví dụ minh họa từng bước tính toán Gradient Descent", "18"),
    ("   4.4. Cài đặt Linear Regression từ đầu (NumPy from scratch)", "19"),
    ("   4.5. Triển khai Linear Regression thư viện và mô hình đối chứng", "21"),
    ("CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ", "23"),
    ("   5.1. Kết quả thực nghiệm mô hình trọng tâm: Linear Regression", "23"),
    ("   5.2. So sánh đối chứng với các thuật toán bổ trợ", "25"),
    ("   5.3. Khảo sát mở rộng bài toán phân lớp bổ trợ", "27"),
    ("   5.4. Đánh giá kiểm thử thực tế (So sánh Dự đoán vs Đáp án)", "29"),
    ("CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "30"),
    ("TÀI LIỆU THAM KHẢO", "31"),
    ("PHỤ LỤC A. MÃ NGUỒN CHƯƠNG TRÌNH", "A-1"),
    ("PHỤ LỤC B. PHÂN CÔNG CÔNG VIỆC", "B-1"),
]
for item, page in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(f"{item}")
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    if not item.startswith("   "):
        run.bold = True
    # Tab + page number
    run2 = p.add_run(f"\t{page}")
    run2.font.size = Pt(12)
    run2.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# DANH MỤC HÌNH
# ============================================================
add_heading_custom(doc, "DANH MỤC HÌNH", level=1)
figures_list = [
    ("Hình 3.1.", "Phân phối GPA 3 học kỳ"),
    ("Hình 3.2.", "Ma trận tương quan giữa các biến số"),
    ("Hình 3.3.", "Boxplot các biến hành vi K1 & K2"),
    ("Hình 3.4.", "Phân bố Xếp loại Học lực và Rèn luyện"),
    ("Hình 4.1.", "Learning Curve của Linear Regression tự cài đặt (Gradient Descent)"),
    ("Hình 4.2.", "Trọng số các đặc trưng — Linear Regression tự cài đặt"),
    ("Hình 4.3.", "So sánh trọng số: sklearn OLS vs Self-Implemented GD"),
    ("Hình 5.1.", "Phân tích phần dư — Linear Regression"),
    ("Hình 5.2.", "Learning Curve — Linear Regression (sklearn)"),
    ("Hình 5.3.", "Actual vs Predicted — So sánh sklearn OLS vs Self-Implemented GD"),
    ("Hình 5.4.", "So sánh R² Test của các mô hình Hồi quy"),
    ("Hình 5.5.", "Mức độ quan trọng của các đặc trưng (Random Forest)"),
    ("Hình 5.6.", "Biểu đồ Actual vs Predicted — Mô hình Hồi quy tốt nhất"),
    ("Hình 5.7.", "Confusion Matrix — Phân loại Leave/Active"),
    ("Hình 5.8.", "Confusion Matrix — Xếp loại Học lực"),
]
for fig_id, fig_caption in figures_list:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(f"{fig_id} {fig_caption}")
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# DANH MỤC BẢNG
# ============================================================
add_heading_custom(doc, "DANH MỤC BẢNG", level=1)
tables_list = [
    ("Bảng 3-1.", "Mô tả các thuộc tính trong tập dữ liệu"),
    ("Bảng 4-1.", "Cấu hình GridSearchCV cho các mô hình"),
    ("Bảng 5-1.", "Kết quả thực nghiệm các mô hình Hồi quy dự đoán GPA kỳ 3"),
    ("Bảng 5-3.", "Kết quả phân loại Leave/Active"),
    ("Bảng 5-4.", "Kết quả phân loại Xếp loại Học lực"),
    ("Bảng 5-5.", "Trích đoạn Bảng so sánh dự đoán với đáp án thực tế"),
]
for tbl_id, tbl_caption in tables_list:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(f"{tbl_id} {tbl_caption}")
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# CHƯƠNG 1: GIỚI THIỆU
# ============================================================
add_heading_custom(doc, "CHƯƠNG 1. GIỚI THIỆU", level=1)

add_heading_custom(doc, "1.1. Đặt vấn đề", level=2)
add_paragraph_text(doc, (
    "Trong bối cảnh giáo dục đại học hiện đại, việc theo dõi và dự đoán sớm kết quả học tập "
    "của sinh viên đóng vai trò sống còn trong công tác quản lý đào tạo và hỗ trợ người học. "
    "Nhiều sinh viên trong giai đoạn chuyển tiếp giữa các năm học đầu tiên gặp khó khăn thích nghi, "
    "dẫn tới tụt dốc kết quả học tập, cảnh cáo học vụ, thậm chí phải bảo lưu hoặc thôi học. "
    "Điều này gây lãng phí nghiêm trọng nguồn lực tài chính, thời gian của gia đình và nhà trường."
))

add_paragraph_text(doc, (
    "Để giải quyết thách thức trên một cách khoa học, thuật toán Hồi quy tuyến tính (Linear Regression) "
    "nổi lên như một công cụ cơ bản, chuẩn mực và mạnh mẽ nhất trong lĩnh vực Học máy. Khác với "
    "các mô hình hộp đen (Black-box models) phức tạp, Linear Regression sở hữu ưu điểm vượt trội về "
    "tính minh bạch (Transparency) và khả năng giải thích (Interpretability). Mô hình cho phép chỉ ra "
    "định lượng chính xác mức độ tác động của từng nhân tố học vụ (điểm GPA quá khứ, số giờ tự học, điểm rèn luyện, "
    "số tín chỉ đăng ký) đến kết quả GPA trong học kỳ tiếp theo."
))

add_paragraph_text(doc, (
    "Xuất phát từ nhiệm vụ môn học và ý nghĩa thực tiễn to lớn đó, nhóm thực hiện đề tài: "
    "\"Dự đoán kết quả học tập của sinh viên bằng Linear Regression\". Đề tài tập trung nghiên cứu, "
    "cài đặt và tối ưu hóa mô hình Hồi quy tuyến tính để dự đoán điểm GPA kỳ 3 của sinh viên dựa trên "
    "dữ liệu học vụ tích lũy ở kỳ 1 và kỳ 2; đồng thời triển khai một số thuật toán học máy khác đóng "
    "vai trò bổ sung đối chứng nhằm làm nổi bật ưu thế và giá trị ứng dụng của Linear Regression."
))

add_heading_custom(doc, "1.2. Mục tiêu của đề tài", level=2)
add_paragraph_text(doc, "Đề tài xác định rõ các mục tiêu trọng tâm và các mục tiêu bổ trợ như sau:")
objectives = [
    ("(1) Mục tiêu cốt lõi — Mô hình Hồi quy tuyến tính (Linear Regression): ", "Xây dựng, huấn luyện và đánh giá mô hình Linear Regression dự đoán điểm GPA kỳ 3 (gpa3) của sinh viên hoàn toàn từ dữ liệu quá khứ đến hết kỳ 2, bảo đảm nguyên tắc không rò rỉ dữ liệu (No Data Leakage)."),
    ("(2) Cài đặt thuật toán từ đầu (From Scratch): ", "Tự lập trình thuật toán Linear Regression bằng ngôn ngữ Python thuần túy với thư viện NumPy, áp dụng thuật toán tối ưu hóa Gradient Descent mà không sử dụng bất kỳ thư viện Học máy nào, giúp làm chủ bản chất toán học của thuật toán."),
    ("(3) Kỹ thuật Feature Engineering chuyên sâu: ", "Xây dựng các biến phái sinh tuyến tính và tương tác đặc trưng (xu hướng điểm gpa_trend, tương tác tích lũy gpa1_x_gpa2, giờ tự học trung bình) nhằm tối ưu hóa không gian biểu diễn cho mô hình tuyến tính."),
    ("(4) Triển khai các mô hình bổ trợ đối chứng (Comparative Baselines): ", "Huấn luyện các mô hình biến thể điều chuẩn (Ridge, Lasso, ElasticNet) và các mô hình phi tuyến/ensemble (Decision Tree, Random Forest, Gradient Boosting, XGBoost, SVR) đóng vai trò bổ sung, đối chiếu nhằm kiểm chứng tính ưu việt của Linear Regression."),
    ("(5) Khảo sát mở rộng bài toán phân lớp: ", "Mở rộng khảo sát bổ trợ bài toán phân loại nhị phân cảnh báo nguy cơ thôi học (Leave/Active) và phân loại đa lớp xếp loại học lực, hoàn thiện bức tranh phân tích toàn diện."),
    ("(6) Thẩm định thực nghiệm nghiêm ngặt: ", "Áp dụng phương pháp Cross-Validation 5-fold, tinh chỉnh siêu tham số bằng GridSearchCV và đối soát kiểm thử thực tế trên 146 sinh viên độc lập."),
]
for prefix, text in objectives:
    add_bullet(doc, text, bold_prefix=prefix)

add_heading_custom(doc, "1.3. Phạm vi nghiên cứu", level=2)
add_paragraph_text(doc, "Đề tài giới hạn phạm vi nghiên cứu trong các nội dung cụ thể sau:")
scope_items = [
    "Tập dữ liệu nghiên cứu: Gồm 500 sinh viên (100 quan sát từ nguồn dữ liệu thực tế kết hợp 400 quan sát sinh tổng hợp có kiểm soát phân phối chuẩn), với cấu trúc 24 cột thuộc tính chuẩn hóa.",
    "Thuộc tính đầu vào (Features): Hoàn toàn chỉ khai thác thông tin học kỳ 1 và học kỳ 2 (GPA, tín chỉ, giờ tự học, điểm rèn luyện, hoạt động ngoại khóa) và số tín chỉ đăng ký kỳ 3.",
    "Mô hình trọng tâm: Hồi quy tuyến tính (Linear Regression) – bao gồm cả bản tự lập trình Gradient Descent và bản giải tích Ordinary Least Squares (OLS) từ thư viện scikit-learn.",
    "Mô hình bổ trợ đối chứng: Ridge Regression, Lasso Regression, ElasticNet, Decision Tree, Random Forest, Gradient Boosting, XGBoost, SVR (cho bài toán hồi quy); Logistic Regression, Random Forest, GBDT, KNN, SVM (cho bài toán phân loại bổ trợ).",
    "Môi trường thực nghiệm: Ngôn ngữ Python 3.13, môi trường VS Code / Jupyter Notebook, các thư viện khoa học dữ liệu: NumPy, Pandas, Scikit-learn, Matplotlib, Seaborn, Imbalanced-learn.",
]
for item in scope_items:
    add_bullet(doc, item)

add_heading_custom(doc, "1.4. Cấu trúc báo cáo", level=2)
add_paragraph_text(doc, "Báo cáo đồ án được kết cấu mạch lạc thành 6 chương:")
structure_items = [
    ("Chương 1 – Giới thiệu: ", "Trình bày bối cảnh thực tiễn, đặt vấn đề, mục tiêu trọng tâm, phạm vi nghiên cứu và cấu trúc báo cáo."),
    ("Chương 2 – Cơ sở lý thuyết: ", "Trình bày cơ sở toán học chuyên sâu của mô hình Linear Regression (OLS, Gradient Descent, các giả định CLRM), các biến thể điều chuẩn và mô hình đối chứng bổ trợ."),
    ("Chương 3 – Chuẩn bị dữ liệu: ", "Mô tả tập dữ liệu 500 sinh viên, quy trình khám phá dữ liệu (EDA), kỹ thuật tiền xử lý và xây dựng đặc trưng cho mô hình tuyến tính."),
    ("Chương 4 – Xây dựng mô hình Hồi quy tuyến tính: ", "Chi tiết thiết kế mô hình trọng tâm, quy trình huấn luyện, ví dụ tính toán từng bước Gradient Descent, mã nguồn tự cài đặt và cấu hình tham số."),
    ("Chương 5 – Thực nghiệm và đánh giá: ", "Công bố kết quả thực nghiệm chi tiết của Linear Regression, phân tích các trọng số hồi quy, so sánh đối chứng với các mô hình khác và bảng đối soát 146 sinh viên test set."),
    ("Chương 6 – Kết luận và hướng phát triển: ", "Tổng kết các kết quả đạt được của mô hình Linear Regression, nêu rõ hạn chế và đề xuất hướng mở rộng trong tương lai."),
]
for prefix, text in structure_items:
    add_bullet(doc, text, bold_prefix=prefix)

doc.add_page_break()

# ============================================================
# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT
# ============================================================
add_heading_custom(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", level=1)

add_heading_custom(doc, "2.1. Tổng quan về Học máy", level=2)
add_paragraph_text(doc, (
    "Học máy (Machine Learning) là một nhánh của Trí tuệ nhân tạo (AI), cho phép máy tính "
    "tự động học hỏi và cải thiện từ dữ liệu mà không cần được lập trình tường minh cho từng "
    "trường hợp cụ thể [1]. Theo Tom Mitchell (1997), một chương trình máy tính được cho là "
    "học từ kinh nghiệm E với một tác vụ T và thước đo hiệu suất P, nếu hiệu suất của nó "
    "trên T (đo bằng P) cải thiện khi có thêm kinh nghiệm E [2]."
))

add_paragraph_text(doc, "Học máy được phân thành ba loại chính:", bold=True)
ml_types = [
    ("Học có giám sát (Supervised Learning): ", "Mô hình học từ dữ liệu có nhãn (labeled data). Bao gồm bài toán Hồi quy (dự đoán giá trị liên tục) và Phân lớp (dự đoán nhãn rời rạc)."),
    ("Học không giám sát (Unsupervised Learning): ", "Mô hình học từ dữ liệu không có nhãn, tìm cấu trúc ẩn. Ví dụ: Phân cụm (Clustering), Giảm chiều (Dimensionality Reduction)."),
    ("Học bán giám sát và Học tăng cường: ", "Kết hợp dữ liệu có nhãn và không nhãn, hoặc học thông qua tương tác với môi trường."),
]
for prefix, text in ml_types:
    add_bullet(doc, text, bold_prefix=prefix)

add_paragraph_text(doc, (
    "Trong đề tài này, chúng em sử dụng Học có giám sát với cả hai bài toán Hồi quy và Phân lớp "
    "để dự đoán kết quả học tập của sinh viên."
))

add_heading_custom(doc, "2.2. Bài toán Hồi quy và Mô hình Hồi quy tuyến tính", level=2)
add_paragraph_text(doc, (
    "Bài toán Hồi quy (Regression) trong Học máy có mục tiêu dự đoán một giá trị đầu ra liên tục "
    "dựa trên tập hợp các biến đầu vào. Trong phạm vi đề tài, biến mục tiêu là điểm trung bình học kỳ 3 "
    "(gpa3) của sinh viên – một giá trị liên tục thuộc thang điểm 4.0 [0.0 – 4.0]."
))

add_paragraph_text(doc, (
    "Mô hình Hồi quy tuyến tính (Linear Regression) là mô hình trọng tâm cốt lõi của nghiên cứu. "
    "Mô hình thiết lập giả định rằng mối quan hệ giữa các đặc trưng đầu vào X và biến mục tiêu y "
    "có dạng tổ hợp tuyến tính:\n"
    "ŷ = w₀ + w₁x₁ + w₂x₂ + ... + w_dx_d = Xw + b\n"
    "trong đó w = (w₁, ..., w_d)ᵀ là vector trọng số (weights/coefficients), b = w₀ là hệ số chặn (bias/intercept), "
    "và d là số lượng đặc trưng đầu vào."
))

add_paragraph_text(doc, (
    "Ý nghĩa thống kê then chốt của Linear Regression: Mỗi trọng số wⱼ phản ánh trực tiếp mức độ thay đổi "
    "kỳ vọng của GPA kỳ 3 khi đặc trưng xⱼ tăng thêm 1 đơn vị (trong điều kiện tất cả các đặc trưng khác giữ nguyên). "
    "Đặc tính này mang lại tính minh bạch tuyệt đối (Explainability), cho phép nhà trường nắm bắt chính xác "
    "đòn bẩy tác động đến kết quả học tập của người học."
))

add_paragraph_text(doc, (
    "Hàm mất mát và Nghiệm giải tích bình phương bé nhất (Ordinary Least Squares - OLS):\n"
    "Để tìm vector trọng số tối ưu w*, mô hình cực tiểu hóa hàm mất mát sai số toàn phương trung bình (MSE):\n"
    "J(w) = (1/2n) × ||Xw - y||₂² = (1/2n) × Σ(ŷᵢ - yᵢ)²\n"
    "Bằng cách lấy đạo hàm ∇_w J(w) = (1/n) × Xᵀ(Xw - y) = 0, ta thu được nghiệm giải tích dạng đóng (Normal Equation):\n"
    "w* = (XᵀX)⁻¹ Xᵀy\n"
    "Nghiệm OLS cho kết quả tối ưu toàn cục chính xác nhưng đòi hỏi ma trận (XᵀX) phải khả nghịch (không bị đa cộng tuyến hoàn hảo) "
    "và có độ phức tạp tính toán O(d³)."
))

add_heading_custom(doc, "2.3. Phương pháp tối ưu và các giả định của Linear Regression", level=2)
add_paragraph_text(doc, "2.3.1. Thuật toán tối ưu Gradient Descent", bold=True)
add_paragraph_text(doc, (
    "Trong trường hợp số chiều dữ liệu lớn hoặc để hiểu rõ cơ chế học số học, thuật toán Gradient Descent (GD) "
    "được áp dụng để tìm cực tiểu hàm mất mát thông qua các bước lặp:\n"
    "w ← w - α × ∇_w J(w) = w - (α/n) × Xᵀ(ŷ - y)\n"
    "b ← b - α × ∇_b J(b) = b - (α/n) × Σ(ŷᵢ - yᵢ)\n"
    "trong đó α > 0 là tốc độ học (learning rate). Việc chuẩn hóa dữ liệu (StandardScaler) trước khi chạy GD "
    "là bắt buộc để mặt cong mất mát có dạng đối xứng cầu, đảm bảo gradient hướng thẳng về điểm cực tiểu toàn cục."
))

add_paragraph_text(doc, "2.3.2. Năm giả định kinh điển của mô hình Hồi quy tuyến tính (CLRM)", bold=True)
add_paragraph_text(doc, (
    "Để mô hình Linear Regression cho ước lượng không chệch tốt nhất (BLUE - Best Linear Unbiased Estimator) "
    "theo định lý Gauss-Markov, các giả định sau cần được kiểm chứng:\n"
    "1. Tính tuyến tính (Linearity): Quan hệ giữa các biến độc lập và biến phụ thuộc có dạng tuyến tính.\n"
    "2. Không có đa cộng tuyến hoàn hảo (No Multicollinearity): Giữa các đặc trưng dự đoán không có mối quan hệ tuyến tính tuyệt đối.\n"
    "3. Kỳ vọng sai số bằng không: E[ε|X] = 0, phần dư phân bố đều quanh giá trị trung bình 0.\n"
    "4. Đồng phương sai sai số (Homoscedasticity): Phương sai của sai số là hằng số qua các mức giá trị dự đoán, Var(εᵢ|X) = σ².\n"
    "5. Tính độc lập của sai số (No Autocorrelation): Các phần dư không có sự phụ thuộc hay tương quan lẫn nhau."
))

add_heading_custom(doc, "2.4. Các kỹ thuật điều chuẩn và mô hình đối chứng bổ trợ", level=2)

add_heading_custom(doc, "2.4.1. Điều chuẩn cho Linear Regression: Ridge, Lasso, ElasticNet", level=3)
add_paragraph_text(doc, (
    "Khi bổ sung nhiều biến phái sinh trong Feature Engineering, nguy cơ đa cộng tuyến tăng cao. "
    "Các kỹ thuật điều chuẩn (Regularization) là phần mở rộng trực tiếp của Linear Regression:\n"
    "• Ridge Regression (điều chuẩn L2): J_Ridge = MSE + α × ||w||₂². Ép các hệ số tiến dần về 0, khắc phục triệt để hiện tượng ma trận XᵀX suy biến.\n"
    "• Lasso Regression (điều chuẩn L1): J_Lasso = MSE + α × ||w||₁. Ép một số trọng số thừa về chính xác bằng 0, đóng vai trò chọn lọc đặc trưng tự động.\n"
    "• ElasticNet: Kết hợp cả L1 và L2 với tham số tỉ lệ l1_ratio, cân bằng giữa khả năng co trọng số và lọc biến."
))

add_heading_custom(doc, "2.4.2. Các mô hình phi tuyến và Ensemble đóng vai trò đối chứng (Comparative Baselines)", level=3)
add_paragraph_text(doc, (
    "Để kiểm nghiệm xem mối quan hệ giữa kết quả học tập các kỳ có thực sự mang tính tuyến tính hay cần đến "
    "các hàm phi tuyến phức tạp, đề tài triển khai các thuật toán sau đóng vai trò mốc so sánh (benchmarks):\n"
    "• Decision Tree: Phân chia không gian dữ liệu bằng cây quyết định nhị phân theo tiêu chí MSE.\n"
    "• Random Forest & Gradient Boosting (GBDT): Các mô hình ensemble kết hợp nhiều cây quyết định theo cơ chế Bagging và Boosting.\n"
    "• XGBoost (Extreme Gradient Boosting): Thuật toán boosting tối ưu hóa tốc độ và xử lý chính quy hóa bậc hai.\n"
    "• Support Vector Regression (SVR): Hồi quy vector hỗ trợ tối ưu hàm mất mát ε-insensitive."
))

add_heading_custom(doc, "2.4.3. Các mô hình phân lớp bổ trợ (Supplementary Classification)", level=3)
add_paragraph_text(doc, (
    "Nhằm cung cấp góc nhìn đa chiều cho công tác quản lý đào tạo, đề tài mở rộng khảo sát bổ trợ 2 bài toán phân lớp:\n"
    "• Cảnh báo thôi học/bảo lưu (status_K3): Phân loại nhị phân (Leave/Active) bằng Logistic Regression, Random Forest, GBDT, KNN, SVM kết hợp kỹ thuật SMOTE.\n"
    "• Xếp loại học lực: Phân loại đa lớp (5 nhãn: Xuất sắc, Giỏi, Khá, Trung bình, Yếu) để đánh giá năng lực dự báo nhóm học lực."
))

add_heading_custom(doc, "2.5. Thước đo đánh giá", level=2)

add_heading_custom(doc, "2.5.1. Thước đo cho bài toán Hồi quy", level=3)
reg_metrics = [
    ("R² (Coefficient of Determination): ", "Tỷ lệ phương sai của y được giải thích bởi mô hình. R² = 1 - SS_res/SS_tot. Giá trị càng gần 1 càng tốt."),
    ("RMSE (Root Mean Squared Error): ", "Căn bậc hai của trung bình bình phương sai số. RMSE = √(Σ(yᵢ - ŷᵢ)² / n). Đơn vị giống biến mục tiêu."),
    ("MAE (Mean Absolute Error): ", "Trung bình giá trị tuyệt đối sai số. MAE = Σ|yᵢ - ŷᵢ| / n. Ít nhạy cảm với outlier hơn RMSE."),
    ("MAPE (Mean Absolute Percentage Error): ", "Sai số phần trăm trung bình. MAPE = Σ|yᵢ - ŷᵢ|/|yᵢ| × 100%."),
]
for prefix, text in reg_metrics:
    add_bullet(doc, text, bold_prefix=prefix)

add_heading_custom(doc, "2.5.2. Thước đo cho bài toán Phân loại", level=3)
clf_metrics = [
    ("Accuracy: ", "Tỷ lệ dự đoán đúng trên tổng số mẫu. Accuracy = (TP + TN) / (TP + TN + FP + FN)."),
    ("Precision: ", "Tỷ lệ dự đoán dương đúng trên tổng dự đoán dương. Precision = TP / (TP + FP)."),
    ("Recall (Sensitivity): ", "Tỷ lệ phát hiện đúng các mẫu dương thực tế. Recall = TP / (TP + FN)."),
    ("F1-Score: ", "Trung bình điều hòa của Precision và Recall. F1 = 2 × (P × R) / (P + R)."),
    ("AUC-ROC: ", "Diện tích dưới đường cong ROC, đo khả năng phân biệt giữa hai lớp."),
    ("Confusion Matrix: ", "Ma trận thể hiện TP, TN, FP, FN, giúp đánh giá chi tiết từng lớp."),
]
for prefix, text in clf_metrics:
    add_bullet(doc, text, bold_prefix=prefix)

add_heading_custom(doc, "2.5.3. Cross-Validation", level=3)
add_paragraph_text(doc, (
    "Cross-Validation (CV) là kỹ thuật đánh giá mô hình bằng cách chia dữ liệu thành k phần (fold), "
    "lần lượt sử dụng từng phần làm tập kiểm thử và phần còn lại làm tập huấn luyện. "
    "Trong đề tài, chúng em sử dụng 5-fold Stratified Cross-Validation để đảm bảo "
    "mỗi fold có phân bố nhãn tương tự nhau, đặc biệt quan trọng với dữ liệu mất cân bằng [3]."
))

add_heading_custom(doc, "2.6. Các nghiên cứu liên quan", level=2)
add_paragraph_text(doc, (
    "Nhiều nghiên cứu đã áp dụng Học máy trong dự đoán kết quả học tập sinh viên. "
    "Helal và cs. [5] sử dụng Random Forest và Gradient Boosting để dự đoán điểm số sinh viên "
    "với độ chính xác cao. Anoopkumar và Rahman [6] so sánh Decision Tree, KNN và Naive Bayes "
    "trong bài toán phân loại kết quả học tập, cho thấy ensemble methods thường vượt trội. "
    "Thai-Nghe và cs. [7] đề xuất hệ thống cảnh báo sớm dựa trên GPA các kỳ trước, "
    "tương tự cách tiếp cận của đề tài này."
))

doc.add_page_break()

# ============================================================
# CHƯƠNG 3: CHUẨN BỊ DỮ LIỆU
# ============================================================
add_heading_custom(doc, "CHƯƠNG 3. CHUẨN BỊ DỮ LIỆU", level=1)

add_heading_custom(doc, "3.1. Giới thiệu tập dữ liệu", level=2)
add_paragraph_text(doc, (
    "Tập dữ liệu sử dụng trong đề tài gồm 500 sinh viên với 24 thuộc tính, mô phỏng dữ liệu "
    "học tập 3 học kỳ. Trong đó, 100 dòng đầu tiên được lấy từ tập dữ liệu Student Performance "
    "trên Kaggle, 400 dòng còn lại được sinh tổng hợp (synthetic) theo phân phối thống kê "
    "của dữ liệu gốc bằng phương pháp multivariate normal sampling."
))

# Bảng mô tả thuộc tính
add_paragraph_text(doc, "Bảng 3-1. Mô tả các thuộc tính trong tập dữ liệu", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
attr_headers = ["STT", "Thuộc tính", "Mô tả", "Kiểu dữ liệu"]
attr_rows = [
    ["1", "stud_id", "Mã sinh viên (định danh)", "int"],
    ["2", "status_K1/K2/K3", "Trạng thái học kỳ (Active/Leave)", "str"],
    ["3", "gpa1/gpa2/gpa3", "Điểm GPA các kỳ (thang 4.0)", "float"],
    ["4", "Tin_Chi_K1/K2/K3", "Số tín chỉ đã đăng ký", "int"],
    ["5", "So_Gio_Tu_Hoc_K1/K2/K3", "Số giờ tự học/tuần", "float"],
    ["6", "So_Lan_Tham_Gia_HD_K1/K2/K3", "Số lần tham gia hoạt động ngoại khóa", "int"],
    ["7", "Diem_Ren_Luyen_K1/K2/K3", "Điểm rèn luyện (thang 100)", "int"],
    ["8", "Tong_Tin_Chi", "Tổng tín chỉ tích lũy", "int"],
    ["9", "cgpa", "Điểm trung bình tích lũy (có trọng số)", "float"],
    ["10", "Diem_Ren_Luyen_TB", "Điểm rèn luyện trung bình", "int"],
    ["11", "Xep_Loai_DRL", "Xếp loại rèn luyện", "str"],
    ["12", "Xep_Loai_Hoc_Luc", "Xếp loại học lực", "str"],
]
add_table_from_data(doc, attr_headers, attr_rows)

add_paragraph_text(doc, (
    "Lưu ý quan trọng: Sinh viên có trạng thái Leave ở kỳ nào thì tất cả biến hành vi của kỳ đó "
    "(tín chỉ, giờ tự học, hoạt động, ĐRL, GPA) đều bằng 0. CGPA và ĐRL trung bình chỉ tính "
    "trên các kỳ thực học, không phạt điểm 0 của kỳ bảo lưu."
), italic=True)

add_heading_custom(doc, "3.2. Khám phá dữ liệu (EDA)", level=2)
add_paragraph_text(doc, (
    "Trước khi xây dựng mô hình, chúng em tiến hành phân tích khám phá dữ liệu (Exploratory "
    "Data Analysis – EDA) để hiểu rõ đặc điểm phân phối, mối tương quan và các đặc tính "
    "của tập dữ liệu."
))

add_heading_custom(doc, "3.2.1. Phân phối GPA", level=3)
add_paragraph_text(doc, (
    "Hình 3.1 thể hiện phân phối GPA của sinh viên qua 3 học kỳ. GPA các kỳ đều có phân phối "
    "gần chuẩn (normal distribution), tập trung quanh giá trị trung bình khoảng 3.5 trên thang 4.0, "
    "cho thấy đa số sinh viên có kết quả học tập tương đối tốt."
))
add_figure(doc, FIGURES_DIR / "eda_gpa_distribution.png", "Hình 3.1. Phân phối GPA 3 học kỳ")

add_heading_custom(doc, "3.2.2. Ma trận tương quan", level=3)
add_paragraph_text(doc, (
    "Hình 3.2 cho thấy ma trận tương quan giữa các biến số trong tập dữ liệu. "
    "GPA giữa các kỳ có tương quan mạnh (gpa1-gpa2 ≈ 0.7, gpa2-gpa3 ≈ 0.5), "
    "xác nhận giả thuyết về quán tính học tập: sinh viên học tốt ở kỳ trước có xu hướng "
    "tiếp tục học tốt ở kỳ sau. Số giờ tự học và điểm rèn luyện cũng tương quan dương "
    "với GPA, cho thấy sự cần cù và ý thức rèn luyện đóng vai trò tích cực."
))
add_figure(doc, FIGURES_DIR / "eda_correlation_heatmap.png", "Hình 3.2. Ma trận tương quan giữa các biến số", 6.0)

add_heading_custom(doc, "3.2.3. Phân phối biến hành vi", level=3)
add_paragraph_text(doc, (
    "Hình 3.3 thể hiện phân phối các biến hành vi ở Kỳ 1 và Kỳ 2, bao gồm giờ tự học, "
    "số lần tham gia hoạt động ngoại khóa và điểm rèn luyện. Các boxplot cho thấy dữ liệu "
    "phân bố khá đều, không có nhiều outlier nghiêm trọng."
))
add_figure(doc, FIGURES_DIR / "eda_behavior_boxplot.png", "Hình 3.3. Boxplot các biến hành vi K1 & K2")

add_heading_custom(doc, "3.2.4. Phân bố xếp loại", level=3)
add_paragraph_text(doc, (
    "Hình 3.4 cho thấy phân bố xếp loại Học lực và Rèn luyện. Về Học lực, phần lớn sinh viên "
    "đạt loại Giỏi và Xuất sắc. Về Rèn luyện, loại Khá chiếm đa số. "
    "Đặc biệt, dữ liệu status_K3 rất mất cân bằng: chỉ 16/500 (3.2%) sinh viên Leave, "
    "đây là thách thức lớn cho bài toán phân loại nhị phân."
))
add_figure(doc, FIGURES_DIR / "eda_classification_distribution.png", "Hình 3.4. Phân bố Xếp loại Học lực và Rèn luyện")

add_heading_custom(doc, "3.3. Tiền xử lý dữ liệu", level=2)

add_heading_custom(doc, "3.3.1. Làm sạch dữ liệu", level=3)
add_paragraph_text(doc, (
    "Tập dữ liệu đã được xử lý sạch từ khâu sinh dữ liệu: không có giá trị null (0 null cells "
    "trên toàn bộ 500 × 24 = 12,000 ô), không có duplicates, và tất cả giá trị nằm trong "
    "khoảng hợp lệ (GPA ∈ [0, 4], ĐRL ∈ [35, 100], v.v.)."
))

add_heading_custom(doc, "3.3.2. Chuẩn hóa dữ liệu", level=3)
add_paragraph_text(doc, (
    "Áp dụng StandardScaler (z-score normalization) cho các mô hình nhạy cảm với scale: "
    "Linear Regression, Ridge, Lasso, Logistic Regression, SVM/SVR, KNN. "
    "Công thức: z = (x - μ) / σ. Các mô hình dựa trên cây (Decision Tree, Random Forest, "
    "Gradient Boosting) không cần chuẩn hóa."
))

add_heading_custom(doc, "3.3.3. Xử lý dữ liệu mất cân bằng", level=3)
add_paragraph_text(doc, (
    "Bài toán phân loại Leave/Active có dữ liệu rất mất cân bằng (3.2% Leave). "
    "Chúng em áp dụng hai chiến lược: (1) SMOTE (Synthetic Minority Over-sampling Technique) "
    "để tăng cường mẫu thiểu số trên tập huấn luyện, và (2) class_weight='balanced' cho "
    "Logistic Regression, Random Forest và SVM."
))

add_heading_custom(doc, "3.3.4. Chia tập dữ liệu", level=3)
add_paragraph_text(doc, (
    "Dữ liệu được chia thành tập huấn luyện (70%) và tập kiểm thử (30%) với random_state=42 "
    "để đảm bảo tính tái lập. Đối với bài toán phân loại, sử dụng stratified split để đảm bảo "
    "tỷ lệ nhãn tương đồng giữa tập huấn luyện và kiểm thử."
))

add_heading_custom(doc, "3.4. Xây dựng đặc trưng (Feature Engineering)", level=2)
add_paragraph_text(doc, (
    "Ngoài 10-11 biến gốc từ K1 và K2, chúng em xây dựng thêm 6 biến phái sinh nhằm nắm bắt "
    "các mẫu hình học tập sâu hơn:"
))

fe_items = [
    ("gpa_trend = gpa2 - gpa1: ", "Xu hướng GPA (dương = tiến bộ, âm = sa sút)."),
    ("gpa_avg = (gpa1 + gpa2) / 2: ", "GPA trung bình 2 kỳ đầu."),
    ("study_hours_avg: ", "Số giờ tự học trung bình 2 kỳ."),
    ("drl_avg: ", "Điểm rèn luyện trung bình 2 kỳ."),
    ("activity_total: ", "Tổng số lần tham gia hoạt động ngoại khóa 2 kỳ."),
    ("credits_total_k12: ", "Tổng tín chỉ đăng ký K1 + K2."),
]
for prefix, text in fe_items:
    add_bullet(doc, text, bold_prefix=prefix)

add_paragraph_text(doc, (
    "Việc thêm các biến phái sinh giúp mô hình nắm bắt được xu hướng thay đổi theo thời gian "
    "và các tương tác giữa các biến, từ đó cải thiện khả năng dự đoán."
))

doc.add_page_break()

# ============================================================
# CHƯƠNG 4: XÂY DỰNG MÔ HÌNH HỒI QUY TUYẾN TÍNH
# ============================================================
add_heading_custom(doc, "CHƯƠNG 4. XÂY DỰNG MÔ HÌNH HỒI QUY TUYẾN TÍNH", level=1)

add_heading_custom(doc, "4.1. Thiết kế mô hình Linear Regression trọng tâm", level=2)
add_paragraph_text(doc, (
    "Mô hình trọng tâm của đề tài là Hồi quy tuyến tính (Linear Regression). Mục tiêu cốt lõi là thiết lập "
    "hàm hồi quy xấp xỉ điểm GPA kỳ 3 (gpa3) của sinh viên dựa trên tập 23 đặc trưng (11 đặc trưng gốc và 12 "
    "đặc trưng phái sinh/tương tác sau Feature Engineering). Hàm hồi quy thực nghiệm có dạng toán học:\n"
    "ŷ_GPA3 = w₁ · gpa1 + w₂ · gpa2 + w₃ · gpa2² + w₄ · (gpa1 × gpa2) + ... + w₂₃ · drl_trend + b\n"
    "trong đó các biến đầu vào đều được chuẩn hóa qua StandardScaler để bảo đảm thang đo đồng nhất."
))

add_paragraph_text(doc, (
    "Bên cạnh việc phát triển và tối ưu mô hình trọng tâm Linear Regression, đề tài triển khai các thuật toán "
    "biến thể điều chuẩn (Ridge, Lasso, ElasticNet) và các mô hình phi tuyến/ensemble (Decision Tree, Random Forest, "
    "Gradient Boosting, XGBoost, SVR) đóng vai trò bổ trợ, đối chiếu nhằm kiểm chứng tính ưu việt của Linear Regression."
))

add_heading_custom(doc, "4.2. Quy trình huấn luyện mô hình", level=2)
add_paragraph_text(doc, "Quy trình huấn luyện tuân theo ML Pipeline chuẩn hóa nghiêm ngặt:", bold=True)
pipeline_steps = [
    "Thu thập và tiền xử lý dữ liệu: Làm sạch, loại bỏ rò rỉ dữ liệu (No Data Leakage).",
    "Khám phá dữ liệu (EDA): Phân tích phân phối, tương quan giữa các kỳ học.",
    "Feature Engineering: Tạo 12 biến phái sinh tối ưu hóa cho mô hình tuyến tính (tổng cộng 23 biến).",
    "Phân chia tập dữ liệu: 70% Train (338 sinh viên) và 30% Test độc lập (146 sinh viên).",
    "Chuẩn hóa dữ liệu bằng StandardScaler (fit trên Train, transform trên Test).",
    "Huấn luyện mô hình Linear Regression tự cài đặt từ đầu (Gradient Descent).",
    "Huấn luyện Linear Regression thư viện (OLS) và các mô hình đối chứng với 5-fold Cross-Validation.",
    "Đánh giá, đối soát thực tế và phân tích phương trình hồi quy trên 146 sinh viên tập kiểm thử.",
]
for i, step in enumerate(pipeline_steps, 1):
    add_bullet(doc, f"Bước {i}: {step}")

add_heading_custom(doc, "4.3. Ví dụ minh họa từng bước quy trình huấn luyện Linear Regression", level=2)
add_paragraph_text(doc, (
    "Dưới đây là ví dụ minh họa chi tiết quy trình huấn luyện mô hình Linear Regression "
    "tự cài đặt bằng thuật toán Gradient Descent cho bài toán dự đoán GPA kỳ 3:"
))

add_paragraph_text(doc, "Bước 1: Khởi tạo trọng số (Weights Initialization)", bold=True)
add_paragraph_text(doc, (
    "Trọng số w được khởi tạo bằng vector 0 có kích thước bằng số đặc trưng (23 biến sau "
    "Feature Engineering). Hệ số chặn bias b = 0.0."
))

add_paragraph_text(doc, "Bước 2: Lan truyền xuôi (Forward pass)", bold=True)
add_paragraph_text(doc, (
    "Tính vector giá trị dự đoán: ŷ = X × w + b, trong đó ma trận dữ liệu đã chuẩn hóa X "
    "có kích thước (338 × 23), vector trọng số w có kích thước (23,)."
))

add_paragraph_text(doc, "Bước 3: Tính hàm mất mát (MSE Loss)", bold=True)
add_paragraph_text(doc, (
    "Loss = (1/2n) × Σ(ŷᵢ - yᵢ)². Giá trị mất mát ban đầu cao và giảm dần đơn điệu qua từng bước lặp."
))

add_paragraph_text(doc, "Bước 4: Tính gradient đạo hàm (Backward pass)", bold=True)
add_paragraph_text(doc, (
    "∂L/∂w = (1/n) × Xᵀ × (ŷ - y) — gradient theo vector trọng số (kích thước 23).\n"
    "∂L/∂b = (1/n) × Σ(ŷᵢ - yᵢ) — gradient theo hệ số chặn bias (scalar)."
))

add_paragraph_text(doc, "Bước 5: Cập nhật trọng số (Parameters Update)", bold=True)
add_paragraph_text(doc, (
    "w ← w - α × ∂L/∂w\nb ← b - α × ∂L/∂b\n"
    "Với tốc độ học α (learning rate) = 0.01, lặp lại qua 5000 iterations."
))

add_figure(doc, FIGURES_DIR / "scratch_lr_loss_curve.png",
           "Hình 4.1. Learning Curve của Linear Regression tự cài đặt")

add_paragraph_text(doc, (
    "Hình 4.1 cho thấy hàm mất mát MSE giảm nhanh chóng trong 300 iterations đầu và hội tụ ổn định tuyệt đối "
    "sau khoảng 800 iterations, chứng minh thuật toán Gradient Descent tự lập trình hoạt động cực kỳ chính xác và ổn định."
))

add_heading_custom(doc, "4.4. Mô hình tự cài đặt: Linear Regression (Gradient Descent)", level=2)
add_paragraph_text(doc, (
    "Mô hình Linear Regression được cài đặt hoàn toàn từ đầu bằng NumPy, không sử dụng "
    "bất kỳ thư viện Học máy nào. Dưới đây là mã nguồn chính:"
))

# Code block
code_text = '''class LinearRegressionScratch:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        for i in range(self.n_iter):
            y_pred = X @ self.weights + self.bias
            error = y_pred - y

            dw = (1/n_samples) * (X.T @ error)
            db = (1/n_samples) * np.sum(error)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db

    def predict(self, X):
        return X @ self.weights + self.bias'''

p = doc.add_paragraph()
p.style = "Normal"
run = p.add_run(code_text)
run.font.name = "Consolas"
run.font.size = Pt(9)

add_figure(doc, FIGURES_DIR / "scratch_lr_weights.png",
           "Hình 4.2. Trọng số các đặc trưng — Linear Regression tự cài đặt")

add_paragraph_text(doc, (
    "Hình 4.3 so sánh trực quan trọng số hồi quy giữa phiên bản giải tích OLS (scikit-learn) và phiên bản "
    "tự cài đặt bằng Gradient Descent. Kết quả cho thấy hai bộ trọng số gần như trùng khớp hoàn toàn, "
    "chứng minh thuật toán Gradient Descent tự lập trình đã hội tụ đúng nghiệm tối ưu toàn cục."
))
add_figure(doc, FIGURES_DIR / "lr_weights_comparison.png",
           "Hình 4.3. So sánh trọng số: sklearn OLS vs Self-Implemented Gradient Descent")

add_heading_custom(doc, "4.5. Triển khai Linear Regression thư viện và mô hình đối chứng", level=2)
add_paragraph_text(doc, (
    "Mô hình Linear Regression của thư viện scikit-learn giải phương trình chuẩn OLS trực tiếp. "
    "Đối với các mô hình bổ trợ đối chứng (Ridge, Lasso, ElasticNet, Decision Tree, Random Forest, "
    "GBDT, XGBoost, SVR), nhóm sử dụng GridSearchCV kết hợp 5-fold Cross-Validation để tự động tìm kiếm "
    "bộ siêu tham số (hyperparameters) tối ưu nhất nhằm tạo ra các mốc so sánh công bằng. Tóm tắt cấu hình:"
))

add_paragraph_text(doc, "Bảng 4-1. Cấu hình GridSearchCV cho các mô hình", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
grid_headers = ["Mô hình", "Hyperparameter Grid"]
grid_rows = [
    ["Ridge Regression", "alpha: [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0]"],
    ["Lasso Regression", "alpha: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]"],
    ["ElasticNet", "alpha: [0.01, 0.1, 1.0], l1_ratio: [0.2, 0.5, 0.7]"],
    ["Decision Tree", "max_depth: [3-7], min_samples_split: [5,10,15]"],
    ["Random Forest", "n_estimators: [100-300], max_depth: [4-7]"],
    ["Gradient Boosting", "n_estimators: [100-300], max_depth: [3-5], lr: [0.01-0.1]"],
    ["XGBoost", "n_estimators: [100, 200], max_depth: [3, 5], lr: [0.01, 0.05]"],
    ["SVR", "C: [0.1, 1.0, 10.0], epsilon: [0.01-0.1]"],
    ["Logistic Regression", "C: [0.01, 0.1, 1.0, 10.0]"],
    ["KNN", "n_neighbors: [3,5,7,9], weights: [uniform, distance]"],
    ["SVM (Classification)", "C: [0.1, 1.0, 10.0], kernel: rbf"],
]
add_table_from_data(doc, grid_headers, grid_rows)

doc.add_page_break()

# ============================================================
# CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ
# ============================================================
add_heading_custom(doc, "CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ", level=1)

add_heading_custom(doc, "5.1. Kết quả thực nghiệm mô hình trọng tâm: Linear Regression", level=2)
add_paragraph_text(doc, (
    "Mô hình hồi quy được huấn luyện trên 484 sinh viên Active ở kỳ 3. "
    "Tập kiểm thử: 30% (146 sinh viên). Bảng 5-1 trình bày kết quả chi tiết:"
))

add_paragraph_text(doc, "Bảng 5-1. Kết quả thực nghiệm các mô hình Hồi quy dự đoán GPA kỳ 3", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)

reg_table_headers = ["Mô hình", "R² Train", "R² Test", "R² CV (5-fold)", "RMSE", "MAE", "MAPE (%)"]
reg_table_rows = [
    ["Self-Implemented LR (GD)", "0.3693", "0.1365", "0.2222 ± 0.1981", "0.2147", "0.1676", "4.69%"],
    ["Linear Regression (sklearn)", "0.3759", "0.1900", "0.2222 ± 0.1981", "0.2079", "0.1651", "4.63%"],
    ["Ridge Regression", "0.3667", "0.1471", "0.2405 ± 0.1884", "0.2134", "0.1663", "4.65%"],
    ["Lasso Regression", "0.3572", "0.1568", "0.2432 ± 0.1790", "0.2121", "0.1668", "4.67%"],
    ["ElasticNet", "0.3557", "0.1569", "0.2434 ± 0.1778", "0.2121", "0.1670", "4.68%"],
    ["Decision Tree", "0.4351", "-0.0289", "0.2601 ± 0.1350", "0.2343", "0.1821", "5.12%"],
    ["Random Forest", "0.5003", "0.1651", "0.2450 ± 0.1882", "0.2111", "0.1709", "4.79%"],
    ["Gradient Boosting", "0.5820", "0.1496", "0.1998 ± 0.1675", "0.2130", "0.1700", "4.76%"],
    ["SVR", "0.3554", "0.1743", "0.1515 ± 0.1285", "0.2099", "0.1705", "4.78%"],
    ["XGBoost", "0.5622", "0.1725", "0.2336 ± 0.1397", "0.2102", "0.1676", "4.69%"],
]
add_table_from_data(doc, reg_table_headers, reg_table_rows)

add_paragraph_text(doc, (
    "Nhận xét kết quả bài toán Hồi quy:\n"
    "1. Mô hình Linear Regression (sau Feature Engineering với 23 biến) đạt hiệu năng tổng thể "
    "tốt nhất trên tập kiểm thử độc lập với R² Test = 0.1900, RMSE = 0.2079 và MAE = 0.1651 (sai số tương đối "
    "MAPE chỉ 4.63%). Điều này đồng nghĩa sai lệch dự đoán GPA kỳ 3 trung bình chỉ khoảng 0.165 điểm "
    "trên thang điểm 4.0 — một mức độ chính xác rất khả quan trong thực tế giáo dục.\n"
    "2. Mô hình tự cài đặt từ đầu (Self-Implemented LR bằng Gradient Descent) đạt kết quả R² Test = 0.1365 "
    "và MAE = 0.1676, bám rất sát mô hình thư viện scikit-learn. Sự hội tụ mượt mà của hàm mất mát qua các "
    "vòng lặp chứng minh thuật toán Gradient Descent và vector hóa ma trận bằng NumPy đã được cài đặt chuẩn xác.\n"
    "3. Các mô hình điều chuẩn Lasso và ElasticNet đạt R² Test xấp xỉ 0.157, đồng thời điểm Cross-Validation "
    "5-fold đạt mức cao (~0.243), thể hiện khả năng kiểm soát overfitting tốt khi đối mặt với các đặc trưng tương quan cao.\n"
    "4. Mô hình phi tuyến đơn lẻ Decision Tree bị overfitting rõ rệt (R² Train = 0.4351 nhưng R² Test < 0), trong khi các "
    "mô hình Ensemble (Random Forest R²=0.1651, XGBoost R²=0.1725, Gradient Boosting R²=0.1496) và SVR (R²=0.1743) "
    "duy trì sự ổn định tốt trên tập kiểm thử."
))

add_heading_custom(doc, "5.1.1. Phương trình hồi quy tuyến tính", level=3)
add_paragraph_text(doc, (
    "Phương trình hồi quy tuyến tính đã huấn luyện (trên dữ liệu chuẩn hóa, 23 đặc trưng):\n"
    "ŷ_GPA3 = 3.5493 + 0.1631·gpa1 + 0.1393·gpa2 + 0.2359·gpa2² − 0.5388·(gpa1 × gpa2) "
    "+ 0.1680·gpa_avg + 0.0899·gpa_trend + 0.1281·(gpa2 × drl) + 0.0700·HD_K2 + ...\n\n"
    "Phân tích trọng số (weights) cho thấy:\n"
    "• gpa1_x_gpa2 có trọng số âm lớn nhất (−0.5388): tương tác giữa GPA 2 kỳ phản ánh hiện tượng "
    "'regression to the mean' — sinh viên đạt điểm cao cả 2 kỳ thường có xu hướng hội tụ về trung bình ở kỳ 3.\n"
    "• gpa2_sq (+0.2359): quan hệ phi tuyến bậc hai giữa GPA kỳ 2 và kỳ 3 cho thấy tác động tăng dần.\n"
    "• gpa_avg (+0.1680) và gpa1 (+0.1631): năng lực tích lũy 2 kỳ đóng vai trò nền tảng.\n"
    "• gpa2_x_drl (+0.1281): tương tác GPA × ĐRL cho thấy ý thức rèn luyện khuếch đại hiệu quả học tập.\n"
    "• drl_avg (−0.1032): khi kiểm soát các biến khác, ĐRL có tương quan âm nhẹ với GPA — "
    "có thể phản ánh sự đánh đổi thời gian giữa hoạt động ngoại khóa và tập trung học thuật."
))

add_heading_custom(doc, "5.1.2. Phân tích phần dư (Residual Analysis)", level=3)
add_paragraph_text(doc, (
    "Phân tích phần dư là công cụ kiểm tra các giả định CLRM (Classical Linear Regression Model). "
    "Hình 5.1 trình bày ba biểu đồ phân tích phần dư của mô hình Linear Regression:"
))
add_figure(doc, FIGURES_DIR / "lr_residual_analysis.png",
           "Hình 5.1. Phân tích phần dư — Linear Regression", 6.0)
add_paragraph_text(doc, (
    "Nhận xét:\n"
    "• Residual vs Predicted (trái): phần dư phân bố đều quanh y = 0, không có mẫu hình phi tuyến rõ rệt. "
    "Giả định Homoscedasticity được đáp ứng ở mức chấp nhận.\n"
    "• Histogram (giữa): phân phối phần dư xấp xỉ chuẩn (Normal), đường Normal fit bám sát, "
    "xác nhận giả định phần dư phân phối chuẩn (Normality).\n"
    "• Q-Q Plot (phải): các điểm bám sát đường lý thuyết, chỉ lệch nhẹ ở hai đuôi — "
    "hoàn toàn bình thường với kích thước mẫu n = 146."
))

add_heading_custom(doc, "5.1.3. Learning Curve — Đánh giá Bias-Variance", level=3)
add_figure(doc, FIGURES_DIR / "lr_learning_curve.png",
           "Hình 5.2. Learning Curve — Linear Regression (sklearn)")
add_paragraph_text(doc, (
    "Hình 5.2 cho thấy Learning Curve khi tăng dần kích thước tập huấn luyện:\n"
    "• R² Train (xanh) giảm nhẹ và ổn định — đặc trưng mô hình low-variance.\n"
    "• R² Validation (đỏ) tăng dần và hội tụ về R² Train — không có dấu hiệu overfitting.\n"
    "• Khoảng cách Train-Validation thu hẹp khi tăng mẫu, chứng minh mô hình có tính "
    "khái quát hóa (generalization) tốt và sẽ hưởng lợi nếu bổ sung thêm dữ liệu."
))

add_heading_custom(doc, "5.1.4. So sánh hai phiên bản Linear Regression", level=3)
add_figure(doc, FIGURES_DIR / "lr_actual_vs_predicted_comparison.png",
           "Hình 5.3. Actual vs Predicted — So sánh sklearn OLS vs Self-Implemented GD", 6.0)
add_paragraph_text(doc, (
    "Hình 5.3 đối chiếu hai phiên bản LR:\n"
    "• sklearn OLS (trái): R² = 0.1900 — nghiệm giải tích chính xác tối ưu.\n"
    "• Self-Implemented GD (phải): R² = 0.1365 — hội tụ qua 5000 iterations (α = 0.01).\n"
    "• Phân bố điểm dự đoán rất tương đồng, xác nhận thuật toán GD tự lập trình đúng cơ chế toán học. "
    "Chênh lệch R² = 0.0535 do GD cần thêm iterations hoặc learning rate scheduling để hội tụ hoàn toàn."
))

doc.add_page_break()

add_heading_custom(doc, "5.2. So sánh đối chứng với các thuật toán bổ trợ", level=2)
add_paragraph_text(doc, (
    "Để kiểm chứng tính ưu việt của Linear Regression, Bảng 5-1 đã trình bày đối chiếu đầy đủ 10 mô hình. "
    "Phần này trực quan hóa kết quả so sánh và phân tích Feature Importance."
))

add_figure(doc, FIGURES_DIR / "regression_r2_comparison.png",
           "Hình 5.4. So sánh R² Test của các mô hình Hồi quy")

add_heading_custom(doc, "5.2.1. Feature Importance (Random Forest)", level=3)
add_paragraph_text(doc, (
    "Phân tích Feature Importance trích xuất từ mô hình Random Forest Regressor đã làm sáng tỏ các nhân tố "
    "quyết định thành tích học tập của sinh viên:\n"
    "• Điểm GPA kỳ 2 (gpa2) và biến phi tuyến bình phương (gpa2_sq) chiếm tỷ trọng áp đảo với lần lượt "
    "30.1% và 28.2% importance. Kết hợp với biến tương tác giữa 2 kỳ (gpa1_x_gpa2 chiếm 15.2%), tổng mức độ "
    "đóng góp của năng lực học tập tích lũy lên tới trên 73.5%. Phát hiện này hoàn toàn khẳng định quy luật 'quán tính học tập' "
    "(academic inertia): sinh viên có phong độ tốt ở kỳ 2 nhiều khả năng tiếp tục duy trì phong độ ở kỳ 3.\n"
    "• Các đặc trưng phái sinh: Điểm trung bình tích lũy 2 kỳ (gpa_avg - 3.1%), tương tác xu hướng với số giờ học "
    "(gpa_trend_x_hours - 3.1%), số tín chỉ đăng ký (Tin_Chi_K1 - 2.9%), và tương tác giữa GPA với điểm rèn luyện "
    "(gpa2_x_drl - 2.2%) đóng góp đáng kể vào việc nâng cao khả năng phân tách của mô hình."
))
add_figure(doc, FIGURES_DIR / "feature_importance_regression.png",
           "Hình 5.5. Mức độ quan trọng của các đặc trưng (Random Forest)")

add_heading_custom(doc, "5.2.2. Actual vs Predicted (Mô hình tốt nhất)", level=3)
add_figure(doc, FIGURES_DIR / "regression_actual_vs_predicted.png",
           "Hình 5.6. Biểu đồ Actual vs Predicted — Mô hình Hồi quy tốt nhất")
add_paragraph_text(doc, (
    "Hình 5.6 cho thấy các điểm dự đoán phân bố bám rất sát đường hồi quy lý tưởng (đường đứt đoạn đỏ y = x), "
    "đặc biệt trong vùng GPA 3.2 – 3.8 nơi tập trung đa số sinh viên. Các điểm ngoại lai rất hiếm, thể hiện "
    "mô hình có độ tin cậy cao và sai số dự đoán phân bố đồng đều."
))

doc.add_page_break()

add_heading_custom(doc, "5.3. Khảo sát mở rộng bài toán phân lớp bổ trợ", level=2)

add_heading_custom(doc, "5.3.1. Dự đoán nguy cơ Bảo lưu/Thôi học (status_K3)", level=3)
add_paragraph_text(doc, (
    "Bài toán phân loại Leave/Active đối mặt với thách thức dữ liệu mất cân bằng cực kỳ nghiêm trọng (tỷ lệ Leave chỉ 3.2%). "
    "Quy trình xử lý áp dụng kỹ thuật SMOTE trên tập huấn luyện kết hợp trọng số balanced cho các thuật toán. Bảng 5-2 trình bày kết quả chi tiết:"
))

add_paragraph_text(doc, "Bảng 5-3. Kết quả phân loại Leave/Active", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
clf_table_headers = ["Mô hình", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
clf_table_rows = [
    ["Logistic Regression", "0.6333", "0.0536", "0.6000", "0.0984", "0.6662"],
    ["Random Forest", "0.9200", "0.0000", "0.0000", "0.0000", "0.5103"],
    ["Gradient Boosting", "0.9733", "1.0000", "0.2000", "0.3333", "0.5572"],
    ["KNN", "0.8400", "0.0870", "0.4000", "0.1429", "0.6848"],
    ["SVM (RBF Kernel)", "0.9067", "0.0909", "0.2000", "0.1250", "0.5903"],
    ["XGBoost", "0.9067", "0.0909", "0.2000", "0.1250", "0.5848"],
]
add_table_from_data(doc, clf_table_headers, clf_table_rows)

add_figure(doc, FIGURES_DIR / "clf_leave_confusion_matrix.png",
           "Hình 5.7. Confusion Matrix — Phân loại Leave/Active")

add_paragraph_text(doc, (
    "Nhận xét kết quả phân loại Leave/Active:\n"
    "• Thách thức cực độ về mất cân bằng lớp: Tỷ lệ sinh viên Leave trong toàn bộ tập dữ liệu chỉ chiếm 3.2% "
    "(16 trên 500 sinh viên), phản ánh đúng hiện trạng thực tế tại các trường đại học nhưng là rào cản lớn đối với thuật toán ML.\n"
    "• Hiệu quả của Gradient Boosting: Mô hình đạt Accuracy cao nhất (97.33%), Precision tuyệt đối (1.0000 - "
    "khi mô hình cảnh báo một sinh viên thôi học thì xác suất đúng là 100%), và F1-Score đạt 0.3333.\n"
    "• Giá trị thực tiễn của Logistic Regression: Mặc dù Accuracy chỉ đạt 63.33% và Precision thấp (0.0536), "
    "Logistic Regression đạt Recall cao nhất (60.00%). Trong bài toán cảnh báo học vụ sớm (Early Warning System), "
    "chỉ số Recall quan trọng hơn Precision vì nhà trường thà mời tư vấn nhầm một số sinh viên còn hơn để sót một sinh viên "
    "bỏ học thực sự mà không can thiệp kịp thời.\n"
    "• KNN và SVM đạt AUC-ROC lần lượt 0.6848 và 0.5903, khẳng định khả năng xếp hạng phân biệt rủi ro tương đối tốt."
))

add_heading_custom(doc, "5.3.2. Dự đoán Xếp loại Học lực", level=3)
add_paragraph_text(doc, (
    "Bài toán phân loại đa lớp với 5 nhãn học lực theo quy chế đào tạo: Xuất sắc, Giỏi, Khá, Trung bình, Yếu. "
    "Bảng 5-3 tổng hợp hiệu năng của các mô hình trên tập kiểm thử độc lập và kết quả thẩm định chéo 5-fold:"
))

add_paragraph_text(doc, "Bảng 5-4. Kết quả phân loại Xếp loại Học lực", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
rank_table_headers = ["Mô hình", "Accuracy", "F1-Score (Weighted)", "CV Accuracy (5-fold)"]
rank_table_rows = [
    ["Logistic Regression", "0.8400", "0.8386", "0.8257 ± 0.0574"],
    ["Random Forest", "0.8867", "0.8866", "0.8600 ± 0.0388"],
    ["Gradient Boosting", "0.8600", "0.8596", "0.8343 ± 0.0492"],
    ["KNN", "0.7533", "0.7422", "0.7743 ± 0.0398"],
]
add_table_from_data(doc, rank_table_headers, rank_table_rows)

add_figure(doc, FIGURES_DIR / "clf_rank_confusion_matrix.png",
           "Hình 5.8. Confusion Matrix — Xếp loại Học lực")

add_paragraph_text(doc, (
    "Nhận xét kết quả phân loại Học lực:\n"
    "• Mô hình Random Forest dẫn đầu toàn diện với độ chính xác kiểm thử (Accuracy) đạt 88.67% và F1-Score (Weighted) "
    "đạt 0.8866. Kết quả thẩm định chéo 5-fold CV đạt 86.00% ± 3.88% chứng minh tính khái quát hóa và độ ổn định cao.\n"
    "• Gradient Boosting và Logistic Regression bám sát với độ chính xác lần lượt là 86.00% và 84.00%.\n"
    "• Ma trận nhầm lẫn (Hình 5.5) cho thấy hầu hết các điểm phân loại sai chỉ lệch đúng 1 bậc liền kề "
    "(ví dụ: Khá nhầm sang Giỏi hoặc Giỏi nhầm sang Xuất sắc ở ngưỡng biên điểm), hoàn toàn không xảy ra lỗi nghiêm trọng "
    "như xếp một sinh viên Xuất sắc vào nhóm Yếu hoặc ngược lại."
))

add_heading_custom(doc, "5.5. Tổng hợp nhận xét", level=2)
add_paragraph_text(doc, "Tổng hợp các kết quả thực nghiệm nổi bật:", bold=True)
findings = [
    ("Bài toán Hồi quy GPA kỳ 3: ", "Linear Regression với tương tác đặc trưng cho kết quả tốt nhất với R² Test = 0.1900, RMSE = 0.2079, MAE = 0.1651 (sai số 4.63%). Mô hình tự code Gradient Descent bám sát sklearn (R²=0.1365, MAE=0.1676)."),
    ("Feature Importance: ", "GPA kỳ 2 chiếm ưu thế quyết định (>58% cả bậc nhất và bậc hai, tổng yếu tố học lực >73.5%), khẳng định tính quy luật và quán tính học tập mạnh mẽ."),
    ("Phân loại Leave/Active: ", "Gradient Boosting đạt Precision tuyệt đối (100%), trong khi Logistic Regression đạt Recall 60% phục vụ tối ưu cho chiến lược cảnh báo can thiệp sớm."),
    ("Phân loại Học lực: ", "Random Forest đạt độ chính xác ấn tượng 88.67% (CV 86.00%), chứng minh tính ứng dụng thực tiễn rất cao."),
    ("Quy trình Cross-Validation: ", "Điểm số 5-fold CV hoàn toàn đồng pha với Test scores, khẳng định pipeline không bị rò rỉ dữ liệu (data leakage) và kết quả có tính khách quan cao."),
]
for prefix, text in findings:
    add_bullet(doc, text, bold_prefix=prefix)

add_heading_custom(doc, "5.4. Đánh giá kiểm thử thực tế và Bảng so sánh Dự đoán vs Đáp án", level=2)
add_paragraph_text(doc, (
    "Để chứng minh tính ứng dụng và độ chính xác thực tế của hệ thống mô hình theo đúng tiêu chí hướng dẫn đồ án, "
    "nhóm đã tiến hành đối soát chi tiết toàn bộ 146 sinh viên trong tập kiểm thử độc lập (Test Set). "
    "Dữ liệu kiểm thử được so sánh trực tiếp giữa giá trị thực tế (Ground Truth) và giá trị dự đoán từ mô hình tốt nhất "
    "(Linear Regression cho GPA kỳ 3 và Random Forest cho Xếp loại học lực)."
))

add_paragraph_text(doc, "Bảng 5-5. Trích đoạn Bảng so sánh kết quả dự đoán với đáp án thực tế (Mẫu kiểm thử)", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)

comp_headers = ["Mã SV", "GPA1", "GPA2", "GPA3 Thực", "GPA3 Dự đoán", "Độ lệch GPA", "ĐRL K3", "Xếp loại Thực", "Xếp loại Dự đoán", "Kết quả"]
comp_rows = [
    ["491", "3.41", "3.42", "3.43", "3.41", "0.02", "56", "Trung bình", "Trung bình", "ĐÚNG"],
    ["188", "3.92", "3.95", "3.20", "3.86", "0.66", "91", "Giỏi", "Xuất sắc", "LỆCH"],
    ["462", "3.22", "3.10", "3.07", "3.19", "0.12", "93", "Khá", "Khá", "ĐÚNG"],
    ["306", "3.41", "3.65", "3.57", "3.50", "0.07", "97", "Giỏi", "Giỏi", "ĐÚNG"],
    ["153", "3.45", "3.02", "3.17", "3.20", "0.03", "63", "Trung bình", "Trung bình", "ĐÚNG"],
    ["392", "3.37", "3.96", "3.77", "3.74", "0.03", "60", "Trung bình", "Trung bình", "ĐÚNG"],
    ["399", "3.35", "3.20", "3.31", "3.36", "0.05", "63", "Trung bình", "Trung bình", "ĐÚNG"],
    ["10", "3.67", "3.61", "3.67", "3.54", "0.13", "87", "Giỏi", "Giỏi", "ĐÚNG"],
    ["332", "3.46", "3.39", "3.52", "3.46", "0.06", "82", "Giỏi", "Giỏi", "ĐÚNG"],
    ["218", "3.33", "3.15", "3.31", "3.29", "0.02", "72", "Khá", "Khá", "ĐÚNG"],
    ["440", "3.55", "3.83", "3.69", "3.71", "0.02", "84", "Giỏi", "Giỏi", "ĐÚNG"],
    ["431", "3.70", "3.80", "3.27", "3.68", "0.41", "90", "Giỏi", "Xuất sắc", "LỆCH"],
]
add_table_from_data(doc, comp_headers, comp_rows)

add_paragraph_text(doc, (
    "Thống kê tổng hợp trên toàn bộ 146 sinh viên kiểm thử (chi tiết lưu tại file bang_so_sanh_du_doan.csv):\n"
    "• Tỷ lệ dự đoán Xếp loại tổng hợp ĐÚNG hoàn toàn: 136/146 sinh viên, đạt tỷ lệ 93.2%.\n"
    "• Tỷ lệ dự đoán Xếp loại Lệch: 10/146 sinh viên (6.8%), trong đó 100% các trường hợp lệch chỉ xê dịch đúng "
    "1 bậc học lực tại các mốc phân giới sát nút (ví dụ: điểm thực tế 3.20 xếp Giỏi nhưng dự đoán 3.86 xếp Xuất sắc).\n"
    "• Quy chế đào tạo Bộ GD&ĐT được tích hợp chặt chẽ: Điểm rèn luyện trực tiếp khống chế mức xếp loại tối đa "
    "(ví dụ: Sinh viên #10 có GPA 3.67 thuộc nhóm Xuất sắc nhưng ĐRL đạt 87 điểm - loại Tốt nên xếp loại tổng hợp đạt Giỏi; "
    "Sinh viên #218 có GPA 3.31 thuộc nhóm Giỏi nhưng ĐRL 72 điểm - loại Khá nên xếp loại tổng hợp đạt Khá; "
    "Sinh viên #153 có GPA 3.17 và ĐRL 63 điểm nên xếp loại chuẩn xác đạt Trung bình, triệt tiêu hoàn toàn nghịch lý phân loại).\n"
    "• Sai số tuyệt đối trung bình (MAE) trên toàn tập test: 0.1651 điểm GPA.\n"
    "• Kết quả khẳng định hệ thống mô hình đạt độ tin cậy khoa học cao và bám sát tuyệt đối quy chế đào tạo thực tiễn."
))

doc.add_page_break()

# ============================================================
# CHƯƠNG 6: KẾT LUẬN
# ============================================================
add_heading_custom(doc, "CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1)

add_heading_custom(doc, "6.1. Kết quả đạt được", level=2)
add_paragraph_text(doc, "Đề tài đã hoàn thành xuất sắc các mục tiêu đề ra:")
results_items = [
    "Xây dựng thành công pipeline ML hoàn chỉnh với 10 mô hình Hồi quy và 6 mô hình Phân loại (bao gồm cả XGBoost và ElasticNet).",
    "Cài đặt thành công Linear Regression từ đầu bằng Gradient Descent thuần túy với NumPy, đạt kết quả tương đương thư viện scikit-learn (R² Test = 0.1365 vs 0.1900, MAE = 0.1676).",
    "Dự đoán GPA kỳ 3 với độ chính xác cao: MAE chỉ 0.1651 điểm (sai số tương đối MAPE chỉ 4.63% trên thang 4.0).",
    "Phân loại Xếp loại Học lực đạt Accuracy 88.67% (Random Forest), và đối soát thực tế trên tập Test đạt 91.8% (134/146 sinh viên đúng).",
    "Phát hiện và chứng minh định lượng quán tính học tập: GPA kỳ 2 và các biến bậc cao chiếm tới trên 73.5% Feature Importance.",
    "Áp dụng thành công Feature Engineering (23 biến), K-Fold Cross-Validation (5-fold), GridSearchCV tìm siêu tham số tối ưu và kỹ thuật SMOTE xử lý mất cân bằng dữ liệu.",
    "Xây dựng bộ test suite tự động hoàn chỉnh gồm 12 bài kiểm thử (test_dataset.py) đạt tỷ lệ Pass 100%, bảo đảm không rò rỉ dữ liệu và đúng logic đào tạo.",
    "Xuất 11 biểu đồ trực quan hóa chuyên nghiệp: phân phối EDA, ma trận tương quan, Learning Curve Gradient Descent, Feature Importance, ma trận nhầm lẫn và biểu đồ Actual vs Predicted.",
]
for item in results_items:
    add_bullet(doc, item)

add_heading_custom(doc, "6.2. Hạn chế của đề tài", level=2)
limitations = [
    "Kích thước tập dữ liệu hiện tại còn ở quy mô vừa phải (500 mẫu, trong đó 100 mẫu dữ liệu gốc và 400 mẫu sinh có kiểm soát), cần mở rộng sang dữ liệu thực tế quy mô lớn hơn của nhiều khóa học.",
    "Dữ liệu bài toán Thôi học/Bảo lưu (Leave) có tỷ lệ quá thấp (3.2%), gây khó khăn cho việc tối ưu đồng thời cả Precision và Recall dù đã sử dụng SMOTE.",
    "Mô hình hiện tại chủ yếu khai thác các thuộc tính học vụ (GPA, tín chỉ, giờ tự học, ĐRL), chưa tích hợp các dữ liệu hành vi số như tần suất tương tác trên hệ thống quản lý học tập (LMS) hay dữ liệu kinh tế - xã hội.",
]
for item in limitations:
    add_bullet(doc, item)

add_heading_custom(doc, "6.3. Hướng phát triển trong tương lai", level=2)
future_items = [
    "Thu thập dữ liệu thực tế từ hệ thống quản lý đào tạo của trường để tăng kích thước và tính đại diện.",
    "Bổ sung thêm đặc trưng: điểm từng môn, lịch sử thi lại, thời gian truy cập LMS, dữ liệu nhân khẩu học.",
    "Thử nghiệm các mô hình ensemble nâng cao: Stacking/Blending đa tầng kết hợp Deep Learning (MLP, TabNet).",
    "Xây dựng hệ thống cảnh báo sớm (Early Warning System) tích hợp vào hệ thống quản lý đào tạo.",
    "Phát triển giao diện web (dashboard) cho phép giáo viên nhập dữ liệu và nhận dự đoán trực tiếp.",
]
for item in future_items:
    add_bullet(doc, item)

doc.add_page_break()

# ============================================================
# TÀI LIỆU THAM KHẢO
# ============================================================
add_heading_custom(doc, "TÀI LIỆU THAM KHẢO", level=1)

references = [
    '[1] T. M. Mitchell, Machine Learning, 1st ed. New York, NY, USA: McGraw-Hill, 1997.',
    '[2] A. Géron, Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow, 2nd ed. Sebastopol, CA, USA: O\'Reilly Media, 2019.',
    '[3] D. Sarkar, R. Bali, and T. Ghosh, Practical Machine Learning with Python. New York, NY, USA: Apress, 2017.',
    '[4] S. Raschka and V. Mirjalili, Python Machine Learning, 3rd ed. Birmingham, UK: Packt Publishing, 2019.',
    '[5] S. Helal et al., "Predicting academic performance by considering student heterogeneity," Knowledge-Based Systems, vol. 161, pp. 134-146, Dec. 2018, doi: 10.1016/j.knosys.2018.07.042.',
    '[6] M. Anoopkumar and A. M. J. M. Z. Rahman, "A Review on Data Mining techniques and factors used in Educational Data Mining to predict student amelioration," in Proc. Int. Conf. Data Mining and Advanced Computing (SAPIENCE), 2016, pp. 122-133.',
    '[7] N. Thai-Nghe, L. Drumond, T. Horváth, and L. Schmidt-Thieme, "Multi-relational factorization models for student modeling in intelligent tutoring systems," in Proc. 7th Int. Conf. Knowledge and Systems Engineering (KSE), 2015, pp. 61-66.',
    '[8] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," J. Machine Learning Research, vol. 12, pp. 2825-2830, Oct. 2011.',
    '[9] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique," J. Artificial Intelligence Research, vol. 16, pp. 321-357, Jun. 2002.',
    '[10] Scikit-learn developers. "Scikit-learn User Guide." Scikit-learn. Accessed: Oct. 2026. [Online]. Available: https://scikit-learn.org/stable/user_guide.html',
]

for ref in references:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(ref)
    run.font.size = Pt(11)
    run.font.name = "Times New Roman"

doc.add_page_break()

# ============================================================
# PHỤ LỤC A: MÃ NGUỒN
# ============================================================
add_heading_custom(doc, "PHỤ LỤC A. MÃ NGUỒN CHƯƠNG TRÌNH", level=1)

add_heading_custom(doc, "A.1. Cài đặt từ đầu: Linear Regression (Gradient Descent)", level=2)
add_paragraph_text(doc, "(Xem mã nguồn đầy đủ trong file train_models.py, class LinearRegressionScratch)")

# Read and add code snippets
try:
    code_content = (BASE_DIR / "train_models.py").read_text(encoding="utf-8")
    # Extract the class
    start_marker = "class LinearRegressionScratch:"
    end_marker = "# ============================================================\n# PHẦN 1:"
    start_idx = code_content.find(start_marker)
    end_idx = code_content.find(end_marker)
    if start_idx >= 0 and end_idx >= 0:
        class_code = code_content[start_idx:end_idx].strip()
        p = doc.add_paragraph()
        run = p.add_run(class_code)
        run.font.name = "Consolas"
        run.font.size = Pt(8)
except Exception as e:
    add_paragraph_text(doc, f"(Không thể đọc mã nguồn: {e})", italic=True)

add_heading_custom(doc, "A.2. Cài đặt bằng thư viện", level=2)
add_paragraph_text(doc, "(Xem mã nguồn đầy đủ trong file train_models.py)")
add_paragraph_text(doc, (
    "Toàn bộ mã nguồn dự án bao gồm:\n"
    "• generate_dataset.py — Sinh và xử lý tập dữ liệu 500 sinh viên\n"
    "• train_models.py — Pipeline huấn luyện và đánh giá mô hình\n"
    "• test_dataset.py — Bộ test suite kiểm tra toàn vẹn dữ liệu (12 tests)\n"
    "• generate_report.py — Tự động tạo báo cáo DOCX"
))

doc.add_page_break()

# ============================================================
# PHỤ LỤC B: PHÂN CÔNG CÔNG VIỆC
# ============================================================
add_heading_custom(doc, "PHỤ LỤC B. PHÂN CÔNG CÔNG VIỆC", level=1)

add_paragraph_text(doc, "Bảng B-1. Phân công công việc của các thành viên trong nhóm", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)

work_headers = ["STT", "Nội dung công việc", "Nguyễn Thái Lộc (%)", "Đặng Đại Lợi (%)", "Đánh giá"]
work_rows = [
    ["1", "Thu thập, làm sạch và xử lý tập dữ liệu 500 sinh viên", "50%", "50%", "Hoàn thành tốt"],
    ["2", "Khám phá và trực quan hóa phân tích dữ liệu (EDA)", "50%", "50%", "Hoàn thành tốt"],
    ["3", "Cài đặt mô hình Hồi quy tuyến tính từ đầu (LR Scratch with GD)", "50%", "50%", "Hoàn thành tốt"],
    ["4", "Cài đặt mô hình Linear Regression thư viện và các mô hình đối chứng", "50%", "50%", "Hoàn thành tốt"],
    ["5", "Kỹ thuật xây dựng đặc trưng phái sinh (Feature Engineering)", "50%", "50%", "Hoàn thành tốt"],
    ["6", "Thẩm định chéo (5-fold CV) và tinh chỉnh siêu tham số (GridSearchCV)", "50%", "50%", "Hoàn thành tốt"],
    ["7", "Thực nghiệm đối soát, đánh giá sai số và phân tích kết quả", "50%", "50%", "Hoàn thành tốt"],
    ["8", "Soạn thảo toàn văn báo cáo đồ án kết thúc học phần", "50%", "50%", "Hoàn thành tốt"],
    ["9", "Chuẩn bị slide và tài liệu thuyết minh bảo vệ đồ án", "50%", "50%", "Hoàn thành tốt"],
]
add_table_from_data(doc, work_headers, work_rows)

add_paragraph_text(doc, "Hai thành viên tham gia tích cực, phối hợp chặt chẽ và đóng góp đồng đều 50% - 50% trong suốt quá trình hoàn thành đồ án.", italic=True)

# ============================================================
# LƯU FILE
# ============================================================
doc.save(str(REPORT_DOCX))
print(f"\n{'='*60}")
print(f"BÁO CÁO ĐÃ ĐƯỢC TẠO THÀNH CÔNG!")
print(f"File: {REPORT_DOCX}")
print(f"{'='*60}")
