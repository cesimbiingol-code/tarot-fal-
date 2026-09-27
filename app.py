import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import random

# Sayfa Ayarları
st.set_page_config(page_title="Mistik Tarot Kehaneti", page_icon="🔮", layout="centered")

# CSS - Özel Mistik Tema
st.markdown("""
<style>
    .stApp { background-color: #0f0a1c; color: #e2e8f0; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    .stButton>button { width: 100%; background-color: #4c1d95; color: #d4af37; border: 1px solid #d4af37; font-weight: bold; }
    .stButton>button:hover { background-color: #5b21b6; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.title("🔮 ACI GERÇEKLER TAROTU")
st.caption("Pembe tablolar yok. Sadece kartlar ve saklanan gerçekler.")

# NVIDIA API Key Girişi
api_key = st.sidebar.text_input("NVIDIA API Key Giriniz", type="password")

# Form Alanı
with st.form("tarot_form"):
    name = st.text_input("Adınız / Danışan Adı", placeholder="Örn: Selin")
    birth_date = st.date_input("Doğum Tarihiniz")
    topic = st.selectbox("Fal Konusu", ["Aşk ve İlişkiler", "Kariyer ve Para", "Genel Gelecek & Engeller"])
    package = st.radio("Paket Seçimi", ["Standart Paket (3 Kart)", "Premium Paket (5 Kart)"])
    submitted = st.form_submit_button("🔮 KARTLARI KAR VE FALI BAŞLAT")

all_cards = ["Kule", "Ölüm", "Aşıklar", "Kılıç Üçlüsü", "Kupa Ası", "Büyücü", "Şeytan", "Ay", "Güneş", "Adalet", "Kılıç Dokuzlusu", "Azize"]

def generate_pdf(reading_text, name, topic):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#2C1A4D"), alignment=1, spaceAfter=15)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor("#1A1A1A"), spaceAfter=8)

    story = [
        Paragraph("<b>🔮 ÖZEL TAROT KEHANET RAPORU</b>", title_style),
        Paragraph(f"<b>Danışan:</b> {name} | <b>Odak:</b> {topic}", styles['Normal']),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6B46C1"), spaceAfter=15)
    ]

    for paragraph in reading_text.split('\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

if submitted:
    if not api_key:
        st.error("Lütfen sol menüden NVIDIA API Anahtarınızı giriniz!")
    else:
        num_cards = 3 if "3" in package else 5
        selected_cards = random.sample(all_cards, num_cards)
        
        st.info(f"Çekilen Kartlar: {', '.join(selected_cards)}")
        st.write("🔮 *NVIDIA AI derin kehaneti hazırlıyor, lütfen bekleyin...*")
        
        try:
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
            
            system_prompt = "Sen son derece deneyimli, acımasızca dürüst, duygusallıktan uzak ve keskin öngörüleri olan profesyonel bir Tarot üstadısın. Pembe hayaller kurdurma, gerçekleri acımasızca yüzleşitir."
            user_prompt = f"Danışan: {name}, Doğum Tarihi: {birth_date}, Konu: {topic}, Paket: {package}, Kartlar: {', '.join(selected_cards)}. Detaylı, keskin ve uzun bir analiz yap."

            response = client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7,
                max_tokens=2500
            )

            reading_text = response.choices[0].message.content
            st.success("Fal Analiziniz Hazır!")
            st.write(reading_text)

            # PDF İndirme Butonu
            pdf_bytes = generate_pdf(reading_text, name, topic)
            st.download_button(
                label="📄 2 Sayfalık PDF Raporunu İndir",
                data=pdf_bytes,
                file_name=f"Tarot_Fali_{name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
