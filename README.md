# AI Quiz Chương 6 - Toán 10 Kết nối tri thức

Ứng dụng Streamlit giúp giáo viên tạo bài tập online cho Chương 6: Hàm số, đồ thị và ứng dụng.

## Chức năng

- Giáo viên chọn dạng toán:
  - Bài 15: Hàm số
  - Bài 16: Hàm số bậc hai
  - Bài 17: Dấu tam thức bậc hai
  - Bài 17: Bất phương trình bậc hai
  - Bài 18: Phương trình quy về phương trình bậc hai
- Chọn số câu và loại câu hỏi:
  - Trắc nghiệm 4 lựa chọn
  - Đúng/Sai
- Sinh tự động câu hỏi, đáp án và hướng dẫn ngắn.
- Tạo link bài tập để học sinh làm online.
- Gửi kết quả về Google Sheet thông qua Google Apps Script.

## Chạy trên máy

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Triển khai lên Streamlit Community Cloud

1. Đưa thư mục này lên GitHub.
2. Vào <https://streamlit.io/cloud>.
3. Tạo app mới, chọn repo GitHub.
4. Main file path: `streamlit_app.py`.
5. Deploy.

## Google Apps Script

Mở file `google_apps_script.gs`, làm theo hướng dẫn trong phần chú thích đầu file.
Sau khi deploy Apps Script dạng Web App, copy URL và dán vào app khi tạo bài.

## Gợi ý dùng trong sáng kiến

Ứng dụng này có thể xem là sản phẩm minh chứng cho giải pháp:

> Sử dụng Python xây dựng hệ thống bài tập tương tự nhằm rèn kỹ năng giải toán Chương 6 - Hàm số, đồ thị và ứng dụng cho học sinh yếu môn Toán 10, bộ Kết nối tri thức.
