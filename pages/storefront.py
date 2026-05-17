import streamlit as st
from utils import load_patterns, load_products

st.set_page_config(page_title="B2C Storefront", layout="wide", initial_sidebar_state="expanded")

st.title("🛍️ B2C Storefront - Mua sắm & Gợi ý")
st.markdown("Mô phỏng trải nghiệm mua hàng và nhận gợi ý thông minh thời gian thực dựa trên thuật toán **PrefixSpan**.")

# Khởi tạo giỏ hàng
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Đọc danh sách sản phẩm
products = load_products()

# --- Giao diện chọn hàng ---
st.markdown("### 🛒 Thêm vào giỏ hàng")
if not products:
    st.warning("Không tải được danh sách sản phẩm.")
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_product = st.selectbox("Chọn một sản phẩm từ danh mục:", products, label_visibility="collapsed")
    with col2:
        if st.button("➕ Thêm vào giỏ", use_container_width=True):
            if selected_product not in st.session_state.cart:
                st.session_state.cart.append(selected_product)
                st.toast(f"Đã thêm **{selected_product}** vào giỏ!", icon="✅")
            else:
                st.toast(f"**{selected_product}** đã có trong giỏ hàng rồi!", icon="⚠️")
            st.rerun()

# --- Hiển thị giỏ hàng trên Sidebar ---
st.sidebar.title("🛒 Giỏ hàng của bạn")
if len(st.session_state.cart) > 0:
    for i, item in enumerate(st.session_state.cart):
        col_item, col_btn = st.sidebar.columns([5, 1])
        with col_item:
            st.markdown(f"**{i+1}.** {item}")
        with col_btn:
            # Nút xóa từng sản phẩm
            if st.button("❌", key=f"remove_{i}", help="Xóa sản phẩm này"):
                st.session_state.cart.pop(i)
                st.rerun()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Xóa toàn bộ giỏ hàng", type="primary", use_container_width=True):
        st.session_state.cart = []
        st.rerun()
else:
    st.sidebar.info("Giỏ hàng đang trống. Hãy thêm sản phẩm để nhận gợi ý nhé!")

# --- Động cơ gợi ý ---
st.markdown("---")
st.markdown("### ✨ Gợi ý dành riêng cho bạn")

if len(st.session_state.cart) > 0:
    # Bước 1: Tạo tiền tố. 
    prefix_str = " -> ".join([f"[{item}]" for item in st.session_state.cart]) + " -> "
    
    df = load_patterns()
    
    if df.empty:
         st.warning("Hệ thống chưa có dữ liệu pattern.")
    else:
        # Bước 2: Tìm kiếm khớp chuỗi
        with st.spinner("Đang phân tích thói quen mua sắm..."):
            matched_df = df[df["Pattern"].str.startswith(prefix_str, na=False)]
            
            # Bước 3: Trích xuất gợi ý
            if not matched_df.empty:
                suggestions = {}
                for idx, row in matched_df.iterrows():
                    pattern = row["Pattern"]
                    support = row["Support"]
                    
                    # Cắt chuỗi lấy phần nằm ngay sau tiền tố
                    remaining = pattern[len(prefix_str):].strip()
                    if remaining:
                        next_item_match = remaining.split(']')[0]
                        if next_item_match.startswith('['):
                            next_item = next_item_match[1:].strip() # Xóa dấu '[' và khoảng trắng thừa
                            
                            # Lưu lại support cao nhất của từng gợi ý
                            if next_item not in suggestions or support > suggestions[next_item]:
                                suggestions[next_item] = support
                
                # Sắp xếp danh sách gợi ý theo độ phổ biến giảm dần
                sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
                
                # Bước 4: Hiển thị dưới dạng Lưới (Grid)
                if sorted_suggestions:
                    st.success("Dựa trên giỏ hàng của bạn, những khách hàng khác cũng thường mua các sản phẩm sau:")
                    
                    # Hiển thị tối đa 9 gợi ý đẹp mắt trên 3 cột
                    cols = st.columns(3)
                    for i, (s_item, s_supp) in enumerate(sorted_suggestions[:9]):
                        with cols[i % 3]:
                            with st.container(border=True):
                                # Dùng UI Avatars tạo ảnh placeholder từ tên sản phẩm để giao diện trực quan hơn
                                img_url = f"https://ui-avatars.com/api/?name={s_item.replace(' ', '+')}&background=random&size=128&color=fff&font-size=0.33&bold=true"
                                st.image(img_url, use_container_width=True)
                                
                                st.markdown(f"**{s_item}**")
                                st.caption(f"🔥 Độ phổ biến: **{s_supp}** lượt mua cùng")
                                if st.button("Thêm vào giỏ", key=f"add_sugg_{i}", use_container_width=True):
                                    st.session_state.cart.append(s_item)
                                    st.toast(f"Đã thêm **{s_item}** vào giỏ!", icon="✅")
                                    st.rerun()
                else:
                    st.info("💡 Chưa có gợi ý phù hợp cho chuỗi sản phẩm này. Thử thêm món khác xem sao!")
            else:
                st.info("💡 Chưa có gợi ý phù hợp cho chuỗi sản phẩm này. Thử thêm món khác xem sao!")
else:
    st.info("👈 Hãy thêm sản phẩm vào giỏ để hệ thống phân tích và đưa ra gợi ý tự động.")
