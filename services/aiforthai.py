"""
AIForThai API Client Wrapper
Provides integration with AIForThai services:
- OCR (Optical Character Recognition)
- STT (Partii Speech to Text / VajaX STT)
- TTS (Vaja Text-to-Speech)
- EmoNews (Social media sentiment & emotional news analysis)
- FAQ Question Search (Semantic similarity / retrieval)

Fallback mock modes are supported to guarantee full functionality during demos and offline testing.
"""

import os
import requests
import json
from typing import Dict, Any, Optional

class AIForThaiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AIFORTHAI_API_KEY", "")
        self.base_headers = {
            "Apikey": self.api_key
        } if self.api_key else {}

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_aiforthai_api_key_here")

    def ocr_image(self, file_bytes: bytes, filename: str = "image.jpg") -> Dict[str, Any]:
        """
        AIForThai OCR API (e.g. ocr / th-ocr)
        Extracts Thai/English text from uploaded rescue request screenshots or photos.
        """
        if not self.is_configured():
            return {
                "success": True,
                "text": "ขอความช่วยเหลือด่วน! น้ำท่วมมิดหลังคา ซอยวัดกู้ ต.บางพูด อ.ปากเกร็ด จ.นนทบุรี ติดอยู่ 4 คน มีคนแก่ติดเตียง 1 คน และเด็ก 1 คน ขาดน้ำดื่มและอาหารด่วนมาก",
                "is_mock": True
            }

        url = "https://api.aiforthai.in.th/p-ocr"
        headers = {"Apikey": self.api_key}
        files = {"file": (filename, file_bytes, "image/jpeg")}

        try:
            response = requests.post(url, headers=headers, files=files, timeout=25)
            if response.status_code == 200:
                data = response.json()
                # Depending on actual API payload schema
                extracted_text = data.get("text") or data.get("result") or str(data)
                return {"success": True, "text": extracted_text, "is_mock": False, "raw": data}
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}",
                    "text": "ขอความช่วยเหลือด่วน น้ำท่วมสูง ม.4 ต.เวียง อ.ฝาง จ.เชียงใหม่ มีผู้สูงอายุ 2 ราย ขอยารักษาโรค",
                    "is_mock": True
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "ขอความช่วยเหลือด่วน ติดอยู่บนชั้น 2 ซอยรามคำแหง น้ำระดับอก ไฟฟ้าถูกตัด ต้องการเรืออพยพ 3 คน",
                "is_mock": True
            }

    def speech_to_text(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """
        AIForThai STT (Partii Speech to Text)
        Transcribes Thai voice distress calls.
        """
        if not self.is_configured():
            return {
                "success": True,
                "text": "ฮัลโหล ขอความช่วยเหลือหน่อยครับ น้ำเอ่อล้นตลิ่งเข้าท่วมบ้านแล้ว อยู่ชุมชนริมน้ำวัดเทวราชกุญชร ดุสิต ตอนนี้ระดับน้ำสูงถึงเอว มีผู้ป่วยติดเตียงต้องการเรือพาไปโรงพยาบาลครับ",
                "is_mock": True
            }

        url = "https://api.aiforthai.in.th/partii-web-api"
        headers = {"Apikey": self.api_key}
        files = {"wavfile": (filename, audio_bytes, "audio/wav")}

        try:
            response = requests.post(url, headers=headers, files=files, timeout=30)
            if response.status_code == 200:
                data = response.json()
                transcript = data.get("result") or data.get("text") or str(data)
                return {"success": True, "text": transcript, "is_mock": False, "raw": data}
            else:
                return {
                    "success": False,
                    "error": f"STT API returned {response.status_code}",
                    "text": "แจ้งเหตุด่วนครับ ตอนนี้น้ำป่าไหลหลากเข้าท่วมหมู่บ้านแม่สาย มีคนติดอยู่ 5 คน ต้องการเรือยางและอาหารกล่องด่วน",
                    "is_mock": True
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "ขอความช่วยเหลือด่วนครับ น้ำท่วมสูงระดับเอว ถนนขาด สัญจรไม่ได้ ต้องการน้ำดื่มและไฟฉาย",
                "is_mock": True
            }

    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        AIForThai Vaja TTS API
        Synthesizes Thai speech for crisis response or radio broadcast.
        """
        if not self.is_configured():
            return {
                "success": True,
                "audio_url": None,
                "message": "โหมดจำลองเสียง (TTS Mock Mode): บันทึกข้อความเสียงสำเร็จ",
                "is_mock": True
            }

        url = f"https://api.aiforthai.in.th/vaja"
        headers = {"Apikey": self.api_key, "Content-Type": "application/x-www-form-urlencoded"}
        data = {"text": text, "mode": "say"}

        try:
            response = requests.post(url, headers=headers, data=data, timeout=20)
            if response.status_code == 200:
                res_data = response.json()
                wav_url = res_data.get("wav_url")
                return {"success": True, "audio_url": wav_url, "is_mock": False, "raw": res_data}
            else:
                return {"success": False, "error": f"TTS Status {response.status_code}", "is_mock": True}
        except Exception as e:
            return {"success": False, "error": str(e), "is_mock": True}

    def get_emonews(self, keyword: str = "น้ำท่วม", limit: int = 10) -> Dict[str, Any]:
        """
        AIForThai EmoNews API
        Analyzes news sentiment, emotion (fear, sadness, anger, joy), and trend regarding floods.
        """
        if not self.is_configured():
            # Comprehensive realistic simulated data for crisis monitoring
            mock_news = [
                {
                    "title": "ด่วน! น้ำยมทะลักท่วมเทศบาลเมืองสุโขทัย ชาวบ้านเร่งขนของหนีน้ำกลางดึก",
                    "source": "ThaiPBS / Social Monitor",
                    "sentiment": "Negative",
                    "emotion": "Panic / Fear",
                    "panic_score": 88,
                    "date": "2026-10-04 18:30",
                    "sentiment_breakdown": {"fear": 65, "sadness": 20, "anger": 10, "neutral": 5}
                },
                {
                    "title": "เขื่อนเจ้าพระยาปรับเพิ่มการระบายน้ำ เตือน 11 จังหวัดท้ายเขื่อนรับมือน้ำล้นตลิ่ง",
                    "source": "กรมชลประทาน",
                    "sentiment": "Negative",
                    "emotion": "Alert / Fear",
                    "panic_score": 75,
                    "date": "2026-10-04 16:15",
                    "sentiment_breakdown": {"fear": 55, "sadness": 15, "anger": 15, "neutral": 15}
                },
                {
                    "title": "กู้ภัยและทหารเข้าช่วยเหลืออพยพผู้สูงอายุติดเตียง 15 ราย พื้นที่ อ.สารภี ปลอดภัยทุกคน",
                    "source": "จิตอาสาพระราชทาน",
                    "sentiment": "Positive",
                    "emotion": "Relief / Hope",
                    "panic_score": 25,
                    "date": "2026-10-04 14:00",
                    "sentiment_breakdown": {"fear": 10, "sadness": 10, "joy": 70, "neutral": 10}
                },
                {
                    "title": "ชาวบ้านร้องเรียนน้ำท่วมขังวันที่ 4 ยังไร้หน่วยงานแจกถุงยังชีพ วอนส่งเรือเข้าช่วย",
                    "source": "X (Twitter) Trending",
                    "sentiment": "Negative",
                    "emotion": "Anger / Frustration",
                    "panic_score": 82,
                    "date": "2026-10-04 12:45",
                    "sentiment_breakdown": {"fear": 30, "sadness": 25, "anger": 40, "neutral": 5}
                },
                {
                    "title": "เทศบาลเปิดศูนย์พักพิงชั่วคราว 3 จุด พร้อมจัดเตรียมโรงครัวพระราชทาน 3 มื้อ",
                    "source": "สำนักงานประชาสัมพันธ์จังหวัด",
                    "sentiment": "Positive",
                    "emotion": "Hope / Gratitude",
                    "panic_score": 20,
                    "date": "2026-10-04 11:10",
                    "sentiment_breakdown": {"fear": 5, "sadness": 5, "joy": 80, "neutral": 10}
                },
                {
                    "title": "ระดับน้ำแม่น้ำปิงเริ่มทรงตัว คาดว่าหากฝนไม่ตกซ้ำจะลดลงสู่ระดับปกติภายใน 48 ชม.",
                    "source": "ศูนย์เตือนภัยพิบัติแห่งชาติ",
                    "sentiment": "Neutral / Positive",
                    "emotion": "Relief",
                    "panic_score": 35,
                    "date": "2026-10-04 09:20",
                    "sentiment_breakdown": {"fear": 20, "sadness": 10, "joy": 45, "neutral": 25}
                }
            ]
            return {
                "success": True,
                "keyword": keyword,
                "data": mock_news[:limit],
                "avg_panic_index": 54.2,
                "overall_sentiment": "Negative / Moderate Panic",
                "is_mock": True
            }

        url = "https://api.aiforthai.in.th/emonews"
        headers = {"Apikey": self.api_key}
        params = {"text": keyword, "num": limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "keyword": keyword, "data": data, "is_mock": False}
            else:
                return self.get_emonews(keyword, limit) # fallback to mock with indicator
        except Exception:
            return self.get_emonews(keyword, limit)

    def search_faq(self, query: str) -> Dict[str, Any]:
        """
        AIForThai FAQ Question Search API
        Finds the closest official flood crisis FAQ match.
        """
        predefined_faqs = [
            {
                "question": "หากน้ำท่วมฉุกเฉินระดับสูงต้องการเรือกู้ภัย ติดต่อเบอร์ใด?",
                "answer": "โทรสายด่วน ปภ. 1784 (ตลอด 24 ชม.), สายด่วนตำรวจตระเวนชายแดน 1155, หรือศูนย์ประสานงานร่วมกู้ภัยสว่างบริบูรณ์ 1669",
                "category": "สายด่วนฉุกเฉิน"
            },
            {
                "question": "ศูนย์พักพิงชั่วคราวหลักและการลงทะเบียนรับความช่วยเหลืออยู่ที่ไหน?",
                "answer": "ศูนย์พักพิงหลักอยู่ที่อาคารอเนกประสงค์เทศบาล, โรงเรียนประจำอำเภอ และหอประชุมประจำจังหวัด สามารถนำบัตรประชาชนมาลงทะเบียนรับเต็นท์และอาหารได้ทันที",
                "category": "ศูนย์พักพิง"
            },
            {
                "question": "ขั้นตอนการตัดไฟในบ้านเมื่อน้ำเริ่มเอ่อล้นเข้าท่วมเพื่อป้องกันไฟดูด?",
                "answer": "1. ปลดเมนสวิตช์หรือเบรกเกอร์ย่อยของชั้น 1 ทันที 2. ห้ามสัมผัสสวิตช์ไฟขณะตัวเปียกหรือแช่น้ำ 3. ถอดปลั๊กเครื่องใช้ไฟฟ้าและยกขึ้นที่สูง หากน้ำท่วมถึงเบรกเกอร์ให้แจ้งการไฟฟ้าตัดไฟสายเมน 1129 หรือ 1130",
                "category": "ความปลอดภัยทางไฟฟ้า"
            },
            {
                "question": "การขอรับถุงยังชีพและยาเวชภัณฑ์ฉุกเฉินสำหรับผู้ป่วยติดเตียง?",
                "answer": "แจ้งผ่านแอปพลิเคชันหรือสายด่วน อสม. ประจำตำบล หรือโทรแจ้ง 1669 โดยระบุพิกัดบ้าน เลขที่บ้าน และจำนวนผู้ป่วยติดเตียงเพื่อจัดชุดเรือแพทย์เคลื่อนที่เข้าส่งยาเฉพาะโรค",
                "category": "ถุงยังชีพและเวชภัณฑ์"
            },
            {
                "question": "วิธีปฏิบัติตัวเมื่อถูกน้ำป่าไหลหลากหรือดินโคลนถล่ม?",
                "answer": "1. อพยพขึ้นที่สูงทันที ไม่ข้ามกระแสน้ำเชี่ยว 2. หลีกเลี่ยงเส้นทางริมห้วยหรือไหล่เขา 3. ห้ามขับรถลุยน้ำที่ลึกเกินครึ่งล้อรถ 4. ส่งสัญญาณไฟฉายหรือเสียงขอความช่วยเหลือ",
                "category": "การเอาชีวิตรอด"
            },
            {
                "question": "การขอเงินชดเชยเยียวยาผู้ประสบภัยน้ำท่วมจากภาครัฐ?",
                "answer": "ถ่ายรูปความเสียหายของบ้านเรือน ทะเบียนบ้าน บัตรประชาชน และติดต่อผู้ใหญ่บ้านหรือ อบต./เทศบาล เพื่อกรอกแบบฟอร์ม ก.ช.ภ.อ. รับเงินเยียวยาครัวเรือนละ 5,000 - 9,000 บาท ตามเกณฑ์",
                "category": "เงินเยียวยาและฟื้นฟู"
            }
        ]

        if not self.is_configured():
            # Keyword/semantic scoring fallback
            matches = []
            q_lower = query.lower()
            for faq in predefined_faqs:
                score = 0
                for word in ["เบอร์", "โทร", "กู้ภัย", "ฉุกเฉิน", "ไฟ", "ไฟฟ้า", "พักพิง", "ศูนย์", "ถุงยังชีพ", "ยา", "เงิน", "ชดเชย", "น้ำป่า", "เรือ"]:
                    if word in q_lower and word in (faq["question"] + faq["answer"]):
                        score += 30
                if any(k in faq["question"] for k in query.split()):
                    score += 40
                if score > 0:
                    matches.append({**faq, "similarity_score": min(score, 98)})

            matches.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            return {
                "success": True,
                "query": query,
                "matches": matches if matches else predefined_faqs[:2],
                "is_mock": True
            }

        url = "https://api.aiforthai.in.th/faq-search"
        headers = {"Apikey": self.api_key}
        params = {"text": query}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            if response.status_code == 200:
                return {"success": True, "query": query, "matches": response.json(), "is_mock": False}
            else:
                return self.search_faq(query)
        except Exception:
            return self.search_faq(query)
