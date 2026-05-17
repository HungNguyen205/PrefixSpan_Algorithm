import streamlit as st
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATTERN_FILE_PATH = os.path.join(BASE_DIR, "data", "output_online_retail_mapped_0.5.txt")
PRODUCT_MAPPING_PATH = os.path.join(BASE_DIR, "data", "item_mapping.json")

@st.cache_data
def load_patterns():
    # Đường dẫn tới file kết quả
    filepath = PATTERN_FILE_PATH
    
    patterns = []
    supports = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Cắt chuỗi bằng ký tự |
                if ' | (Support: ' in line:
                    pattern_part, support_part = line.split(' | (Support: ')
                    # Loại bỏ dấu ')' để lấy số
                    support_val = int(support_part.replace(')', ''))
                    patterns.append(pattern_part)
                    supports.append(support_val)
        
        df = pd.DataFrame({
            'Pattern': patterns,
            'Support': supports
        })
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file pattern: {e}")
        return pd.DataFrame(columns=['Pattern', 'Support'])

@st.cache_data
def load_products():
    filepath = PRODUCT_MAPPING_PATH
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return list(data.values())
    except Exception as e:
        st.error(f"Lỗi khi đọc file products: {e}")
        return []
