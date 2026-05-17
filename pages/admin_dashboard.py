import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_patterns

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("📊 Admin Dashboard - Thống kê Hành vi Khách hàng")
st.markdown("Nền tảng phân tích chuyên sâu các mô hình hành vi tuần tự được khai phá từ thuật toán PrefixSpan.")

# Tải dữ liệu
df = load_patterns()

if not df.empty:
    # =====================================================================
    # PHẦN 1: HÀNG KPI CHỈ SỐ TỔNG QUAN
    # =====================================================================
    st.markdown("### 📈 Chỉ số Hiệu suất chính (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    
    # Tính toán các chỉ số nâng cao từ tập dữ liệu có sẵn
    max_sup = df['Support'].max()
    avg_sup = int(df['Support'].mean())
    multi_seq_count = len(df[df["Pattern"].str.contains("->", regex=False)])
    
    with col1:
        st.metric(label="Tổng số tập luật", value=f"{len(df):,}", delta="Đã khai phá", delta_color="normal")
    with col2:
        st.metric(label="Luật tuần tự (Chứa chuỗi)", value=f"{multi_seq_count:,}", delta="Có liên kết ->")
    with col3:
        st.metric(label="Độ hỗ trợ lớn nhất", value=f"{max_sup:,}", delta="Mẫu phổ biến nhất")
    with col4:
        st.metric(label="Độ hỗ trợ trung bình", value=f"{avg_sup:,}", delta="Trên toàn tập luật")

    st.markdown("---")

    # =====================================================================
    # PHẦN 2: HỆ THỐNG TABS PHÂN CHIA GIAO DIỆN
    # =====================================================================
    tab1, tab2, tab3 = st.tabs([
        "📊 Phân tích xu hướng", 
        "🔗 Biểu đồ Sankey", 
        "🗄️ Tra cứu Luật"
    ])

    # ---------------------------------------------------------------------
    # TAB 1: PHÂN TÍCH XU HƯỚNG & ĐỘ DÀI CHUỖI
    # ---------------------------------------------------------------------
    with tab1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Top 10 Hành vi phổ biến nhất")
            top_10 = df.sort_values(by="Support", ascending=False).head(10)
            
            fig = px.bar(
                top_10, 
                x="Support", 
                y="Pattern", 
                orientation='h', 
                color="Support",
                color_continuous_scale="Blues",
                labels={"Support": "Độ hỗ trợ (Lượt mua)", "Pattern": "Mẫu hành vi"}
            )
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            st.subheader("Phân phối Độ dài Chuỗi hành vi")
            df['Độ dài chuỗi'] = df['Pattern'].apply(lambda x: x.count('->') + 1)
            length_dist = df['Độ dài chuỗi'].value_counts().reset_index()
            length_dist.columns = ['Số lượng sản phẩm', 'Số lượng Luật']
            
            fig_pie = px.pie(
                length_dist, 
                names='Số lượng sản phẩm', 
                values='Số lượng Luật', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------------------------------------------------------------
    # TAB 2: BIỂU ĐỒ DÒNG CHẢY SANKEY (INTERACTIVE SLEEK VERSION)
    # ---------------------------------------------------------------------
    with tab2:
        st.subheader("🔗 Biểu đồ Dòng chảy Hành vi Mua sắm (Sankey Diagram)")
        st.markdown("Biểu đồ thể hiện trực quan lộ trình mua sắm động của khách hàng. Luồng dày hơn thể hiện xác suất xảy ra chuỗi hành vi đó cao hơn.")
        
        num_flows = st.slider("Điều chỉnh số lượng luồng hành vi hiển thị:", min_value=5, max_value=40, value=15, step=5)
        
        sequential_df = df[df["Pattern"].str.contains("->", regex=False)]
        
        if not sequential_df.empty:
            top_sankey = sequential_df.sort_values(by="Support", ascending=False).head(num_flows)
            
            nodes = []
            sources = []
            targets = []
            values = []
            
            def get_node_index(node_name):
                if node_name not in nodes:
                    nodes.append(node_name)
                return nodes.index(node_name)
                
            for _, row in top_sankey.iterrows():
                pattern_str = row["Pattern"]
                support = row["Support"]
                
                # Tách chuỗi dạng: [Item A] -> [Item B] -> [Item C] và bỏ dấu ngoặc []
                raw_items = [item.strip()[1:-1] for item in pattern_str.split("->")]
                
                # Thêm nhãn bước (Bước 1, Bước 2...)
                steps_items = [f"{item} (Bước {i+1})" for i, item in enumerate(raw_items)]
                
                for i in range(len(steps_items) - 1):
                    src = steps_items[i]
                    tgt = steps_items[i+1]
                    
                    sources.append(get_node_index(src))
                    targets.append(get_node_index(tgt))
                    values.append(support)
            
            fig_sankey = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 20,
                    thickness = 15,
                    line = dict(color = "rgba(0,0,0,0.3)", width = 0.5),
                    label = nodes,
                    color = "#3182bd"
                ),
                link = dict(
                    source = sources,
                    target = targets,
                    value = values,
                    color = "rgba(49, 130, 189, 0.15)"
                )
            )])
            
            fig_sankey.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                font_size=10,
                height=550
            )
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("Không có đủ dữ liệu chuỗi tuần tự để biểu diễn sơ đồ Sankey.")

    # ---------------------------------------------------------------------
    # TAB 3: TRA CỨU DỮ LIỆU
    # ---------------------------------------------------------------------
    with tab3:
        st.subheader("🗄️ Tra cứu Kho tập luật")
        st.markdown("*Lưu ý: Hệ thống sử dụng bảng hiển thị tự động xuống dòng đối với các chuỗi dài (Hiển thị tối đa 100 dòng đầu để tối ưu tốc độ).*")
        
        search_term = st.text_input("🔍 Nhập từ khóa hoặc tên sản phẩm để lọc nhanh:", placeholder="Ví dụ: HEART, LUNCH BAG...")
        
        if search_term:
            filtered_df = df[df["Pattern"].str.contains(search_term, case=False, na=False, regex=False)]
            st.write(f"Tìm thấy **{len(filtered_df):,}** kết quả trùng khớp.")
            
            st.table(filtered_df.head(100).reset_index(drop=True))
            
        else:
            st.write(f"Tổng số tập luật có trong hệ thống: **{len(df):,}**.")
            
            st.table(df.head(100).reset_index(drop=True))
else:
    st.warning("Không tìm thấy dữ liệu mẫu hành vi. Vui lòng kiểm tra lại cấu hình file trong thư mục data.")