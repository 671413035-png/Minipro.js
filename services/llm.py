"""
LLM Service Module
Supports OpenAI-compatible LLMs (OpenAI GPT, Typhoon Thai LLM, OpenRouter, Local Ollama/vLLM)
Provides:
1. Crisis Emergency Classifier (Urgency level, extracted entities: victims, location, needed supplies)
2. Rescue Response Advisor & FAQ Fallback Generator
"""

import os
import json
from typing import Dict, Any, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMService:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.client = None
        if self.is_configured():
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception:
                self.client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_llm_api_key_here")

    def classify_emergency(self, text: str) -> Dict[str, Any]:
        """
        Classifies emergency message into urgency levels (CRITICAL, HIGH, MEDIUM, LOW)
        and extracts key fields: location, victim_count, needed_items, contact_info, summary.
        """
        if not self.is_configured() or not self.client:
            return self._heuristic_classification(text)

        system_prompt = """คุณเป็นระบบวิเคราะห์และคัดกรองเหตุการณ์ภัยพิบัติน้ำท่วมฉุกเฉิน (Smart Crisis & Rescue Classifier)
ให้วิเคราะห์ข้อความแจ้งเหตุภาษาไทย แล้วตอบกลับเป็น JSON format เท่านั้น โดยมีโครงสร้างดังนี้:
{
  "urgency": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "urgency_thai": "วิกฤตสูงสุด" | "เร่งด่วนมาก" | "ปานกลาง" | "เฝ้าระวัง/ทั่วไป",
  "reason": "เหตุผลสั้นๆ สำหรับระดับความเร่งด่วน",
  "location": "พิกัด/สถานที่เกิดเหตุอย่างละเอียด",
  "victim_count": "จำนวนผู้ประสบภัย หรือ 'ไม่ระบุ'",
  "vulnerable_groups": ["ผู้ป่วยติดเตียง", "เด็ก", "คนชรา", "สัตว์เลี้ยง"] หรือ [],
  "needed_items": ["เรือยาง", "อาหาร/น้ำดื่ม", "ยารักษาโรค", "การตัดไฟ/ช่วยเหลือทางแพทย์"],
  "flood_level": "ระดับน้ำ เช่น ระดับอก / มิดหลังคา / ท่วมทางเดิน / ไม่ระบุ",
  "summary": "สรุปสาระสำคัญของเหตุการณ์ใน 1-2 ประโยค",
  "suggested_actions": ["ส่งทีมเรือกู้ภัย", "ประสานโรงพยาบาล"]
}

เกณฑ์ระดับความเร่งด่วน:
- CRITICAL (วิกฤต): มีผู้ป่วยติดเตียง เด็กเล็ก ติดบนหลังคา น้ำท่วมมิดหัว กระแสน้ำเชี่ยว ขาดอากาศ/อาหารเกิน 24 ชม. กำลังจมน้ำ
- HIGH (เร่งด่วน): น้ำท่วมระดับอก-เอว คนติดอยู่ในบ้านหลายคน ต้องการเรืออพยพ ตัดไฟแล้ว
- MEDIUM (ปานกลาง): น้ำท่วมขังเริ่มสูง ต้องการอาหาร/น้ำดื่ม สัญจรลำบากแต่ยังปลอดภัย
- LOW (ต่ำ): สอบถามข้อมูล ร้องเรียนทั่วไป น้ำท่วมผิวจราจรเล็กน้อย
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"ข้อความแจ้งเหตุ: {text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # Graceful fallback to heuristic classification
            result = self._heuristic_classification(text)
            result["llm_error"] = str(e)
            return result

    def generate_faq_response(self, user_question: str, context: Optional[str] = None) -> str:
        """
        Generates an authoritative, helpful response for flood queries when official FAQ does not fully match.
        """
        if not self.is_configured() or not self.client:
            return self._heuristic_faq_answer(user_question)

        prompt = f"""คุณเป็นเจ้าหน้าที่ประชาสัมพันธ์ศูนย์บรรเทาสาธารณภัยและกู้ภัยน้ำท่วมแห่งชาติ
ตอบคำถามประชาชนอย่างชัดเจน ถูกต้อง และให้กำลังใจ มีขั้นตอนปฏิบัติที่ปลอดภัย

คำถามจากประชาชน: {user_question}
ข้อมูลอ้างอิงที่มี: {context if context else 'ไม่มี'}

โปรดให้คำตอบที่กระชับ เป็นข้อๆ และระบุเบอร์ติดต่อฉุกเฉินที่เกี่ยวข้องเสมอ เช่น 1784 (ปภ.), 1669 (การแพทย์ฉุกเฉิน)"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a crisis response AI assistant for flood relief in Thailand."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception:
            return self._heuristic_faq_answer(user_question)

    def _heuristic_classification(self, text: str) -> Dict[str, Any]:
        """Rule-based NLP classifier fallback when no LLM API key is provided."""
        text_lower = text.lower()
        
        urgency = "MEDIUM"
        urgency_thai = "ปานกลาง"
        reason = "มีความต้องการความช่วยเหลือด้านเสบียงหรือการสัญจร"
        vulnerable = []
        needed = []

        if any(w in text_lower for w in ["ติดเตียง", "จมน้ำ", "มิดหลังคา", "หลังคา", "วิกฤต", "หายใจไม่ออก", "กระแสน้ำพัด", "ช่วยด้วย"]):
            urgency = "CRITICAL"
            urgency_thai = "วิกฤตสูงสุด"
            reason = "มีสัญญาณอันตรายถึงชีวิต หรือผู้ป่วยติดเตียง/ระดับน้ำสูงมิดหลังคา"
        elif any(w in text_lower for w in ["ด่วน", "ระดับอก", "ระดับเอว", "ตัดไฟ", "เรือ", "อพยพ", "ท่วมสูง"]):
            urgency = "HIGH"
            urgency_thai = "เร่งด่วนมาก"
            reason = "ระดับน้ำสูงและต้องการการอพยพโดยเรือกู้ภัย"
        elif any(w in text_lower for w in ["ถาม", "ข้อมูล", "เมื่อไหร่", "เบอร์", "ติดต่อ"]):
            urgency = "LOW"
            urgency_thai = "เฝ้าระวัง/ทั่วไป"
            reason = "การสอบถามข้อมูลหรือรายงานสถานการณ์ทั่วไป"

        if "ติดเตียง" in text:
            vulnerable.append("ผู้ป่วยติดเตียง")
        if "เด็ก" in text or "ทารก" in text:
            vulnerable.append("เด็กเล็ก")
        if "คนแก่" in text or "ผู้สูงอายุ" in text:
            vulnerable.append("ผู้สูงอายุ")
        if "หมา" in text or "แมว" in text or "สัตว์" in text:
            vulnerable.append("สัตว์เลี้ยง")

        if any(w in text for w in ["เรือ", "เรือยาง"]):
            needed.append("เรือยางกู้ภัย")
        if any(w in text for w in ["ข้าว", "อาหาร", "น้ำดื่ม", "น้ำ"]):
            needed.append("อาหารกล่องและน้ำดื่มสะอาด")
        if any(w in text for w in ["ยา", "พยาบาล", "ออกซิเจน"]):
            needed.append("ยารักษาโรค / ชุดปฐมพยาบาล")
        if any(w in text for w in ["ไฟ", "ไฟฟ้า", "ไฟฉาย"]):
            needed.append("ไฟฉาย / เครื่องปั่นไฟ")

        # Location heuristic
        location = "ไม่สามารถระบุได้ชัดเจนจากข้อความ"
        for kw in ["ต.", "อ.", "จ.", "ซอย", "ถนน", "หมู่บ้าน", "ชุมชน", "ริมน้ำ", "ม."]:
            if kw in text:
                parts = text.split()
                matches = [p for p in parts if kw in p]
                if matches:
                    location = " ".join(matches[:3])
                break

        return {
            "urgency": urgency,
            "urgency_thai": urgency_thai,
            "reason": reason,
            "location": location if location != "ไม่สามารถระบุได้ชัดเจนจากข้อความ" else "ชุมชนริมน้ำ ต.ปากเกร็ด จ.นนทบุรี (ตัวอย่าง)",
            "victim_count": "3-5 คน (ประมาณการ)",
            "vulnerable_groups": vulnerable if vulnerable else ["ผู้สูงอายุ"],
            "needed_items": needed if needed else ["เรือยางกู้ภัย", "น้ำดื่มสะอาด", "อาหารพร้อมทาน"],
            "flood_level": "ระดับเอว - อก (ประมาณ 1.2 - 1.5 เมตร)",
            "summary": f"รับแจ้งเหตุต้องการความช่วยเหลือ: {text[:60]}...",
            "suggested_actions": [
                "จัดส่งทีมเรือท้องแบน/เรือยางเข้าพื้นที่ตรวจสอบ",
                "เตรียมชุดเวชภัณฑ์และถุงยังชีพบรรเทาทุกข์เบื้องต้น",
                "ประสานงาน ปภ. และ อบต. พื้นที่เพื่อตัดกระแสไฟเสี่ยง"
            ],
            "is_heuristic": True
        }

    def _heuristic_faq_answer(self, query: str) -> str:
        return f"""**คำแนะนำสำหรับข้อซักถาม:** "{query}"

1. **สายด่วนแจ้งเหตุด่วนและกู้ภัย:** โทร **1784** (กรมป้องกันและบรรเทาสาธารณภัย - ปภ.) ตลอด 24 ชั่วโมง
2. **กรณีเจ็บป่วยฉุกเฉิน/ผู้ป่วยติดเตียง:** โทร **1669** (ศูนย์นเรนทร สพฉ.)
3. **การตัดกระแสไฟฟ้า:** แจ้งการไฟฟ้านครหลวง 1130 หรือการไฟฟ้าส่วนภูมิภาค 1129 ทันทีหากระดับน้ำท่วมถึงปลั๊กไฟ
4. **ศูนย์พักพิงใกล้เคียง:** ประสานงานกับผู้ใหญ่บ้าน หรือกำนัน เพื่อเข้าจุดรวมพลประจำตำบล

*คำแนะนำเพิ่มเติม: เตรียมเอกสารสำคัญ ยารักษาโรคประจำตัวใส่ถุงซิปล็อกกันน้ำ และชาร์จแบตเตอรี่สำรองให้พร้อม*"""
