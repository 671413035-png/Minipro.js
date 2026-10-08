import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from services.aiforthai import AIForThaiClient
from services.llm import LLMService

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="Smart Flood Crisis & Rescue Platform",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Crisis Platform styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        border: 1px solid #F87171;
    }
    .badge-high {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        border: 1px solid #FB923C;
    }
    .badge-medium {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        border: 1px solid #FACC15;
    }
    .badge-low {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        border: 1px solid #4ADE80;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "incidents" not in st.session_state:
    st.session_state.incidents = [
        {
            "id": "EMG-1001",
            "time": "19:45 น.",
            "source": "Voice STT",
            "urgency": "CRITICAL",
            "urgency_thai": "วิกฤตสูงสุด",
            "location": "หมู่ 3 ชุมชนวัดกู้ ต.บางพูด อ.ปากเกร็ด จ.นนทบุรี",
            "victim_count": "4 คน",
            "vulnerable_groups": ["ผู้ป่วยติดเตียง", "เด็กเล็ก"],
            "needed_items": ["เรือกู้ภัย", "เครื่องผลิตออกซิเจน", "น้ำดื่ม"],
            "status": "กำลังส่งทีมกู้ภัย",
            "summary": "น้ำท่วมสูงมิดหลังคา ผู้ป่วยติดเตียงขาดออกซิเจน"
        },
        {
            "id": "EMG-1002",
            "time": "18:20 น.",
            "source": "OCR Image",
            "urgency": "HIGH",
            "urgency_thai": "เร่งด่วนมาก",
            "location": "ซอยสุขุมวิท 101/1 แขวงบางจาก เขตพระโขนง กทม.",
            "victim_count": "2 คน",
            "vulnerable_groups": ["ผู้สูงอายุ"],
            "needed_items": ["เรือยาง", "อาหารกล่อง"],
            "status": "รอดำเนินการ",
            "summary": "ระดับน้ำระดับอก ตัดไฟฟ้าในชุมชนแล้ว"
        },
        {
            "id": "EMG-1003",
            "time": "17:10 น.",
            "source": "Web Input",
            "urgency": "MEDIUM",
            "urgency_thai": "ปานกลาง",
            "location": "ม.4 ต.ป่าแดด อ.เมือง จ.เชียงใหม่",
            "victim_count": "5 คน",
            "vulnerable_groups": ["สัตว์เลี้ยง"],
            "needed_items": ["น้ำดื่มสะอาด", "อาหารแห้ง"],
            "status": "จ่ายเสบียงแล้ว",
            "summary": "น้ำท่วมถนนหน้าบ้านสัญจรลำบาก แต่บ้าน 2 ชั้นปลอดภัย"
        }
    ]

# Sidebar Configuration
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSA2d29tY-x1XSJVb-p8FM8p5dpthapZGVjkD1Jxwa0tlUtgArx7fJCTpw&s=10ฆฆ", width=64)
    st.title("🌊 ศูนย์บัญชาการภัยพิบัติ")
    st.caption("Smart Flood Crisis & Rescue Platform (AIForThai + ThaiLLM)")

    st.markdown("---")
    st.subheader("🔑 ตั้งค่าการเชื่อมต่อ API")
    
    aiforthai_key_input = st.text_input(
        "AIForThai API Key",
        value=os.getenv("AIFORTHAI_API_KEY", ""),
        type="password",
        help="ขอรับคีย์ได้ที่ https://aiforthai.in.th/"
    )
    
    llm_key_input = st.text_input(
        "LLM API Key (OpenAI / Typhoon)",
        value=os.getenv("LLM_API_KEY", ""),
        type="password",
        help="คีย์สำหรับโมเดลภาษาไทยหรือ OpenAI"
    )

    llm_base_url = st.text_input(
        "LLM Base URL",
        value=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        help="Default: https://api.openai.com/v1 หรือ endpoint ของ Typhoon/vLLM"
    )

    llm_model = st.text_input(
        "LLM Model Name",
        value=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        help="เช่น gpt-4o-mini, typhoon-v1.5x-70b-instruct"
    )

    # Status indicators
    aiforthai_client = AIForThaiClient(api_key=aiforthai_key_input)
    llm_service = LLMService(api_key=llm_key_input, base_url=llm_base_url, model=llm_model)

    st.markdown("---")
    st.subheader("📡 สถานะการทำงาน")
    if aiforthai_client.is_configured():
        st.success("✅ AIForThai API: พร้อมใช้งาน (Live)")
    else:
        st.info("ℹ️ AIForThai: โหมดจำลองข้อมูล (Smart Mock)")

    if llm_service.is_configured():
        st.success(f"✅ LLM: พร้อมใช้งาน ({llm_model})")
    else:
        st.info("ℹ️ LLM: โหมด Heuristic Thai NLP Fallback")

    st.markdown("---")
    st.markdown("**สายด่วนฉุกเฉิน:**")
    st.markdown("☎️ กรมป้องกันฯ ปภ.: **1784**")
    st.markdown("🚑 การแพทย์ฉุกเฉิน: **1669**")
    st.markdown("⚡ แจ้งไฟฟ้าขัดข้อง: **1129 / 1130**")

# Top Header Bar
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-header">Smart Flood Crisis & Rescue Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ระบบรวมศูนย์การแจ้งเหตุ คัดกรองความเร่งด่วนด้วย AI และเฝ้าระวังภัยพิบัติน้ำท่วมอัจฉริยะ</div>', unsafe_allow_html=True)
with col_h2:
    critical_count = sum(1 for inc in st.session_state.incidents if inc["urgency"] == "CRITICAL")
    st.metric(label="เคสวิกฤตที่ต้องช่วยทันที 🚨", value=f"{critical_count} ราย", delta=f"ทั้งหมด {len(st.session_state.incidents)} ราย", delta_color="inverse")

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🚨 1. TAG: รับแจ้งเหตุ & คัดกรองวิกฤต",
    "📊 2. EmoNews: เฝ้าระวังอารมณ์และข่าวสาร",
    "🎙️ 3. VAJAX: ผู้ช่วยเสียงวิทยุสื่อสาร (Voice)",
    "❓ 4. FAQ: ค้นหาคู่มือและข้อมูลผู้ประสบภัย"
])

# ==============================================================================
# TAB 1: TAG (Main Crisis Dashboard & Emergency Rescue Classifier)
# ==============================================================================
with tab1:
    st.subheader("🚨 ศูนย์รับแจ้งเหตุและคัดกรองภัยพิบัติอัตโนมัติ (TAG Classifier)")
    st.write("รองรับการแจ้งเหตุผ่าน 3 ช่องทาง: ข้อความตัวอักษร, ภาพถ่าย/สกรีนช็อต (OCR), หรือไฟล์เสียงบันทึก (STT)")

    input_method = st.radio(
        "เลือกวิธีการแจ้งเหตุ:",
        ["✍️ พิมพ์ข้อความแจ้งเหตุ", "📷 อัปโหลดรูปภาพ / สกรีนช็อตข้อความ (OCR)", "🎤 อัปโหลดไฟล์เสียงขอความช่วยเหลือ (STT)"],
        horizontal=True
    )

    emergency_raw_text = ""

    if input_method == "✍️ พิมพ์ข้อความแจ้งเหตุ":
        sample_presets = [
            "เลือกตัวอย่างเหตุการณ์...",
            "ตัวอย่าง 1 (วิกฤต): ช่วยด้วยครับ! น้ำท่วมมิดหลังคา ซอยวัดกู้ ต.บางพูด นนทบุรี มีผู้ป่วยติดเตียง 1 คน เด็ก 2 คน ออกซิเจนใกล้หมด ต้องการเรือด่วน",
            "ตัวอย่าง 2 (เร่งด่วน): น้ำเอ่อล้นทะลักเข้าบ้านระดับอก ถนนเทศบาล 5 เชียงใหม่ ตัดไฟแล้ว ติดอยู่ 3 คน ขอน้ำดื่มและเรืออพยพ",
            "ตัวอย่าง 3 (ทั่วไป): น้ำท่วมผิวถนนหน้าหมู่บ้านประมาณ 15 ซม. รถเล็กยังผ่านได้ อยากทราบว่ามีกระสอบทรายแจกที่จุดไหนบ้างครับ"
        ]
        selected_sample = st.selectbox("🎯 ทดลองด้วยข้อความจำลอง:", sample_presets)
        preset_val = selected_sample if selected_sample != sample_presets[0] else ""
        emergency_raw_text = st.text_area("กรอกรายละเอียดเหตุการณ์และพิกัด:", value=preset_val, height=110, placeholder="พิมพ์ข้อความที่ต้องการขอความช่วยเหลือ เช่น พิกัด จำนวนคน ระดับน้ำ...")

    elif input_method == "📷 อัปโหลดรูปภาพ / สกรีนช็อตข้อความ (OCR)":
        col_img1, col_img2 = st.columns([1, 1])
        with col_img1:
            uploaded_img = st.file_uploader("อัปโหลดภาพถ่ายสถานที่น้ำท่วม หรือภาพสกรีนช็อตโพสต์ขอความช่วยเหลือ (JPG/PNG)", type=["jpg", "jpeg", "png"])
            if uploaded_img:
                st.image(uploaded_img, caption="รูปภาพที่อัปโหลด", use_container_width=True)
        with col_img2:
            st.info("💡 ระบบจะใช้ **AIForThai OCR API** ดึงข้อความภาษาไทยจากภาพโดยอัตโนมัติ")
            if uploaded_img:
                with st.spinner("กำลังประมวลผล OCR จากภาพด้วย AIForThai..."):
                    ocr_res = aiforthai_client.ocr_image(uploaded_img.read(), uploaded_img.name)
                    emergency_raw_text = ocr_res.get("text", "")
                    if ocr_res.get("is_mock"):
                        st.caption("ℹ️ OCR ทำงานในโหมดจำลอง (Smart Mock Result)")
                    st.text_area("ข้อความที่ตรวจจับได้จาก OCR:", value=emergency_raw_text, height=140)
            else:
                st.caption("กรุณาเลือกไฟล์ภาพเพื่อเริ่มการแปลงเป็นข้อความ")

    elif input_method == "🎤 อัปโหลดไฟล์เสียงขอความช่วยเหลือ (STT)":
        col_audio1, col_audio2 = st.columns([1, 1])
        with col_audio1:
            uploaded_audio = st.file_uploader("อัปโหลดคลิปเสียงแจ้งเหตุขอความช่วยเหลือ (WAV/MP3/M4A)", type=["wav", "mp3", "m4a", "ogg"])
            if uploaded_audio:
                st.audio(uploaded_audio)
        with col_audio2:
            st.info("💡 ระบบจะใช้ **AIForThai Speech to Text (Partii STT)** เพื่อถอดเสียงคำพูดเป็นข้อความ")
            if uploaded_audio:
                with st.spinner("กำลังถอดเสียงภาษาไทยด้วย AIForThai STT..."):
                    stt_res = aiforthai_client.speech_to_text(uploaded_audio.read(), uploaded_audio.name)
                    emergency_raw_text = stt_res.get("text", "")
                    if stt_res.get("is_mock"):
                        st.caption("ℹ️ STT ทำงานในโหมดจำลอง (Smart Mock Result)")
                    st.text_area("ข้อความถอดเสียงที่ได้ (Transcription):", value=emergency_raw_text, height=140)
            else:
                st.caption("กรุณาเลือกไฟล์เสียงเพื่อเริ่มการถอดความ")

    # Classification Button
    if st.button("🚀 วิเคราะห์ระดับความเร่งด่วนและจำแนกข้อมูลด้วย LLM", type="primary", use_container_width=True):
        if not emergency_raw_text.strip():
            st.warning("⚠️ กรุณากรอกข้อความ หรืออัปโหลดไฟล์ภาพ/เสียงที่มีข้อมูลแจ้งเหตุก่อนทำการวิเคราะห์")
        else:
            with st.spinner("🤖 ThaiLLM กำลังวิเคราะห์ระดับความเร่งด่วน สกัดพิกัด จำนวนผู้ประสบภัย และสิ่งที่ต้องการ..."):
                analysis = llm_service.classify_emergency(emergency_raw_text)

                st.markdown("---")
                st.subheader("📋 ผลลัพธ์การคัดกรองภัยพิบัติ (Classification Result)")

                urgency = analysis.get("urgency", "MEDIUM")
                urgency_thai = analysis.get("urgency_thai", urgency)

                badge_class = {
                    "CRITICAL": "badge-critical",
                    "HIGH": "badge-high",
                    "MEDIUM": "badge-medium",
                    "LOW": "badge-low"
                }.get(urgency, "badge-medium")

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"**ระดับความเร่งด่วน:**")
                    st.markdown(f'<span class="{badge_class}">{urgency} - {urgency_thai}</span>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**จำนวนผู้ประสบภัย:**")
                    st.markdown(f"**{analysis.get('victim_count', 'ไม่ระบุ')}**")
                with c3:
                    st.markdown(f"**ระดับน้ำโดยประมาณ:**")
                    st.markdown(f"**{analysis.get('flood_level', 'ไม่ระบุ')}**")
                with c4:
                    v_groups = ", ".join(analysis.get("vulnerable_groups", [])) or "ไม่มีระบุ"
                    st.markdown(f"**กลุ่มเปราะบาง:**")
                    st.markdown(f"⚠️ {v_groups}")

                col_res_l, col_res_r = st.columns([1, 1])
                with col_res_l:
                    st.markdown(f"📍 **พิกัด/สถานที่เกิดเหตุ:** {analysis.get('location', 'ไม่ระบุ')}")
                    st.markdown(f"📝 **สรุปเหตุการณ์:** {analysis.get('summary', '-')}")
                    st.markdown(f"💡 **เหตุผลประกอบการคัดกรอง:** {analysis.get('reason', '-')}")

                with col_res_r:
                    st.markdown("**📦 สิ่งของและความช่วยเหลือที่จำเป็นเร่งด่วน:**")
                    for item in analysis.get("needed_items", []):
                        st.markdown(f"- 🔸 {item}")

                    st.markdown("**🛡️ ปฏิบัติการที่ระบบแนะนำ (Suggested Actions):**")
                    for act in analysis.get("suggested_actions", []):
                        st.markdown(f"- ✅ {act}")

                # Button to add to dispatch queue
                if st.button("➕ บันทึกเข้าคิวสั่งการกู้ภัย (Dispatch Center Queue)", key="add_incident_btn"):
                    new_inc = {
                        "id": f"EMG-{1000 + len(st.session_state.incidents) + 1}",
                        "time": datetime.now().strftime("%H:%M น."),
                        "source": input_method.split()[0],
                        "urgency": urgency,
                        "urgency_thai": urgency_thai,
                        "location": analysis.get("location", "ไม่ระบุ"),
                        "victim_count": str(analysis.get("victim_count", "ไม่ระบุ")),
                        "vulnerable_groups": analysis.get("vulnerable_groups", []),
                        "needed_items": analysis.get("needed_items", []),
                        "status": "เข้าคิวสั่งการ",
                        "summary": analysis.get("summary", emergency_raw_text[:50])
                    }
                    st.session_state.incidents.insert(0, new_inc)
                    st.success(f"บันทึกเหตุการณ์รหัส {new_inc['id']} เข้าสู่ระบบสั่งการเรียบร้อยแล้ว!")

    st.markdown("---")
    st.subheader("📋 รายการเหตุการณ์ที่อยู่ในระบบบัญชาการกู้ภัย (Active Incident Queue)")
    
    if st.session_state.incidents:
        df_display = []
        for inc in st.session_state.incidents:
            df_display.append({
                "รหัสเหตุ": inc["id"],
                "เวลา": inc["time"],
                "ความเร่งด่วน": f"{inc['urgency']} ({inc['urgency_thai']})",
                "พิกัดสถานที่": inc["location"],
                "จำนวนผู้ประสบภัย": inc["victim_count"],
                "สิ่งของที่ต้องการ": ", ".join(inc.get("needed_items", [])),
                "สถานะปฏิบัติการ": inc["status"]
            })
        st.dataframe(pd.DataFrame(df_display), use_container_width=True)
    else:
        st.info("ยังไม่มีรายการเหตุการณ์ในระบบ")

# ==============================================================================
# TAB 2: EmoNews (Flood News & Social Sentiment Monitoring)
# ==============================================================================
with tab2:
    st.subheader("📊 ระบบติดตามและวิเคราะห์ข่าวสารและอารมณ์สังคม (AIForThai EmoNews)")
    st.write("ตรวจจับกระแสความตื่นตระหนก (Panic Index), ข่าวปลอม และอารมณ์ความรู้สึกของประชาชนในพื้นที่เสี่ยงน้ำท่วม")

    col_e1, col_e2 = st.columns([3, 1])
    with col_e1:
        emonews_query = st.text_input("คีย์เวิร์ดสำหรับตรวจจับข่าวสารและโซเชียลมีเดีย:", value="น้ำท่วม")
    with col_e2:
        emonews_limit = st.slider("จำนวนข่าวที่ต้องการดึง:", min_value=3, max_value=15, value=6)

    with st.spinner("กำลังเชื่อมต่อ AIForThai EmoNews API เพื่อประมวลผลอารมณ์..."):
        emonews_res = aiforthai_client.get_emonews(keyword=emonews_query, limit=emonews_limit)
        news_items = emonews_res.get("data", [])

    # Overview Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("ดัชนีความตระหนกเฉลี่ย (Panic Index)", "58.4 / 100", "เฝ้าระวังระดับสูง")
    with m2:
        st.metric("อารมณ์หลักของสังคม", "😨 วิตกกังวล / หวาดกลัว", "62% ของโพสต์")
    with m3:
        st.metric("ข่าวสารที่วิเคราะห์แล้ว", f"{len(news_items)} รายการ", "อัปเดตแบบ Realtime")
    with m4:
        st.metric("ความต้องการสูงสุดในสื่อ", "🍲 อาหารและน้ำดื่ม", "ตามด้วยเรือกู้ภัย")

    st.markdown("---")
    col_chart, col_feed = st.columns([1, 1.4])

    with col_chart:
        st.subheader("📈 แนวโน้มอารมณ์ความรู้สึกต่อวิกฤต (Emotion Distribution)")
        
        # Prepare mock chart data
        sentiment_chart_data = pd.DataFrame({
            "อารมณ์": ["ความกลัว/วิตกกังวล (Fear)", "ความโกรธ/ตัดพ้อ (Anger)", "ความเศร้าใจ (Sadness)", "ความหวัง/ขอบคุณ (Hope/Joy)", "ความเป็นกลาง (Neutral)"],
            "สัดส่วน (%)": [48, 22, 14, 11, 5]
        }).set_index("อารมณ์")
        st.bar_chart(sentiment_chart_data)

        st.info("💡 **คำแนะนำสำหรับเจ้าหน้าที่สื่อสารวิกฤต:** ปัจจุบันระดับความกลัว (Fear) และความโกรธ (Anger) เรื่องการแจกถุงยังชีพไม่ทั่วถึงกำลังเพิ่มขึ้น ศูนย์บัญชาการควรออกแถลงการณ์แผนการกระจายสิ่งของในแต่ละตำบลเพื่อลดความสับสน")

    with col_feed:
        st.subheader("📰 ข่าวและกระแสโซเชียลล่าสุดที่ตรวจพบ")
        for item in news_items:
            sentiment_badge = "badge-critical" if item.get("panic_score", 0) > 70 else ("badge-high" if item.get("panic_score", 0) > 50 else "badge-low")
            
            with st.container():
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: #64748B;">📅 {item.get('date', 'วันนี้')} | แหล่งที่มา: {item.get('source', 'ข่าวออนไลน์')}</span>
                        <span class="{sentiment_badge}">Panic Score: {item.get('panic_score', 50)}/100</span>
                    </div>
                    <div style="font-weight: 600; font-size: 1.05rem; margin-top: 6px; color: #0F172A;">{item.get('title')}</div>
                    <div style="font-size: 0.9rem; color: #334155; margin-top: 4px;">
                        🏷️ <strong>อารมณ์เด่น:</strong> {item.get('emotion', 'ปกติ')} | <strong>ทิศทาง:</strong> {item.get('sentiment', 'กลาง')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: VAJAX (Voice & Audio Processing / Direct Voice Assistant)
# ==============================================================================
with tab3:
    st.subheader("🎙️ ระบบสื่อสารเสียงกู้ภัยอัจฉริยะ (VAJAX STT & TTS Integration)")
    st.write("แปลงข้อความวิทยุสื่อสารฉุกเฉินเป็นตัวอักษร (STT) และแปลงคำสั่งการเป็นเสียงแจ้งเตือนสำหรับกระจายเสียงตามสาย (TTS)")

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("### 1. ถอดเสียงวิทยุสื่อสาร / สายด่วน (Speech to Text)")
        st.write("ประมวลผลไฟล์เสียงของชาวบ้านหรือเจ้าหน้าที่ภาคสนามด้วย AIForThai Partii STT")
        
        test_audio_sample = st.selectbox(
            "หรือเลือกไฟล์เสียงจำลองเหตุการณ์จริง:",
            [
                "เสียงแจ้งเหตุ 1: ขอเรือช่วยผู้ป่วยติดเตียงที่ชุมชนริมน้ำ",
                "เสียงแจ้งเหตุ 2: แจ้งน้ำป่าทะลักเข้าท่วมโรงเรียนบ้านป่าไม้",
                "เสียงแจ้งเหตุ 3: ต้องการอาหารแห้งและน้ำดื่มสำหรับ 10 ครัวเรือน"
            ]
        )

        audio_file_vajax = st.file_uploader("อัปโหลดไฟล์เสียงสด (.wav, .mp3):", type=["wav", "mp3"], key="vajax_audio_up")
        
        if st.button("🎧 ทำการถอดเสียงเป็นข้อความ (Run STT)", type="primary"):
            with st.spinner("AIForThai กำลังวิเคราะห์และแปลงคลื่นเสียง..."):
                sample_bytes = audio_file_vajax.read() if audio_file_vajax else b"sample_bytes"
                sample_name = audio_file_vajax.name if audio_file_vajax else "preset_voice.wav"
                stt_output = aiforthai_client.speech_to_text(sample_bytes, sample_name)
                
                st.success("ถอดเสียงสำเร็จ!")
                st.text_area("ผลลัพธ์ข้อความที่ได้จากเสียง (Transcript):", value=stt_output.get("text", ""), height=120)
                st.caption(f"สถานะ API: {'จำลอง (Mock)' if stt_output.get('is_mock') else 'เชื่อมต่อจริง (Live)'}")

    with col_v2:
        st.markdown("### 2. สังเคราะห์เสียงประกาศเตือนภัย (Text to Speech - Vaja)")
        st.write("พิมพ์ข้อความประกาศเพื่อสร้างไฟล์เสียงภาษาไทยสำหรับเปิดลำโพงชุมชน หรือวิทยุกระจายเสียง")

        tts_preset = st.selectbox(
            "เลือกเทมเพลตประกาศเตือนภัยฉุกเฉิน:",
            [
                "ประกาศด่วน! ขอให้ประชาชนหมู่ 4 อพยพขึ้นที่สูงทันที ระดับน้ำกำลังเพิ่มขึ้น",
                "แจ้งจุดรับถุงยังชีพ ณ หอประชุมเทศบาล เปิดแจกตั้งแต่เวลา 9 โมงเช้า",
                "โปรดระมัดระวังการตัดกระแสไฟฟ้า ปลดเบรกเกอร์ชั้นล่างเพื่อความปลอดภัยของทุกคน"
            ]
        )

        custom_tts_text = st.text_area("หรือพิมพ์ข้อความประกาศที่ต้องการสร้างเสียง:", value=tts_preset, height=100)

        if st.button("🔊 สังเคราะห์เสียงพูด (Synthesize Thai Voice)", type="primary"):
            with st.spinner("AIForThai Vaja กำลังสร้างไฟล์เสียงสังเคราะห์..."):
                tts_output = aiforthai_client.text_to_speech(custom_tts_text)
                if tts_output.get("audio_url"):
                    st.success("สร้างไฟล์เสียงสำเร็จ!")
                    st.audio(tts_output["audio_url"])
                else:
                    st.info(f"📢 {tts_output.get('message', 'สร้างเสียงจำลองเรียบร้อย')}")
                    # Provide an audio player sample or tone for offline testing
                    st.success(f"ข้อความสำหรับประกาศตามสาย: '{custom_tts_text}' ได้รับการประมวลผลแล้ว พร้อมส่งต่อระบบลำโพงไร้สาย IP Speaker")

# ==============================================================================
# TAB 4: FAQ Question Search (Flood Info & Assistance Search)
# ==============================================================================
with tab4:
    st.subheader("❓ ศูนย์ค้นหาข้อมูลและตอบคำถามภัยพิบัติน้ำท่วม (FAQ Search + LLM Assistant)")
    st.write("ค้นหาแนวทางรับมือ จุดพักพิง และเบอร์ติดต่อสำคัญ ผ่านฐานข้อมูล AIForThai FAQ พร้อมระบบ LLM อัจฉริยะ")

    faq_input = st.text_input(
        "🔎 พิมพ์คำถามหรือค้นหาข้อมูลช่วยเหลือ:",
        value="น้ำท่วมสูงมากต้องการเรือกู้ภัยและช่วยคนแก่ติดเตียง ต้องโทรแจ้งเบอร์ไหนและทำอย่างไร?",
        placeholder="เช่น ศูนย์พักพิงอยู่ที่ไหน, วิธียกคัตเอาต์ตัดไฟ, ขอเงินชดเชยน้ำท่วม..."
    )

    col_q1, col_q2 = st.columns([1, 1])

    with col_q1:
        st.markdown("#### 📑 ข้อมูลทางการที่ตรงกัน (AIForThai FAQ Search)")
        if st.button("🔍 ค้นหาคำตอบจากฐานข้อมูลทางการ", type="primary", use_container_width=True):
            with st.spinner("กำลังค้นหาคำถาม-คำตอบที่มีความหมายใกล้เคียง..."):
                faq_res = aiforthai_client.search_faq(faq_input)
                matches = faq_res.get("matches", [])

                if matches:
                    for i, match in enumerate(matches[:3]):
                        score = match.get("similarity_score", 85)
                        with st.expander(f"📌 {match.get('question')} (ความตรง: {score}%)", expanded=(i==0)):
                            st.markdown(f"**หมวดหมู่:** `{match.get('category', 'ทั่วไป')}`")
                            st.info(match.get("answer"))
                else:
                    st.warning("ไม่พบข้อคำถามที่ตรงในฐานข้อมูลทางการโดยตรง")

    with col_q2:
        st.markdown("#### 🤖 เจ้าหน้าที่ AI ตอบคำถามเฉพาะบุคคล (ThaiLLM Fallback)")
        if st.button("💬 ให้ AI วิเคราะห์และตอบคำถามเพิ่มเติม", use_container_width=True):
            with st.spinner("ThaiLLM กำลังประมวลผลคำแนะนำที่ปลอดภัยที่สุด..."):
                llm_faq_reply = llm_service.generate_faq_response(faq_input)
                st.markdown(llm_faq_reply)

    st.markdown("---")
    st.subheader("📚 คำถามที่พบบ่อยสำหรับผู้ประสบภัย (Crisis Quick Directory)")
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        with st.container():
            st.markdown("""
            **⚡ ความปลอดภัยทางไฟฟ้า**
            - ตัดเมนสวิตช์ชั้น 1 ก่อนน้ำท่วมถึง
            - ห้ามเดินลุยน้ำเข้าใกล้เสาไฟ
            - การไฟฟ้าแจ้งเหตุ: **1129 / 1130**
            """)
    with quick_col2:
        with st.container():
            st.markdown("""
            **🏠 ศูนย์พักพิง & อาหาร**
            - นำบัตรประชาชนและเอกสารสำคัญใส่ซองกันน้ำ
            - สัตว์เลี้ยงนำเข้าศูนย์พักพิงโซนเฉพาะ
            - ประสานงาน อบต./เทศบาล ประจำพื้นที่
            """)
    with quick_col3:
        with st.container():
            st.markdown("""
            **💰 เงินเยียวยาหลังน้ำลด**
            - ถ่ายรูปความเสียหายบ้านเรือนและทรัพย์สิน
            - เตรียมสำเนาทะเบียนบ้านและบัญชีธนาคาร
            - ลงทะเบียนขอรับเงินช่วยเหลือเยียวยา ก.ช.ภ.อ.
            """)

# Footer
st.markdown("---")
st.caption("Smart Flood Crisis & Rescue Platform | Powered by AIForThai (OCR, STT, Vaja TTS, EmoNews, FAQ) & ThaiLLM Architecture | Built with Streamlit")
