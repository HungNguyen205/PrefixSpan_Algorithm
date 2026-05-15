import pandas as pd
import json
import os
import time

def preprocess_online_retail():
    start_time = time.time()
    
    # ========================================================
    # 1. THIẾT LẬP ĐƯỜNG DẪN TỰ ĐỘNG
    # ========================================================
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'Online Retail.xlsx')
    mapping_file = os.path.join(current_dir, 'item_mapping.json')
    output_file = os.path.join(current_dir, 'online_retail_clean.txt')

    if not os.path.exists(input_file):
        print(f"[LỖI] Không tìm thấy file gốc tại: {input_file}")
        return

    print("=> Bắt đầu quy trình tiền xử lý dữ liệu Online Retail...\n")
    
    # ========================================================
    # 2. ĐỌC DỮ LIỆU & THỐNG KÊ TRƯỚC LÀM SẠCH
    # ========================================================
    print("[1/5] Đang đọc dữ liệu từ Excel (Vui lòng đợi)...")
    df = pd.read_excel(input_file)
    
    stats_before = {
        'total_rows': len(df),
        'total_customers': df['CustomerID'].nunique(dropna=True),
        'total_invoices': df['InvoiceNo'].nunique(),
        'total_items': df['StockCode'].nunique()
    }

    # ========================================================
    # 3. LÀM SẠCH DỮ LIỆU (DATA CLEANING)
    # ========================================================
    print("[2/5] Đang làm sạch dữ liệu và loại bỏ nhiễu...")
    # Bỏ dòng không có khách hàng, bỏ đơn hủy (C)
    df = df.dropna(subset=['CustomerID'])
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    
    # Lọc Quantity và UnitPrice > 0 để tránh giao dịch rác (hàng tặng, lỗi kho...)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Dùng exact match (.isin) thay vì .contains() để không xóa nhầm mã sản phẩm thật
    non_product_codes = ['POST', 'D', 'M', 'PADS', 'DOT', 'CRUK', 'BANK CHARGES', 'AMAZONFEE']
    df['StockCode_clean'] = df['StockCode'].astype(str).str.strip().str.upper()
    df = df[~df['StockCode_clean'].isin(non_product_codes)]
    
    stats_after = {
        'total_rows': len(df),
        'total_customers': df['CustomerID'].nunique(),
        'total_invoices': df['InvoiceNo'].nunique(),
        'total_items': df['StockCode'].nunique()
    }

    # ========================================================
    # 4. ÁNH XẠ MÃ SẢN PHẨM SANG ID SỐ NGUYÊN & XUẤT JSON
    # ========================================================
    print("[3/5] Đang tạo từ điển ánh xạ ID -> Tên sản phẩm...")
    # Xử lý Description: Nếu trống thì lấy chính mã StockCode đắp vào
    df['Description'] = df['Description'].fillna(df['StockCode'].astype(str))
    stock_to_desc = df.groupby('StockCode')['Description'].first().to_dict()

    unique_items = df['StockCode'].unique()
    item_to_id = {item: idx + 1 for idx, item in enumerate(unique_items)}
    
    # Map sang Cột mới
    df['ItemID'] = df['StockCode'].map(item_to_id)

    # Lưu file JSON với tên sản phẩm
    id_to_name = {str(id_val): str(stock_to_desc.get(stock, stock)).strip() for stock, id_val in item_to_id.items()}
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(id_to_name, f, ensure_ascii=False, indent=4)

    # ========================================================
    # 5. SẮP XẾP & GOM NHÓM CHUỖI TUẦN TỰ
    # ========================================================
    print("[4/5] Đang sắp xếp thời gian & Gom nhóm chuỗi tuần tự...")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df = df.sort_values(by=['CustomerID', 'InvoiceDate'])

    # Lớp 1: Gom ItemID theo hóa đơn (Itemset) và loại bỏ trùng lặp trong 1 hóa đơn bằng set()
    invoice_groups = df.groupby(['CustomerID', 'InvoiceNo'])['ItemID'].apply(lambda x: sorted(list(set(x)))).reset_index()
    
    # Lớp 2: Gom Hóa đơn theo khách hàng (Sequence)
    customer_sequences = invoice_groups.groupby('CustomerID')['ItemID'].apply(list).tolist()

    # ========================================================
    # 6. ĐỊNH DẠNG & XUẤT FILE SPMF
    # ========================================================
    print("[5/5] Đang định dạng và xuất file chuẩn SPMF...")
    total_events = 0
    total_items = 0
    max_seq_len = 0

    # Nối chuỗi bằng List Comprehension để ghi file tốc độ cao
    with open(output_file, 'w') as f:
        for seq in customer_sequences:
            seq_len = len(seq)
            total_events += seq_len
            max_seq_len = max(max_seq_len, seq_len)
            
            for itemset in seq:
                total_items += len(itemset)
            
            # Format chuẩn: item1 item2 -1 item3 -1 -2
            seq_string = " ".join([" ".join(map(str, itemset)) + " -1" for itemset in seq]) + " -2\n"
            f.write(seq_string)

    execution_time = time.time() - start_time

    # ========================================================
    # 7. IN LOG BÁO CÁO TOÀN DIỆN LÊN TERMINAL
    # ========================================================
    print("\n" + "="*80)
    print(" BÁO CÁO TIỀN XỬ LÝ DỮ LIỆU SPMF - ONLINE RETAIL DATASET")
    print("="*80)
    
    print("\n[PHẦN 1] CÁC BƯỚC ĐÃ THỰC THI (PIPELINE):")
    print("  1. Đọc dữ liệu thô từ file Excel.")
    print("  2. Làm sạch dữ liệu (Xóa dòng thiếu CustomerID, bỏ đơn hủy 'C', lọc Quantity & UnitPrice > 0).")
    print("  3. Loại bỏ chính xác các mã phi sản phẩm (POST, M, D, DOT...) bằng .isin().")
    print("  4. Ánh xạ StockCode thành Integer ID (1, 2, 3...) và trích xuất Tên sản phẩm hợp lệ.")
    print("  5. Lưu từ điển ánh xạ {ID: Tên Sản Phẩm} ra file JSON.")
    print("  6. Sắp xếp dòng thời gian theo CustomerID và InvoiceDate.")
    print("  7. Gom nhóm lớp 1: Gộp các sản phẩm mua cùng lúc thành Itemset (đại diện bởi InvoiceNo).")
    print("  8. Gom nhóm lớp 2: Gộp các Itemset thành chuỗi tuần tự (Sequence) đại diện cho CustomerID.")
    print("  9. Xuất dữ liệu chuỗi ra file .txt theo đúng định dạng chuẩn của SPMF (-1 kết thúc hóa đơn, -2 kết thúc chuỗi).")

    print("\n[PHẦN 2] CÁC THUỘC TÍNH (COLUMNS) ĐÃ SỬ DỤNG:")
    print("  - CustomerID  : Dùng để làm sạch dữ liệu rỗng và Gom nhóm lớp 2 (Tạo Sequence).")
    print("  - InvoiceNo   : Dùng để lọc đơn hủy và Gom nhóm lớp 1 (Tạo Itemset).")
    print("  - InvoiceDate : Dùng để sắp xếp đúng trình tự lịch sử mua hàng của khách.")
    print("  - Quantity    : Dùng làm điều kiện lọc (Quantity > 0) để bỏ giao dịch âm/lỗi.")
    print("  - UnitPrice   : Dùng làm điều kiện lọc (UnitPrice > 0) để bỏ hàng tặng miễn phí.")
    print("  - StockCode   : Dùng để lọc mã phi sản phẩm và tạo ID số nguyên.")
    print("  - Description : Dùng để lấy tên sản phẩm lưu vào từ điển JSON.")

    print("\n[PHẦN 3] THỐNG KÊ CHI TIẾT TRƯỚC VÀ SAU KHI LÀM SẠCH:")
    print(f"  {'-'*75}")
    print(f"  | {'Chỉ số':<26} | {'Trước (Thô)':<13} | {'Sau (Sạch)':<12} | {'Bị loại bỏ':<10} |")
    print(f"  {'-'*75}")
    print(f"  | {'Tổng số dòng (Rows)':<26} | {stats_before['total_rows']:<13,} | {stats_after['total_rows']:<12,} | {stats_before['total_rows'] - stats_after['total_rows']:,} |")
    print(f"  | {'Tổng số khách hàng (Users)':<26} | {stats_before['total_customers']:<13,} | {stats_after['total_customers']:<12,} | {stats_before['total_customers'] - stats_after['total_customers']:,} |")
    print(f"  | {'Tổng số hóa đơn (Invoices)':<26} | {stats_before['total_invoices']:<13,} | {stats_after['total_invoices']:<12,} | {stats_before['total_invoices'] - stats_after['total_invoices']:,} |")
    print(f"  | {'Tổng số mặt hàng (Items)':<26} | {stats_before['total_items']:<13,} | {stats_after['total_items']:<12,} | {stats_before['total_items'] - stats_after['total_items']:,} |")
    print(f"  {'-'*75}")

    print("\n[PHẦN 4] THỐNG KÊ HÀNH VI CHUỖI CỦA TẬP DỮ LIỆU ĐẦU RA:")
    print(f"  - Chuỗi dài nhất (Max Invoices/Khách)  : {max_seq_len:,} hóa đơn")
    print(f"  - Trung bình hóa đơn / 1 khách hàng    : {(total_events / len(customer_sequences)):.2f} hóa đơn")
    print(f"  - Trung bình mặt hàng / 1 hóa đơn      : {(total_items / total_events):.2f} mặt hàng")

    print("\n[PHẦN 5] KẾT QUẢ ĐẦU RA (OUTPUT FILES):")
    print(f"  [1] File Từ điển JSON  : {mapping_file}")
    print(f"  [2] File Chuỗi SPMF TXT: {output_file}")
    print(f"\n=> TẤT CẢ ĐÃ HOÀN TẤT TRONG {execution_time:.2f} GIÂY!")
    print("="*80 + "\n")

if __name__ == "__main__":
    preprocess_online_retail()