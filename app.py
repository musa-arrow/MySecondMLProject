import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

from model.utils import predict_crop, load_model, get_typical_values

st.set_page_config(page_title="Tarım Asistanı", layout="centered")

selected_tab = st.sidebar.radio("🧭 Sayfa Seçimi", ["Tahmin", "Model Analizi"])

if selected_tab == "Tahmin":
    st.title("Tarım Asistanı 🌱")
    st.subheader("Tarım verilerinizi analiz ederek en iyi sonuçları elde edin")

    with st.form("veri_formu"):
        st.markdown("### 🌾 Veri Girişi")
        col1, col2 = st.columns(2)

        with col1:
            ph = st.slider("Toprak pH Değeri", 3.5, 9.5, 6.5, step=0.1)
            N = st.number_input("Azot (N)", min_value=0, value=60)
            P = st.number_input("Fosfor (P)", min_value=0, value=40)
            K = st.number_input("Potasyum (K)", min_value=0, value=50)

        with col2:
            temperature = st.slider("Sıcaklık (°C)", -10.0, 50.0, 25.0, step=0.5)
            rainfall = st.slider("Yağış (mm)", 0.0, 400.0, 100.0, step=1.0)

        submitted = st.form_submit_button("Tahmin Et")

    if submitted:
        try:
            crop = predict_crop(N, P, K, ph, rainfall, temperature)
            st.success(f"🌾 Önerilen ürün: **{crop.upper()}**")

            typical = get_typical_values(crop)
            if typical:
                st.markdown("### 📊 Tipik Değerler")
                for key, value in typical.items():
                    st.write(f"{key}: `{value}`")

        except Exception as e:
            st.error(f"❌ Tahmin sırasında hata oluştu: {e}")

elif selected_tab == "Model Analizi":
    st.title("📊 Model Performansı")

    try:
        model, encoder = load_model()
        features = ["N", "P", "K", "pH", "rainfall", "temperature"]
        importances = model.feature_importances_

        if len(features) == len(importances):
            fig, ax = plt.subplots()
            ax.barh(features, importances)
            ax.set_title("Özellik Önem Düzeyleri")
            ax.set_xlabel("Önem Skoru")
            ax.invert_yaxis()
            st.pyplot(fig)
            st.markdown("🔍 Bu grafik, modelin hangi değişkenlere ne kadar önem verdiğini gösterir.")
        else:
            st.warning("⚠️ Özellik sayısı uyuşmadı. Eğitim verilerini kontrol edin.")

    except Exception as e:
        st.error(f"❌ Analiz yüklenemedi: {e}")