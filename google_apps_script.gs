/**
 * Google Apps Script nhận kết quả từ Streamlit app và ghi gọn vào Google Sheet.
 *
 * Cách triển khai:
 * 1. Tạo Google Sheet mới.
 * 2. Vào Extensions -> Apps Script.
 * 3. Dán toàn bộ mã này, bấm Save.
 * 4. Deploy -> New deployment -> Web app.
 * 5. Execute as: Me.
 * 6. Who has access: Anyone.
 * 7. Deploy, cấp quyền, copy Web app URL.
 * 8. Dán Web app URL vào app Streamlit.
 *
 * Sheet chỉ có các cột:
 * Thứ tự | Họ tên học sinh | Lớp | Ngày làm bài | Kết quả | Kết quả từng câu
 */

const RESULT_SHEET = "KetQua";
const RESULT_HEADERS = [
  "Thứ tự",
  "Họ tên học sinh",
  "Lớp",
  "Ngày làm bài",
  "Kết quả",
  "Kết quả từng câu"
];

function jsonOutput_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function getResultSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(RESULT_SHEET) || ss.insertSheet(RESULT_SHEET);

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(RESULT_HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, RESULT_HEADERS.length)
      .setFontWeight("bold")
      .setBackground("#e8f0fe");
    sheet.setColumnWidths(1, RESULT_HEADERS.length, 150);
    sheet.setColumnWidth(2, 220);
    sheet.setColumnWidth(6, 460);
  }

  return sheet;
}

function formatDate_(value) {
  const date = value ? new Date(value) : new Date();
  return Utilities.formatDate(date, Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss");
}

function formatQuestionResults_(details) {
  if (!Array.isArray(details) || details.length === 0) {
    return "";
  }

  return details.map(function(item) {
    const index = item.index || "";
    const isCorrect = item.is_correct === true;
    return index + ": " + (isCorrect ? "Đúng" : "Sai");
  }).join("; ");
}

function setupSheets() {
  getResultSheet_();
  return jsonOutput_({ ok: true, message: "Sheet KetQua is ready." });
}

function doPost(e) {
  try {
    const sheet = getResultSheet_();
    const data = JSON.parse(e.postData.contents || "{}");
    const nextIndex = Math.max(sheet.getLastRow(), 1);
    const score = Number(data.score || 0);
    const total = Number(data.total || 0);
    const percent = Number(data.percent || 0);
    const resultText = score + "/" + total + " (" + percent + "%)";

    sheet.appendRow([
      nextIndex,
      data.student_name || "",
      data.student_class || "",
      formatDate_(data.submitted_at),
      resultText,
      formatQuestionResults_(data.details)
    ]);

    return jsonOutput_({
      ok: true,
      message: "Saved",
      rows: sheet.getLastRow() - 1
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
    .createTextOutput("AI Quiz receiver is running. Sheet KetQua is ready.")
    .setMimeType(ContentService.MimeType.TEXT);
}
