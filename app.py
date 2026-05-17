import streamlit as st

st.set_page_config(page_title="PrefixSpan Demo", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-testid="stContainer"] {
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        background-color: #ffffff;
        padding: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    div[data-testid="stContainer"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("PrefixSpan Algorithm Data Mining Platform")
st.markdown("---")

st.markdown("""
### Tổng quan về đồ án
Ứng dụng này mô phỏng môi trường kiểm thử trực quan cho thuật toán **PrefixSpan** (Prefix-Projected Sequential Pattern Mining). Thuật toán được chạy tối ưu trên bộ dữ liệu **Online Retail Dataset** (Lịch sử giao dịch bán lẻ trực tuyến thương mại điện tử).

* **Ngưỡng kiểm thử hiện tại:** Mức độ hỗ trợ tối thiểu (Minimum Support) được cấu hình cố định tại mức **0.5%** tổng quy mô tập khách hàng.

### Hướng dẫn trải nghiệm nhanh các Phân hệ:
Sử dụng thanh công cụ điều hướng tích hợp sẵn tại giao diện bên trái (**Sidebar**) để chuyển tiếp giữa các màn hình chức năng:
1. **Admin Dashboard**: Giao diện dành cho nhà quản trị doanh nghiệp, hiển thị trực quan các báo cáo phân tích, biểu đồ tròn thể hiện phân phối và biểu đồ dòng chảy hành vi khách hàng.
2. **Storefront**: Giao diện trải nghiệm giả lập ứng dụng mua sắm B2C thương mại điện tử, tự động kích hoạt bộ máy gợi ý bán chéo (Cross-selling suggestions) theo dòng thời gian thực mỗi khi bạn thêm bớt giỏ hàng.
""")