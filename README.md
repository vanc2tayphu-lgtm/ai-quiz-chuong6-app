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
  - Đúng/Sai 4 ý a), b), c), d)
  - Trả lời ngắn
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

## Google Sheet và Google Apps Script

Mở file `google_apps_script.gs`, làm theo hướng dẫn trong phần chú thích đầu file.
Sau khi deploy Apps Script dạng Web App, copy URL và dán vào app khi tạo bài.

Thiết lập nhanh:

1. Tạo Google Sheet mới.
2. Vào `Extensions -> Apps Script`.
3. Dán toàn bộ nội dung file `google_apps_script.gs`.
4. Bấm `Deploy -> New deployment -> Web app`.
5. Chọn `Execute as: Me`.
6. Chọn `Who has access: Anyone`.
7. Copy `Web app URL`.
8. Dán URL này vào ô `Google Apps Script Web App URL` trong app Streamlit.

Khi học sinh nộp bài, Google Sheet sẽ có sheet `KetQua` với 6 cột:

- `Thứ tự`
- `Họ tên học sinh`
- `Lớp`
- `Ngày làm bài`
- `Kết quả`
- `Kết quả từng câu`

Cột `Kết quả từng câu` chỉ ghi đúng/sai theo từng câu hoặc từng ý, ví dụ:
`1: Đúng; 2: Sai; 3a: Đúng; 3b: Sai`.

## Giao diện học sinh trên điện thoại

Trang làm bài của học sinh được thiết kế mobile-first:

- Học sinh nhập họ tên và lớp ngay trên trang, không cần mở sidebar.
- Đáp án là các nút lớn, xếp dọc để dễ bấm trên điện thoại.
- Câu đúng/sai hiển thị theo từng ý a), b), c), d), học sinh chọn Đúng hoặc Sai cho từng ý.
- Câu trả lời ngắn dùng 4 ô ký tự; học sinh nhập dấu phẩy thập phân, ví dụ `15,5`, `3,67`, `-1,25`.
- Học sinh phải chọn đủ đáp án mới nộp được bài hợp lệ.
- Sau khi nộp, app hiển thị điểm và gửi kết quả về Google Sheet nếu đã cấu hình Apps Script URL.

## Gợi ý dùng trong sáng kiến

Ứng dụng này có thể xem là sản phẩm minh chứng cho giải pháp:

> Sử dụng Python xây dựng hệ thống bài tập tương tự nhằm rèn kỹ năng giải toán Chương 6 - Hàm số, đồ thị và ứng dụng cho học sinh yếu môn Toán 10, bộ Kết nối tri thức.
