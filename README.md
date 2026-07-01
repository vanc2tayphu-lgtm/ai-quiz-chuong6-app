# AI Quiz Chương 6 - Toán 10 Kết nối tri thức

Ứng dụng Streamlit giúp giáo viên tạo bài tập online cho Toán 10, hiện hỗ trợ Chương 6 và Chương 9.

## Chức năng

- Giáo viên chọn theo 3 tầng: `Chọn chương`, `Chọn bài`, rồi `Dạng cụ thể`.
  - Bài 15: tính giá trị, điểm thuộc đồ thị, tập xác định, tập xác định chứa tham số, đồng biến/nghịch biến, đồng biến/nghịch biến chứa tham số, bảng dữ liệu thực tế.
  - Bài 16: xác định hàm số bậc hai, đỉnh/trục đối xứng, giao điểm với trục, cực trị/đơn điệu, bảng giá trị/đồ thị, tham số đơn điệu, bài toán thực tế.
  - Bài 17: xét dấu tam thức, đọc bảng xét dấu/đồ thị, tập xác định căn tam thức, giải bất phương trình, tham số để tam thức không đổi dấu, bài toán thực tiễn.
  - Bài 18: phương trình dạng `√f(x)=g(x)`, `√f(x)=√g(x)`, phương trình trùng phương.
- Chương 9: phương pháp tọa độ trong mặt phẳng.
  - Tọa độ vectơ: tọa độ điểm/vectơ trong mặt phẳng, độ dài vectơ, tích vô hướng, trung điểm đoạn thẳng, trọng tâm tam giác.
  - Đường thẳng: phương trình tham số, phương trình tổng quát, vị trí tương đối, giao điểm, góc giữa hai đường thẳng, khoảng cách từ điểm đến đường thẳng.
  - Đường tròn: tâm/bán kính, viết phương trình, tiếp tuyến/vị trí tương đối.
  - Conic: elip, hypebol, parabol, bài toán thực tế với conic.
- Chọn số câu và loại câu hỏi:
  - Trắc nghiệm 4 lựa chọn
  - Đúng/Sai 4 ý a), b), c), d)
  - Trả lời ngắn
- Sinh tự động câu hỏi, đáp án và hướng dẫn ngắn.
- Tạo link bài tập để học sinh làm online.
- Gửi kết quả về Google Sheet thông qua Google Apps Script.
- Giao diện giáo viên dùng các tab `Thiết lập & chia sẻ`, `Xem trước đề`, `Thống kê`.
- Tải đề dưới dạng JSON hoặc file Word `.docx` gồm phần đề và đáp án/hướng dẫn.

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
