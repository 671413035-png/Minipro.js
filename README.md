# 🌊 Smart Flood Crisis & Rescue Platform
ระบบศูนย์บัญชาการวิกฤติน้ำท่วมและกู้ภัยอัจฉริยะ พัฒนาด้วย **Streamlit**, **AIForThai APIs**, และ **ThaiLLM / OpenAI-compatible LLM**

---

## 🌟 จุดเด่นและสถาปัตยกรรมการทำงาน (Service Architecture)

ระบบประกอบไปด้วย 4 บริการหลักในการจัดการภัยพิบัติแบบบูรณาการ:

### 1. 🚨 Service 1: TAG (Main Crisis Dashboard & Emergency Rescue Classifier)
- **Multi-modal Input**: รองรับการแจ้งเหตุผ่าน 3 ช่องทาง
  - พิมพ์ข้อความแจ้งเหตุ (Direct Text Input)
  - อัปโหลดภาพถ่าย/สกรีนช็อตข้อความโพสต์ขอความช่วยเหลือ (**AIForThai OCR**)
  - อัปโหลดไฟล์เสียงขอความช่วยเหลือสด (**AIForThai Speech to Text - Partii STT**)
- **AI Classification & Extraction (LLM)**:
  - จำแนกระดับความเร่งด่วน: `CRITICAL` (วิกฤตสูงสุด), `HIGH` (เร่งด่วนมาก), `MEDIUM` (ปานกลาง), `LOW` (เฝ้าระวัง/ทั่วไป)
  - สกัดข้อมูลสำคัญ: พิกัดสถานที่, จำนวนผู้ประสบภัย, กลุ่มเปราะบาง (ผู้ป่วยติดเตียง/เด็ก/คนชรา), สิ่งของที่ต้องการด่วน (เรือยาง, เสบียง, ออกซิเจน)
  - มีระบบ **Dispatch Queue** เพื่อส่งต่อข้อมูลไปยังทีมกู้ภัยภาคสนาม

### 2. 📊 Service 2: EmoNews (Flood News & Social Sentiment Monitoring)
- เชื่อมต่อ **AIForThai EmoNews API** เพื่อติดตามข่าวสารและกระแสบนโซเชียลมีเดียเกี่ยวกับน้ำท่วม
- ตรวจจับ **Panic Index (ดัชนีความตื่นตระหนก)** และความรู้สึกของสังคม (Fear, Anger, Sadness, Hope, Joy)
- กราฟสรุปสัดส่วนอารมณ์เพื่อใช้วางแผนการสื่อสารวิกฤต (Crisis Communication)

### 3. 🎙️ Service 3: VAJAX (Voice & Audio Processing / Direct Voice Assistant)
- **Speech to Text (STT)**: แปลงเสียงวิทยุสื่อสารหรือโทรศัพท์สายด่วนเป็นข้อความภาษาไทย
- **Text to Speech (Vaja TTS)**: แปลงข้อความประกาศเตือนภัยฉุกเฉินเป็นไฟล์เสียงภาษาไทยสังเคราะห์ สำหรับระบบกระจายเสียงตามสายหรือสถานีวิทยุชุมชน

### 4. ❓ Service 4: FAQ Question Search (Flood Info & Assistance Search)
- ค้นหาคำตอบจากฐานข้อมูลทางการด้วย **AIForThai FAQ Search API**
- มีระบบ **ThaiLLM Fallback Generator** อัจฉริยะ ตอบคำถามเฉพาะบุคคลและแนะนำเบอร์ติดต่อฉุกเฉิน (เช่น ปภ. 1784, การแพทย์ฉุกเฉิน 1669)

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```
C:/Miniproj/
├── app.py                     # เมนแดชบอร์ด Streamlit ครบทั้ง 4 บริการ
├── services/
│   ├── aiforthai.py           # ตัวครอบ API สำหรับ AIForThai (OCR, STT, TTS, EmoNews, FAQ)
│   └── llm.py                 # ตัววิเคราะห์และจำแนกข้อมูลด้วย LLM / Heuristic Fallback
├── data/
│   └── sample_test_data/      # ข้อมูลตัวอย่างสำหรับทดสอบระบบ
│       └── sample_emergencies.json
├── requirements.txt           # รายการแพ็กเกจ Python ที่จำเป็น
├── .env.example               # ตัวอย่างไฟล์ตั้งค่า API Key
├── .env                       # ไฟล์ตั้งค่า API Key ของผู้ใช้ (ไม่ถูก commit)
└── README.md                  # เอกสารคู่มือการติดตั้งและการใช้งาน
```

---

## 🚀 วิธีการติดตั้งและการเริ่มใช้งาน (Quickstart)

### 1. ติดตั้งไลบรารีที่จำเป็น
เปิด Terminal / PowerShell แล้วรันคำสั่ง:
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key (ตัวเลือก)
คัดลอกไฟล์ `.env.example` เป็น `.env`:
```bash
cp .env.example .env
```
แล้วแก้ไขข้อมูลใน `.env` ตามต้องการ:
- `AIFORTHAI_API_KEY`: ขอรับฟรีได้ที่ [https://aiforthai.in.th/](https://aiforthai.in.th/)
- `LLM_API_KEY`: คีย์สำหรับโมเดล OpenAI หรือ Typhoon (OpenAI-compatible)

*(หมายเหตุ: หากยังไม่มี API Key ระบบจะมี **Smart Mock & Heuristic NLP Engine** สำรองให้ทันที สามารถทดสอบการทำงานของ UI ได้อย่างสมบูรณ์แบบโดยไม่ต้องรอคีย์)*

### 3. รันโปรแกรม Streamlit
```bash
streamlit run app.py
```
เปิดบราวเซอร์ไปที่: `http://localhost:8501`

---

## 🧪 การทดสอบระบบด้วยข้อมูลตัวอย่าง (Sample Test Data)
- ภายในแอปพลิเคชัน มีปุ่มเลือก Preset ข้อความแจ้งเหตุกรณีวิกฤต, กรณีเร่งด่วน และกรณีทั่วไป ให้ทดสอบได้ทันทีใน Tab 1
- สามารถดูตัวอย่างข้อมูล JSON เพิ่มเติมได้ที่ [sample_emergencies.json](file:///C:/Miniproj/data/sample_test_data/sample_emergencies.json)
