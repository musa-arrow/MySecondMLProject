import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium

# Sayfa yapılandırması
st.set_page_config(page_title="Tarım Asistanı", layout="wide")

# Başlık ve açıklama
st.title("Tarım Asistanı")
st.subheader("Tarım verilerinizi analiz ederek en iyi sonuçları elde edin")

# Veri setlerini yükle
@st.cache_data
def load_data():
    crop_data = pd.read_csv("Crop_recommendation.csv")
    fertilizer_data = pd.read_csv("fertilizer_recommendation_dataset.csv")
    pest_data = pd.read_csv("pest_infestation.csv")
    return crop_data, fertilizer_data, pest_data

crop_data, fertilizer_data, pest_data = load_data()

# Ana içerik ve sidebar için iki sütun oluştur
col_map, col_inputs = st.columns([2, 1])

# Harita sütunu
with col_map:
    st.header("Konum Seçimi")
    st.write("Haritada bir noktaya tıklayarak konum seçin")
    
    # Başlangıç koordinatları (Türkiye'nin merkezi)
    if 'latitude' not in st.session_state:
        st.session_state.latitude = 39.9334
    if 'longitude' not in st.session_state:
        st.session_state.longitude = 32.8597
    
    # Harita oluştur
    m = folium.Map(
        location=[st.session_state.latitude, st.session_state.longitude], 
        zoom_start=6
    )
    
    # Marker ekle
    folium.Marker(
        [st.session_state.latitude, st.session_state.longitude],
        popup="Seçilen Konum",
        tooltip="Analiz Konumu"
    ).add_to(m)
    
    # Haritayı göster ve tıklama olayını yakala
    map_data = st_folium(m, width=700, height=500)
    
    # Harita tıklaması varsa koordinatları güncelle
    if map_data['last_clicked'] is not None:
        st.session_state.latitude = map_data['last_clicked']['lat']
        st.session_state.longitude = map_data['last_clicked']['lng']
    
    st.write(f"Seçilen konum: Enlem {st.session_state.latitude:.6f}, Boylam {st.session_state.longitude:.6f}")

# Veri giriş formu sütunu
with col_inputs:
    st.header("Veri Girişi")
    
    # Çevresel faktörler
    st.subheader("Çevresel Faktörler")
    temperature = st.slider("Sıcaklık (°C)", 0.0, 50.0, 25.0)
    humidity = st.slider("Nem (%)", 0.0, 100.0, 60.0)
    rainfall = st.slider("Yağış (mm)", 0.0, 500.0, 200.0)
    ph = st.slider("Toprak pH", 0.0, 14.0, 6.5)
    
    # Besin değerleri
    st.subheader("Toprak Besin Değerleri")
    col1, col2, col3 = st.columns(3)
    N = col1.number_input("Azot (N)", 0.0, 200.0, 50.0)
    P = col2.number_input("Fosfor (P)", 0.0, 200.0, 50.0)
    K = col3.number_input("Potasyum (K)", 0.0, 200.0, 50.0)
    
    # Toprak ve mahsul bilgisi
    st.subheader("Toprak ve Mahsul Bilgisi")
    soil_types = ["Loamy Soil", "Peaty Soil", "Acidic Soil", "Sandy Soil"]
    crop_types = ["rice", "wheat", "maize", "arpa"]
    fertilizer_types = ["Compost", "Balanced NPK Fertilizer", "Water Retaining Fertilizer", "Organic Fertilizer", "Gypsum", "Lime", "DAP", "organik"]
    
    soil_type = st.selectbox("Toprak Tipi", soil_types)
    crop_type = st.selectbox("Mahsul Tipi", crop_types)
    fertilizer_type = st.selectbox("Gübre Tipi", fertilizer_types)
    pest_count = st.slider("Haşere Sayısı", 0, 30, 5)
    
    # Tahmin butonu
    if st.button("Tahmin Yap", type="primary"):
        # API isteği için veri hazırlama
        data = {
            "latitude": st.session_state.latitude,
            "longitude": st.session_state.longitude,
            "temperature": temperature,
            "humidity": humidity,
            "rainfall": rainfall,
            "ph": ph,
            "N": N,
            "P": P,
            "K": K,
            "soil_type": soil_type,
            "crop_type": crop_type,
            "fertilizer_type": fertilizer_type,
            "pest_count": pest_count
        }
        
        # API isteği gönderme
        try:
            response = requests.post("http://localhost:8000/predict", json=data)
            result = response.json()
            
            # Sonuçları gösterme
            st.header("Tahmin Sonuçları")
            
            # Sonuç kartı
            result_color = "green" if result["result"] == "olumlu" else "red"
            st.markdown(f"<div style='background-color: {result_color}20; padding: 20px; border-radius: 10px; margin: 10px 0;'>" +
                       f"<h3 style='color: {result_color}; margin: 0;'>Sonuç: {result['result'].upper()}</h3>" +
                       f"<h4 style='margin: 10px 0;'>Olasılık: {result['probability']:.2f}%</h4>" +
                       f"<p style='margin: 0;'>{result['message']}</p>" +
                       f"</div>", unsafe_allow_html=True)
            
            # Raporu kaydetme
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_data = {
                "timestamp": timestamp,
                "location": {"lat": st.session_state.latitude, "lng": st.session_state.longitude},
                "inputs": data,
                "result": result["result"],
                "probability": result["probability"],
                "recommendations": [
                    "Sıcaklık değerleri optimum aralıkta tutulmalıdır.",
                    "Nem seviyesi mahsul tipine göre ayarlanmalıdır.",
                    "Toprak pH'ı düzenli olarak kontrol edilmelidir.",
                    "Haşere kontrolü için düzenli gözlem yapılmalıdır."
                ]
            }
            
            # Rapor klasörünü kontrol et ve oluştur
            if not os.path.exists("reports"):
                os.makedirs("reports")
                
            # Raporu JSON olarak kaydet
            with open(f"reports/result_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
            
            st.success(f"Rapor kaydedildi: reports/result_{timestamp}.json")
            
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")
            st.info("FastAPI sunucusunun çalıştığından emin olun: python -m uvicorn main:app --reload")

# Buradan sonraki tüm veri analizi kısmını siliyoruz
# Ana içerik - Veri Görselleştirme bölümü ve sonrası silinecek
st.header("Veri Analizi")
tab1, tab2, tab3 = st.tabs(["Mahsul Verileri", "Gübre Verileri", "Haşere Verileri"])

with tab1:
    st.header("Mahsul Verileri")
    st.dataframe(crop_data.head(10))
    
    # Basit istatistikler
    st.subheader("Mahsul İstatistikleri")
    col1, col2 = st.columns(2)
    col1.metric("Toplam Mahsul Sayısı", len(crop_data))
    col2.metric("Benzersiz Mahsul Türleri", crop_data["label"].nunique())
    
    # Grafikler
    st.subheader("Mahsul Dağılımı")
    crop_counts = crop_data["label"].value_counts()
    st.bar_chart(crop_counts)

with tab2:
    st.header("Gübre Verileri")
    st.dataframe(fertilizer_data.head(10))
    
    # Basit istatistikler
    st.subheader("Gübre İstatistikleri")
    col1, col2 = st.columns(2)
    col1.metric("Toplam Gübre Kaydı", len(fertilizer_data))
    col2.metric("Benzersiz Gübre Türleri", fertilizer_data["Fertilizer"].nunique())
    
    # Grafikler
    st.subheader("Gübre Dağılımı")
    fertilizer_counts = fertilizer_data["Fertilizer"].value_counts()
    st.bar_chart(fertilizer_counts)

with tab3:
    st.header("Haşere Verileri")
    st.dataframe(pest_data)
    
    # Basit istatistikler
    st.subheader("Haşere İstatistikleri")
    col1, col2 = st.columns(2)
    col1.metric("Toplam Haşere Kaydı", len(pest_data))
    col2.metric("Ortalama Haşere Sayısı", pest_data["pest_count"].mean())
    
    # Grafikler
    st.subheader("Haşere Seviyesi Dağılımı")
    pest_counts = pest_data["infestation_level"].value_counts()
    st.bar_chart(pest_counts)