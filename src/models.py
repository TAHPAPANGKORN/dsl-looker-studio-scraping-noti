from typing import Dict

# Thai translation names map for all dashboard fields
FIELD_NAMES_TH: Dict[str, str] = {
    "borrower_type": "ประเภทผู้กู้",
    "new_borrower_info": "ข้อมูลสำหรับผู้กู้รายใหม่",
    "doc_seq_to_officer": "หมายเลขลำดับเอกสารแจ้งเจ้าหน้าที่",
    
    # Section 1: ขั้นตอนการทำงานเอกสารคำขอเสนอขอกู้ยืม
    "app_doc_intake_status": "สถานะการลงรับเอกสารคำขอ",
    "app_doc_intake_date": "วันที่ลงรับเอกสารคำขอ",
    "app_doc_correct_docs": "เอกสารที่ต้องแก้ไข (คำขอ)",
    "app_doc_correct_officer": "แจ้งเลขแก้ไขกับเจ้าหน้าที่ (คำขอ)",
    "app_doc_correct_date": "วันที่อัปเดตการแก้ไข (คำขอ)",
    "app_doc_corrections_list": "รายการแจ้งแก้ไข 1 (คำขอ)",
    "app_doc_corrections_list_2": "รายการแจ้งแก้ไข 2 (คำขอ)",
    "loan_doc_status": "สถานะเอกสารประกอบคำขอกู้ยืม",
    "loan_doc_date": "วันที่ตรวจสอบเอกสารประกอบคำขอ",

    # Section 2: ขั้นตอนการส่งแบบเบิกเงินกู้ยืม
    "step_1_status": "สถานะลงรับแบบเบิกเงิน",
    "step_1_date": "วันที่ลงรับแบบเบิกเงิน",
    "step_1_correct_docs": "เอกสารที่ต้องแก้ไข (แบบเบิกเงิน)",
    "step_1_correct_officer": "แจ้งเลขแก้ไขกับเจ้าหน้าที่ (แบบเบิกเงิน)",
    "step_1_correct_date": "วันที่อัปเดตการแก้ไข (แบบเบิกเงิน)",
    "step_1_corrections_list": "รายการแจ้งแก้ไข 1 (แบบเบิกเงิน)",
    "step_1_corrections_list_2": "รายการแจ้งแก้ไข 2 (แบบเบิกเงิน)",
    
    "step_2_status": "สถานะการเตรียมนำส่งธนาคาร",
    "step_2_date": "วันที่เตรียมนำส่งธนาคาร",
    "step_2_correct_before": "แจ้งแก้ไขก่อนนำส่งธนาคาร",
    "step_2_correct_docs": "เอกสารแก้ไขก่อนนำส่ง",
    "step_2_correct_date": "วันที่อัปเดตการแก้ไขก่อนนำส่ง",
    "step_2_disburse_num": "เลขที่แบบเบิกเงิน",
    
    "step_3_status": "สถานะการนำส่งธนาคาร",
    "step_3_date": "วันที่นำส่งธนาคาร",
    "step_3_delivery_num": "เลขที่ใบนำส่งธนาคาร",
    "step_3_delivery_date": "วันที่อัปเดตเลขที่ใบนำส่ง",
    "step_3_corrected_bank": "สถานะแก้ไขเพิ่มเติมหลังส่งธนาคาร",
    
    "step_4_status": "สถานะติดตามชุดนำส่งธนาคาร",
    "step_4_date": "วันที่ติดตามชุดนำส่งธนาคาร",
    "step_4_correct_docs": "เอกสารที่ต้องแก้ไข (ขั้นตอนติดตาม)",
    "step_4_disburse_num": "เลขที่แบบเบิกเงิน (ขั้นตอนติดตาม)",
    "step_4_bank_audit_err": "ธนาคารตรวจเอกสารแล้วพบข้อบกพร่อง",
    "step_4_officer_seq": "หมายเลขลำดับเอกสารติดตามแจ้งเจ้าหน้าที่",
    "step_4_officer_date": "วันที่อัปเดตการแจ้งเจ้าหน้าที่ (ติดตาม)",
    "step_4_corrected_bank": "สถานะแก้ไขชุดนำส่งที่ธนาคารตีกลับ",
    "step_4_corrected_date": "วันที่อัปเดตการแก้ไขชุดนำส่ง",
    
    "step_5_status": "สถานะธนาคารตรวจเอกสารเรียบร้อย",
    "step_5_date": "วันที่ธนาคารตรวจเรียบร้อย",
}

# Coordinate-mapped HTML component class mappings in Looker Studio
CLASS_FIELD_MAP: Dict[str, str] = {
    # ข้อมูลประจำตัวนิสิต (Student Profile)
    "cd-gboblwqazd": "student_name",          # ชื่อ - สกุล
    "cd-zu0nbxqazd": "student_id",            # รหัสนิสิต
    "cd-g7s354421d": "borrower_type",         # ประเภทผู้กู้
    "cd-rajav08x2d": "new_borrower_info",     # ข้อมูลสำหรับผู้กู้รายใหม่
    "cd-l2jav08x2d": "doc_seq_to_officer",    # แจ้งหมายเลขลำดับเอกสารกับเจ้าหน้าที่

    # ขั้นตอนการส่งรายการเอกสารประกอบคำขอกู้ยืม (Application Document Stage)
    "cd-mbxef90urd": "app_doc_intake_status",  # ลงรับเอกสารประกอบคำขอ
    "cd-dqq836b31d": "app_doc_intake_date",    # วันที่ลงรับเอกสารประกอบคำขอ
    "cd-rbxef90urd": "app_doc_correct_docs",     # เอกสารที่ต้องแก้ไข (คำขอ)
    "cd-p3xef90urd": "app_doc_correct_officer",  # แจ้งเลขแก้ไขกับเจ้าหน้าที่ (คำขอ)
    "cd-m2uor8a5sd": "app_doc_correct_date",     # วันที่อัปเดตการแก้ไข (คำขอ)
    "cd-v3cv0xawrd": "app_doc_corrections_list",  # รายการแจ้งแก้ไข 1 (คำขอ)
    "cd-2vyef90urd": "app_doc_corrections_list_2",# รายการแจ้งแก้ไข 2 (คำขอ)
    "cd-6ctixl5urd": "loan_doc_status",        # ตรวจเอกสารประกอบคำขอ (สถานะเอกสารประกอบคำขอกู้ยืม)
    "cd-9uk46sx4rd": "loan_doc_date",          # วันที่ตรวจสอบเอกสารประกอบคำขอ

    # ลำดับ 1: งาน กยศ.ม.บูรพา ลงรับเอกสารของนิสิต (Step 1)
    "cd-0bg3vfspgd": "step_1_status",          # สถานะการลงรับเอกสาร
    "cd-xa17hak2rd": "step_1_date",            # วันที่สถานศึกษาแจ้งข้อมูล
    "cd-nh1wqvcsnd": "step_1_correct_docs",    # แก้ไขเอกสาร (ตรวจครั้งที่ 1)
    "cd-gbq3h2uuod": "step_1_correct_date",    # วันที่สถานศึกษาแจ้งข้อมูล (แก้ไขครั้งที่ 1)
    "cd-ui6240itnd": "step_1_correct_officer", # แจ้งเลขแก้ไขกับเจ้าหน้าที่
    "cd-07r0fai2td": "step_1_corrections_list",# รายการแก้ไข 1-3 หรือ 1-8
    "cd-jblan3itnd": "step_1_corrections_list_2", # รายการแจ้งแก้ไข 2 (แบบเบิกเงิน)

    # ลำดับ 2: สถานะเอกสารเตรียมนำส่งธนาคาร (Step 2)
    "cd-8j9vjsdsnd": "step_2_status",          # สถานะเตรียมนำส่ง
    "cd-2awi8ck2rd": "step_2_date",            # วันที่สถานศึกษาแจ้งข้อมูล
    "cd-jgmvjimtnd": "step_2_correct_before",  # แจ้งแก้ไขก่อนนำส่งธนาคาร
    "cd-f12xr16nod": "step_2_correct_docs",    # แก้ไขเอกสาร
    "cd-0z4hoy42yd": "step_2_correct_date",    # วันที่สถานศึกษาแจ้งข้อมูล (แก้ไขก่อนนำส่ง)
    "cd-33popojtnd": "step_2_disburse_num",    # เลขที่แบบเบิกเงิน

    # ลำดับ 3: สถานะเอกสารนำส่งธนาคาร (Step 3)
    "cd-mzhpya5ipd": "step_3_status",          # สถานะนำส่งธนาคาร
    "cd-e7qjng1zwd": "step_3_date",            # วันที่สถานศึกษาแจ้งข้อมูล
    "cd-tripya5ipd": "step_3_delivery_num",    # เลขที่ใบนำส่งธนาคาร
    "cd-e1il2e9yrd": "step_3_delivery_date",   # วันที่สถานศึกษาแจ้งข้อมูล (เลขที่ใบนำส่ง)
    "cd-ezhpya5ipd": "step_3_corrected_bank",  # สถานะเอกสารนำส่งธนาคาร (ที่มีการแก้ไขจากธนาคาร)

    # ลำดับ 4: สถานะเอกสารติดตามชุดนำส่งธนาคาร (Step 4)
    "cd-i7gpya5ipd": "step_4_status",          # สถานะติดตามชุดนำส่ง
    "cd-oripya5ipd": "step_4_date",            # วันที่สถานศึกษาแจ้งข้อมูล
    "cd-f7gpya5ipd": "step_4_correct_docs",    # แก้ไขเอกสาร
    "cd-tjgstmi2td": "step_4_disburse_num",    # เลขที่แบบเบิกเงิน
    "cd-0pp4vy421d": "step_4_bank_audit_err",  # ธนาคารตรวจเอกสารแล้ว มีเอกสารต้องแก้ไข
    "cd-uev0k0421d": "step_4_officer_seq",     # แจ้งหมายเลขลำดับเอกสารกับเจ้าหน้าที่
    "cd-98wr61421d": "step_4_officer_date",    # วันที่สถานศึกษาแจ้งข้อมูล (แจ้งหมายเลขลำดับ)
    "cd-ginj1z421d": "step_4_corrected_bank",  # สถานะเอกสารติดตามชุดนำส่งธนาคาร (ที่มีการแก้ไขจากธนาคาร)
    "cd-ye4f21421d": "step_4_corrected_date",  # วันที่สถานศึกษาแจ้งข้อมูล (ติดตามชุดนำส่งแก้ไข)

    # ลำดับ 5: ธนาคารตรวจเอกสารเรียบร้อย (Step 5)
    "cd-bfgpya5ipd": "step_5_status",          # ธนาคารตรวจเอกสารเรียบร้อย
    "cd-dfgpya5ipd": "step_5_date",            # วันที่สถานศึกษาแจ้งข้อมูล
}
