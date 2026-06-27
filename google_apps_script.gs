/**
 * Google Apps Script nhận kết quả từ Streamlit app và ghi vào Google Sheet.
 *
 * Cách triển khai:
 * 1. Tạo Google Sheet mới, đặt tên ví dụ: Ket qua AI Quiz Chuong 6.
 * 2. Vào Extensions -> Apps Script.
 * 3. Dán toàn bộ mã này, bấm Save.
 * 4. Bấm Deploy -> New deployment -> Web app.
 * 5. Execute as: Me.
 * 6. Who has access: Anyone.
 * 7. Bấm Deploy, cấp quyền, copy Web app URL.
 * 8. Dán Web app URL vào ô Google Apps Script Web App URL trong app Streamlit.
 *
 * Script sẽ tự tạo 2 sheet:
 * - KetQua: mỗi lượt nộp bài là một dòng tổng hợp.
 * - ChiTiet: mỗi câu trả lời là một dòng để giáo viên phân tích lỗi sai.
 */

const SUMMARY_SHEET = "KetQua";
const DETAIL_SHEET = "ChiTiet";

const SUMMARY_HEADERS = [
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
  "percent"
];

const DETAIL_HEADERS = [
  "submitted_at",
  "assignment_id",
  "student_name",
  "student_class",
  "question_index",
  "question",
  "selected",
  "correct_answer",
  "is_correct",
  "explanation"
];

function getOrCreateSheet_(spreadsheet, name, headers) {
  const sheet = spreadsheet.getSheetByName(name) || spreadsheet.insertSheet(name);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold").setBackground("#e8f0fe");
  }
  return sheet;
}

function jsonOutput_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  getOrCreateSheet_(ss, SUMMARY_SHEET, SUMMARY_HEADERS);
  getOrCreateSheet_(ss, DETAIL_SHEET, DETAIL_HEADERS);
  return jsonOutput_({ ok: true, message: "Sheets are ready." });
}

function doPost(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const summarySheet = getOrCreateSheet_(ss, SUMMARY_SHEET, SUMMARY_HEADERS);
    const detailSheet = getOrCreateSheet_(ss, DETAIL_SHEET, DETAIL_HEADERS);
    const data = JSON.parse(e.postData.contents || "{}");
    const submittedAt = data.submitted_at || new Date().toISOString();
    const details = Array.isArray(data.details) ? data.details : [];

    summarySheet.appendRow([
      submittedAt,
      data.assignment_id || "",
      data.assignment_title || "",
      data.teacher || "",
      data.topic || "",
      data.question_type || "",
      data.seed || "",
      data.student_name || "",
      data.student_class || "",
      Number(data.score || 0),
      Number(data.total || 0),
      Number(data.percent || 0)
    ]);

    if (details.length > 0) {
      const detailRows = details.map(function(item) {
        return [
          submittedAt,
          data.assignment_id || "",
          data.student_name || "",
          data.student_class || "",
          item.index || "",
          item.question || "",
          item.selected || "",
          item.correct_answer || "",
          item.is_correct === true,
          item.explanation || ""
        ];
      });
      detailSheet
        .getRange(detailSheet.getLastRow() + 1, 1, detailRows.length, DETAIL_HEADERS.length)
        .setValues(detailRows);
    }

    return jsonOutput_({
      ok: true,
      message: "Saved",
      summary_rows: summarySheet.getLastRow() - 1,
      detail_rows: detailSheet.getLastRow() - 1
    });
  } catch (err) {
    return jsonOutput_({
      ok: false,
      message: String(err && err.message ? err.message : err)
    });
  }
}

function doGet() {
  setupSheets();
  return ContentService
    .createTextOutput("AI Quiz Chuong 6 receiver is running. Sheets KetQua and ChiTiet are ready.")
    .setMimeType(ContentService.MimeType.TEXT);
}
