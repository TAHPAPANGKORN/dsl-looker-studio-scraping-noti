from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import re
import smtplib
from typing import Any, Dict, List, Tuple
from src.config import AppConfig
from src.models import FIELD_NAMES_TH

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Renders visual Looker Studio templates and sends SMTP notifications."""
    
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @staticmethod
    def parse_corrections(text: str) -> List[Tuple[str, str]]:
        """Parses a concatenated Looker Studio simple-table string into key-value pairs."""
        if not text or text == "-":
            return []
            
        text = text.replace("ไม่มีข้อมูล", "").replace("No data-", "").replace("No data", "").strip()
        pattern = r"(รายการแก้ไข\s*(?:\(\d+\))?(?:\s*\d+)?)"
        parts = re.split(pattern, text)
        
        pairs: List[Tuple[str, str]] = []
        current_key = None
        
        for part in parts:
            part_str = part.strip()
            if not part_str:
                continue
            if part_str.startswith("รายการแก้ไข"):
                current_key = part_str
            else:
                if current_key:
                    val = part_str.rstrip("-").strip()
                    # Strip standard row index prefix from value if present
                    key_split = current_key.split()
                    key_last_word = key_split[-1] if key_split else ""
                    if key_last_word.isdigit():
                        idx_prefix = key_last_word
                        if val.startswith(idx_prefix):
                            val = val[len(idx_prefix):].strip()
                    
                    val = val.lstrip("-").strip()
                    if not val or val == "-":
                        val = "-"
                    pairs.append((current_key, val))
                    current_key = None
                    
        if current_key:
            pairs.append((current_key, "-"))
        return pairs

    @staticmethod
    def get_field_display(val: Any) -> str:
        """Normalizes missing values for visualization."""
        if val is None:
            return "-"
        val_str = str(val).strip()
        if not val_str or val_str in ["ไม่มีข้อมูล", "No data-", "No data", "-"]:
            return "-"
        return val_str

    def format_cell_with_extras(self, status_key: str, extra_keys: List[str], status_dict: Dict[str, Any]) -> str:
        """Formats a status cell, appending red warnings or corrections tables below."""
        status_val = self.get_field_display(status_dict.get(status_key))
        
        normal_extras: List[str] = []
        corrections_extras: List[Tuple[str, str]] = []
        
        for ek in extra_keys:
            ev = self.get_field_display(status_dict.get(ek))
            if ev != "-":
                if ek in ["app_doc_corrections_list", "app_doc_corrections_list_2", "step_1_corrections_list", "step_1_corrections_list_2"]:
                    corrections_extras.append((ek, ev))
                else:
                    label = FIELD_NAMES_TH.get(ek, ek)
                    normal_extras.append(f"<strong>{label}:</strong> {ev}")
                    
        cell_html = f"<div>{status_val}</div>"
        
        if normal_extras:
            extras_html = "<br/>".join(normal_extras)
            cell_html += f"""
            <div style="margin-top: 8px; padding: 10px; border: 1px solid #ffcdd2; border-radius: 6px; background-color: #ffebee; font-size: 0.9em; color: #c62828; line-height: 1.6;">
              <div style="font-weight: bold; margin-bottom: 6px; text-align: center; border-bottom: 1px solid #ffcdd2; padding-bottom: 4px;">ตรวจเอกสารแจ้งแก้ไข</div>
              {extras_html}
            </div>
            """
            
        for ek, ev in corrections_extras:
            pairs = self.parse_corrections(ev)
            if pairs:
                rows_html = ""
                for key, val in pairs:
                    rows_html += f"""
                    <tr style="border-bottom: 1px solid #edf2f7;">
                      <td style="padding: 8px 12px; width: 130px; background-color: #1e88e5; color: #ffffff; font-weight: bold; font-size: 0.85em; text-align: center; border: 1px solid #e2e8f0; vertical-align: middle;">
                        {key}
                      </td>
                      <td style="padding: 8px 12px; color: #2d3748; background-color: #ffffff; font-size: 0.9em; border: 1px solid #e2e8f0; vertical-align: middle;">
                        {val}
                      </td>
                    </tr>
                    """
                cell_html += f"""
                <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-top: 12px; padding: 15px;">
                  <h4 style="margin-top: 0; margin-bottom: 10px; color: #d32f2f; font-size: 0.95em; font-weight: bold; text-align: center;">
                    รายการแจ้งแก้ไข
                  </h4>
                  <table style="width: 100%; border-collapse: collapse; margin: 0;">
                    <tbody>
                      {rows_html}
                    </tbody>
                  </table>
                </div>
                """
        return cell_html

    def send_notification(self, receiver_email: str, name: str, new_status: Dict[str, Any], dashboard_url: str) -> bool:
        """Sends the structured dashboard update notification email."""
        if not self.config.sender_email or not self.config.sender_password:
            logger.warning("SMTP Sender Email or App Password is empty. Skipping notification dispatch.")
            return False

        subject = "แจ้งเตือน: สถานะ กยศ. มีการอัปเดตข้อมูลใหม่"
        
        # Format Section 1 Values
        s1_r1_status = self.format_cell_with_extras("app_doc_intake_status", ["app_doc_correct_docs", "app_doc_correct_officer", "app_doc_correct_date", "app_doc_corrections_list", "app_doc_corrections_list_2"], new_status)
        s1_r1_date = self.get_field_display(new_status.get("app_doc_intake_date"))
        s1_r2_status = self.get_field_display(new_status.get("loan_doc_status"))
        s1_r2_date = self.get_field_display(new_status.get("loan_doc_date"))

        # Format Section 2 Values
        s2_r1_status = self.format_cell_with_extras("step_1_status", ["step_1_correct_docs", "step_1_correct_officer", "step_1_correct_date", "step_1_corrections_list", "step_1_corrections_list_2"], new_status)
        s2_r1_date = self.get_field_display(new_status.get("step_1_date"))
        s2_r2_status = self.format_cell_with_extras("step_2_status", ["step_2_correct_before", "step_2_correct_docs", "step_2_correct_date", "step_2_disburse_num"], new_status)
        s2_r2_date = self.get_field_display(new_status.get("step_2_date"))
        s2_r3_status = self.format_cell_with_extras("step_3_status", ["step_3_delivery_num", "step_3_delivery_date", "step_3_corrected_bank"], new_status)
        s2_r3_date = self.get_field_display(new_status.get("step_3_date"))
        s2_r4_status = self.format_cell_with_extras("step_4_status", ["step_4_correct_docs", "step_4_disburse_num", "step_4_bank_audit_err", "step_4_officer_seq", "step_4_officer_date", "step_4_corrected_bank", "step_4_corrected_date"], new_status)
        s2_r4_date = self.get_field_display(new_status.get("step_4_date"))
        s2_r5_status = self.get_field_display(new_status.get("step_5_status"))
        s2_r5_date = self.get_field_display(new_status.get("step_5_date"))

        student_name = self.get_field_display(new_status.get("student_name", name))
        student_id = self.get_field_display(new_status.get("student_id", "-"))
        borrower_type = self.get_field_display(new_status.get("borrower_type", "-"))

        body = f"""
        <html>
          <head>
            <meta charset="utf-8">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
          </head>
          <body style="margin: 0; padding: 0; background-color: #f4f6f8; font-family: 'Prompt', 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333333;">
            <div style="max-width: 680px; margin: 0 auto; padding: 30px 20px;">
              
              <!-- 👥 ข้อมูลผู้กู้ยืม Card -->
              <div style="background-color: #ffffff; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025); margin-bottom: 25px;">
                <h2 style="margin-top: 0; margin-bottom: 16px; color: #1a202c; font-size: 1.25em; font-weight: bold; border-bottom: 2px solid #edf2f7; padding-bottom: 10px;">
                  👥 ข้อมูลผู้กู้ยืม
                </h2>
                <table style="width: 100%; border-collapse: collapse; font-size: 1.05em; color: #4a5568; line-height: 1.8;">
                  <tr>
                    <td style="padding: 4px 0; width: 110px; font-weight: bold; color: #2d3748; vertical-align: top;">ชื่อ-สกุล:</td>
                    <td style="padding: 4px 0; color: #1a202c;">{student_name}</td>
                  </tr>
                  <tr>
                    <td style="padding: 4px 0; font-weight: bold; color: #2d3748; vertical-align: top;">รหัสนิสิต:</td>
                    <td style="padding: 4px 0; color: #1a202c;">{student_id}</td>
                  </tr>
                  <tr>
                    <td style="padding: 4px 0; font-weight: bold; color: #2d3748; vertical-align: top;">ประเภทผู้กู้:</td>
                    <td style="padding: 4px 0; color: #1a202c;">{borrower_type}</td>
                  </tr>
                </table>
              </div>

              <!-- Section 1 Header -->
              <div style="border-left: 6px solid #2e7d32; padding-left: 12px; margin-bottom: 12px; margin-top: 25px;">
                <h3 style="margin: 0; color: #2e7d32; font-size: 1.15em; font-weight: bold;">📋 1. ขั้นตอนการส่งเอกสารคำขอเสนอขอกู้ยืม</h3>
              </div>

              <!-- Section 1 Table Card -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025); overflow: hidden; margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse; margin: 0; font-size: 0.95em;">
                  <thead>
                    <tr style="background-color: #2e7d32; color: #ffffff;">
                      <th style="padding: 14px 16px; font-weight: bold; text-align: left; border-bottom: 1px solid #2e7d32; width: 35%;">ขั้นตอน</th>
                      <th style="padding: 14px 16px; font-weight: bold; text-align: left; border-bottom: 1px solid #2e7d32; width: 45%;">รายละเอียดสถานะ / ข้อมูล</th>
                      <th style="padding: 14px 16px; font-weight: bold; text-align: center; border-bottom: 1px solid #2e7d32; width: 20%;">วันที่อัปเดต</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style="border-bottom: 1px solid #edf2f7; background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">1. งาน กยศ.ม.บูรพา ลงรับเอกสารของนิสิต</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s1_r1_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s1_r1_date}</td>
                    </tr>
                    <tr style="background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">2. สถานะเอกสารประกอบคำขอกู้ยืม</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s1_r2_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s1_r2_date}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Section 2 Header -->
              <div style="border-left: 6px solid #0288d1; padding-left: 12px; margin-bottom: 12px; margin-top: 30px;">
                <h3 style="margin: 0; color: #0288d1; font-size: 1.15em; font-weight: bold;">💳 2. ขั้นตอนการส่งแบบเบิกเงินกู้ยืม ภาคเรียนที่ 1/2569</h3>
              </div>

              <!-- Section 2 Table Card -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025); overflow: hidden; margin-bottom: 25px;">
                <table style="width: 100%; border-collapse: collapse; margin: 0; font-size: 0.95em;">
                  <thead>
                    <tr style="background-color: #0288d1; color: #ffffff;">
                      <th style="padding: 14px 16px; font-weight: bold; text-align: left; border-bottom: 1px solid #0288d1; width: 35%;">ขั้นตอนการดำเนินงาน</th>
                      <th style="padding: 14px 16px; font-weight: bold; text-align: left; border-bottom: 1px solid #0288d1; width: 45%;">รายละเอียดข้อมูล</th>
                      <th style="padding: 14px 16px; font-weight: bold; text-align: center; border-bottom: 1px solid #0288d1; width: 20%;">วันที่สถานศึกษาแจ้ง</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style="border-bottom: 1px solid #edf2f7; background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">1. งาน กยศ.ม.บูรพา ลงรับเอกสาร</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s2_r1_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s2_r1_date}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #edf2f7; background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">2. เตรียมนำส่งธนาคาร</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s2_r2_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s2_r2_date}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #edf2f7; background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">3. นำส่งธนาคาร</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s2_r3_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s2_r3_date}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #edf2f7; background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">4. ติดตามชุดนำส่งธนาคาร</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s2_r4_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s2_r4_date}</td>
                    </tr>
                    <tr style="background-color: #ffffff;">
                      <td style="padding: 14px 16px; font-weight: bold; color: #2d3748; vertical-align: top;">5. ธนาคารตรวจเอกสารเรียบร้อย</td>
                      <td style="padding: 14px 16px; color: #2d3748; vertical-align: top; line-height: 1.5;">{s2_r5_status}</td>
                      <td style="padding: 14px 16px; color: #4a5568; text-align: center; vertical-align: top;">{s2_r5_date}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Button to Dashboard -->
              <p style="text-align: center; margin: 30px 0 15px 0;">
                <a href="{dashboard_url}" target="_blank" style="background-color: #0056b3; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                  เข้าดูหน้า Looker Studio Dashboard
                </a>
              </p>
              
            </div>
          </body>
        </html>
        """

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = Header(subject, 'utf-8')
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.sendmail(self.config.sender_email, receiver_email, msg.as_string())
                
            logger.info(f"Successfully sent notification email to {receiver_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch email to {receiver_email}: {e}")
            return False
