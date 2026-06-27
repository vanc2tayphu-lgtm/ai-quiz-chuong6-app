/**
 * Google Apps Script nhận kết quả từ Streamlit app và ghi vào Google Sheet.
 *
 * Cách dùng:
 * 1. Tạo Google Sheet mới.
 * 2. Extensions -> Apps Script.
 * 3. Dán toàn bộ mã này, lưu lại.
 * 4. Deploy -> New deployment -> Web app.
 * 5. Execute as: Me. Who has access: Anyone.
 * 6. Copy Web App URL và dán vào ô "Google Apps Script Web App URL" trong app.
 */

function doPost(e) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("KetQua") || ss.insertSheet("KetQua");

  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "submitted_at",
      "assignment_id",
      "assignment_title",
      "teacher",
      "topic",
      "question_type",
      "seed",
      "student_name",
      "student_class",
      "score",
      "total",
      "percent",
      "details_json"
    ]);
  }

  const data = JSON.parse(e.postData.contents);
  sheet.appendRow([
    data.submitted_at || new Date().toISOString(),
    data.assignment_id || "",
    data.assignment_title || "",
    data.teacher || "",
    data.topic || "",
    data.question_type || "",
    data.seed || "",
    data.student_name || "",
    data.student_class || "",
    data.score || 0,
    data.total || 0,
    data.percent || 0,
    JSON.stringify(data.details || [])
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService
    .createTextOutput("AI Quiz Chương 6 receiver is running.")
    .setMimeType(ContentService.MimeType.TEXT);
}
