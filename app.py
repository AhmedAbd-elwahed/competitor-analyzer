import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# ضبط إعدادات الصفحة والواجهة
st.set_page_config(page_title="محلل المنافسين - أثاث مكتبي", layout="wide")

st.title("📊 أداة تحليل الكلمات الهيكلية للمنافسين")
st.write("أدخل رابط موقع المنافس لاستخراج الكلمات الرئيسية والفرعية المصنفة تلقائياً.")

# خانة إدخال الرابط
target_url = st.text_input("رابط موقع المنافس:", placeholder="https://example.com")

if st.button("بدء التحليل 🚀"):
    if not target_url:
        st.warning("يرجى إدخال الرابط أولاً.")
    else:
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url

        st.info("جاري فحص وتفكيك كود الموقع...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(target_url, headers=headers, timeout=12)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = []

            # استخراج العناوين الرئيسية Title و H1
            if soup.title and soup.title.string:
                data.append({
                    'الكلمة / العبارة': soup.title.string.strip(),
                    'التصنيف': 'رئيسية (Primary)',
                    'موقعها': 'Page Title'
                })

            for h1 in soup.find_all('h1'):
                txt = h1.get_text().strip()
                if txt:
                    data.append({'الكلمة / العبارة': txt, 'التصنيف': 'رئيسية (Primary)', 'موقعها': 'H1 Tag'})

            # استخراج العناوين الفرعية H2 و H3
            for h2 in soup.find_all('h2'):
                txt = h2.get_text().strip()
                if txt:
                    data.append({'الكلمة / العبارة': txt, 'التصنيف': 'فرعية (Secondary)', 'موقعها': 'H2 Tag'})

            for h3 in soup.find_all('h3'):
                txt = h3.get_text().strip()
                if txt:
                    data.append({'الكلمة / العبارة': txt, 'التصنيف': 'فرعية (Secondary)', 'موقعها': 'H3 Tag'})

            df = pd.DataFrame(data).drop_duplicates(subset=['الكلمة / العبارة'])

            if not df.empty:
                st.success("تم التحليل بنجاح!")
                
                # عرض الجدول الرئيسي
                st.dataframe(df, use_container_width=True)

                st.markdown("---")
                
                # تحويل البيانات إلى صيغة Tab-Separated للنسخ المباشر المريح لـ Google Sheets
                tsv_data = df.to_csv(index=False, sep='\t')
                
                st.subheader("📋 نسخ البيانات للقطها مباشرة بداخل Google Sheets")
                st.caption("اضغط على أيقونة النسخ 📋 في زاوية المربع الأبيض بالأسفل، ثم اعمل Paste بداخل الشيت فوراً:")
                
                # مربع كود يحتوي تلقائياً على زر Copy بداخل Streamlit
                st.code(tsv_data, language='text')

                # زر تحميل CSV
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="⬇️ تحميل البيانات كملف CSV",
                    data=csv_data,
                    file_name="competitor_keywords.csv",
                    mime="text/csv"
                )
            else:
                st.error("لم يتم العثور على عناوين في الصفحة.")

        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالرابط: {e}")
