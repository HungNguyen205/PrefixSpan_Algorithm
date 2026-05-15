import os
from prefixspan_algo import (
    read_spmf_file,
    load_item_dictionary,
    run_prefixspan,
    save_patterns_spmf,
    save_patterns_mapped
)

def main():
    # ========================================================
    # 1. CẤU HÌNH ĐƯỜNG DẪN
    # ========================================================
    # Lấy thư mục gốc hiện tại chứa file main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Định nghĩa các folder con (data và result)
    data_dir = os.path.join(current_dir, 'data')
    result_dir = os.path.join(current_dir, 'result')
    
    # Tự động tạo folder 'result' nếu nó chưa tồn tại trên máy
    os.makedirs(result_dir, exist_ok=True)
    
    # Files đầu vào (sẽ được đọc từ folder 'data')
    input_spmf_file = os.path.join(data_dir, 'online_retail_clean.txt')
    input_dict_file = os.path.join(data_dir, 'item_mapping.json')
    
    # Files đầu ra (sẽ được xuất vào folder 'result')
    output_spmf_file = os.path.join(result_dir, 'output_online_retail_0.5.txt')
    output_mapped_file = os.path.join(result_dir, 'output_online_retail_mapped_0.5.txt')
    
    # ========================================================
    # 2. CẤU HÌNH THUẬT TOÁN
    # ========================================================
    # MIN_SUP tính theo tỷ lệ phần trăm (%)
    # Ví dụ: 1.0 nghĩa là mẫu phải xuất hiện ở ít nhất 1% tổng số khách hàng
    MIN_SUP_PERCENT = 0.5
    
    print("=" * 60)
    print(" BẮT ĐẦU CHẠY THUẬT TOÁN PREFIXSPAN")
    print("=" * 60)
    
    if not os.path.exists(input_spmf_file):
        print(f"[!] Lỗi: Không tìm thấy file dữ liệu tại {input_spmf_file}")
        print("    Vui lòng kiểm tra lại xem file đã nằm trong folder 'data' chưa.")
        return

    # ========================================================
    # 3. ĐỌC DỮ LIỆU & TỪ ĐIỂN
    # ========================================================
    print(f"[1/4] Đang nạp cơ sở dữ liệu SPMF từ folder 'data'...")
    database = read_spmf_file(input_spmf_file)
    
    print(f"[2/4] Đang nạp từ điển ánh xạ sản phẩm từ folder 'data'...")
    item_mapping = load_item_dictionary(input_dict_file)
    
    # ========================================================
    # 4. THỰC THI PREFIXSPAN
    # ========================================================
    print(f"\n[3/4] Đang khai phá mẫu tuần tự (Vui lòng đợi)...")
    results, run_time = run_prefixspan(database, MIN_SUP_PERCENT)
    
    print(f"      -> Tìm thấy tổng cộng {len(results):,} mẫu phổ biến!")
    print(f"      -> Thời gian chạy thuật toán: {run_time:.4f} giây.")
    
    # ========================================================
    # 5. XUẤT KẾT QUẢ
    # ========================================================
    print(f"\n[4/4] Đang xuất kết quả ra folder 'result'...")
    
    # File 1: Định dạng chuẩn SPMF
    save_patterns_spmf(results, output_spmf_file)
    print(f"  + Đã lưu file chuẩn SPMF: {output_spmf_file}")
    
    # File 2: Định dạng đọc được bằng chữ (đã dịch ngược)
    save_patterns_mapped(results, output_mapped_file, item_mapping)
    print(f"  + Đã lưu file dịch ngược Tên SP: {output_mapped_file}")
    
    print("=" * 60)
    print(" HOÀN TẤT THÀNH CÔNG!")
    print("=" * 60)

if __name__ == "__main__":
    main()