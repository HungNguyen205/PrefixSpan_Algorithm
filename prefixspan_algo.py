import time
import json
from collections import defaultdict

# =====================================================================
# PHẦN 1: CÁC HÀM XỬ LÝ I/O (ĐỌC/GHI FILE)
# =====================================================================

def read_spmf_file(file_path):
    """
    Đọc dữ liệu từ file văn bản theo định dạng chuẩn của SPMF.
    
    Trong định dạng SPMF:
      - Các item (mặt hàng) trong cùng một itemset (hóa đơn) được cách nhau bởi khoảng trắng.
      - Kết thúc một itemset được đánh dấu bằng '-1'.
      - Kết thúc một sequence (chuỗi khách hàng) được đánh dấu bằng '-2'.
    
    Input:
        file_path (str): Đường dẫn tuyệt đối hoặc tương đối tới file .txt (định dạng SPMF).
    
    Output:
        list: Một mảng 2 chiều chứa các chuỗi (sequences). Mỗi chuỗi là một list chứa 
              các itemset (list of lists). Ví dụ: [[[1, 2], [3]], [[1], [2, 3]]]
    """
    database = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Bỏ qua các dòng trống hoặc dòng comment (bắt đầu bằng @ hoặc #)
                if not line or line.startswith("@") or line.startswith("#"):
                    continue
                
                # Loại bỏ ký tự -2 ở cuối và cắt chuỗi thành các itemset bởi -1
                parts = line.replace(' -2', '').split(' -1')
                sequence = []
                for part in parts:
                    items = part.strip().split()
                    if items:
                        # Chuyển đổi các item từ string sang integer
                        itemset = [int(item) for item in items]
                        sequence.append(itemset)
                
                if sequence:
                    database.append(sequence)
        return database
    except FileNotFoundError:
        print(f"[!] Lỗi: Không tìm thấy file dữ liệu tại {file_path}")
        return []


def load_item_dictionary(dict_path):
    """
    Đọc từ điển ánh xạ từ ID (số nguyên) sang Tên sản phẩm (chuỗi) từ file JSON.
    
    Input:
        dict_path (str): Đường dẫn tới file .json chứa từ điển.
        
    Output:
        dict: Từ điển dạng {ID_số_nguyên: "Tên sản phẩm"}. Trả về dict rỗng nếu lỗi.
    """
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            str_dict = json.load(f)
            # Chuyển đổi key từ chuỗi (do JSON mặc định) sang số nguyên để map dễ dàng
            return {int(k): v for k, v in str_dict.items()}
    except FileNotFoundError:
        print(f"[!] Cảnh báo: Không tìm thấy file từ điển tại {dict_path}. Kết quả sẽ giữ nguyên ID.")
        return {}


def save_patterns_spmf(results, output_path):
    """
    Lưu các mẫu tuần tự phổ biến tìm được dưới định dạng chuẩn của SPMF.
    
    Input:
        results (list): Danh sách các tuple, mỗi tuple gồm (pattern, support_count).
        output_path (str): Đường dẫn lưu file .txt.
        
    Output:
        None. Hàm sẽ ghi trực tiếp ra file và thêm '#SUP: count' ở cuối.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for pattern, support in results:
            seq_str = ""
            for itemset in pattern:
                seq_str += " ".join(map(str, itemset)) + " -1 "
            # Thêm -2 và thông tin độ hỗ trợ
            seq_str += f"-2 #SUP: {support}\n"
            f.write(seq_str)


def save_patterns_mapped(results, output_path, mapping_dict):
    """
    Lưu các mẫu tuần tự phổ biến dưới dạng văn bản có thể đọc được (Human-readable),
    bằng cách ánh xạ từ ID số nguyên sang Tên sản phẩm thực tế.
    
    Input:
        results (list): Danh sách các tuple (pattern, support_count).
        output_path (str): Đường dẫn lưu file .txt.
        mapping_dict (dict): Từ điển ánh xạ {ID: "Tên SP"}.
        
    Output:
        None.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for pattern, support in results:
            seq_str = ""
            for itemset in pattern:
                # Dịch từng item. Nếu ID không có trong từ điển, giữ nguyên số ID đó
                mapped_itemset = [mapping_dict.get(item, str(item)) for item in itemset]
                seq_str += "[" + ", ".join(mapped_itemset) + "] -> "
            
            # Xóa chuỗi " -> " bị dư ở cuối cùng
            seq_str = seq_str[:-4]
            seq_str += f" | (Support: {support})\n"
            f.write(seq_str)


# =====================================================================
# PHẦN 2: THUẬT TOÁN PREFIXSPAN CỐT LÕI
# =====================================================================

def get_frequent_items_S(DB, min_sup_count):
    """
    Quét cơ sở dữ liệu chiếu để tìm các mặt hàng phổ biến cho S-Extension 
    (Tức là tạo ra một sự kiện/hóa đơn mới nối tiếp vào chuỗi).
    
    Input:
        DB (list): Cơ sở dữ liệu chiếu (Projected Database) hiện tại.
        min_sup_count (int): Số lượng chuỗi hỗ trợ tối thiểu.
        
    Output:
        set: Tập hợp các item phổ biến (đạt min_sup) cho S-Extension.
    """
    counts = defaultdict(int)
    for partial, remaining in DB:
        seen = set()
        # Đối với S-Extension, chúng ta CHỈ đếm các item xuất hiện trong tương lai (remaining)
        for iset in remaining:
            for item in iset:
                if item not in seen:
                    seen.add(item)
                    counts[item] += 1
                    
    return {item for item, count in counts.items() if count >= min_sup_count}


def get_frequent_items_I(DB, min_sup_count, last_item):
    """
    Quét cơ sở dữ liệu chiếu để tìm các mặt hàng phổ biến cho I-Extension 
    (Tức là thêm mặt hàng vào cùng một sự kiện/hóa đơn hiện tại).
    
    Input:
        DB (list): Cơ sở dữ liệu chiếu hiện tại.
        min_sup_count (int): Số lượng chuỗi hỗ trợ tối thiểu.
        last_item (int): Hạng mục cuối cùng trong mẫu tiền tố hiện tại.
        
    Output:
        set: Tập hợp các item phổ biến (> last_item) cho I-Extension.
    """
    counts = defaultdict(int)
    for partial, remaining in DB:
        seen = set()
        # Đối với I-Extension, chúng ta đếm các item nằm cùng sự kiện hiện hành (partial)
        for item in partial:
            # Điều kiện item > last_item đảm bảo không bị trùng lặp tổ hợp (VD: có ab thì không cần ba)
            if item > last_item and item not in seen:
                seen.add(item)
                counts[item] += 1
                
    return {item for item, count in counts.items() if count >= min_sup_count}


def project_S(DB, item):
    """
    Tạo cơ sở dữ liệu chiếu mới dựa trên một item dùng cho S-Extension.
    
    Input:
        DB (list): CSDL chiếu hiện tại.
        item (int): Hạng mục dùng làm điểm cắt.
        
    Output:
        list: CSDL chiếu mới (Các phần còn lại của chuỗi sau khi cắt tại 'item').
    """
    new_DB = []
    for partial, remaining in DB:
        found = False
        # Tìm sự xuất hiện ĐẦU TIÊN của 'item' trong phần remaining
        for idx, iset in enumerate(remaining):
            for i, x in enumerate(iset):
                if x == item:
                    # Cắt chuỗi từ vị trí i+1 của itemset hiện tại
                    new_DB.append((iset[i+1:], remaining[idx+1:]))
                    found = True
                    break
            if found: break
    return new_DB


def project_I(DB, item):
    """
    Tạo cơ sở dữ liệu chiếu mới dựa trên một item dùng cho I-Extension.
    
    Input:
        DB (list): CSDL chiếu hiện tại.
        item (int): Hạng mục dùng làm điểm cắt.
        
    Output:
        list: CSDL chiếu mới.
    """
    new_DB = []
    for partial, remaining in DB:
        # I-Extension chỉ tìm 'item' trong phần partial (cùng sự kiện)
        for i, x in enumerate(partial):
            if x == item:
                new_DB.append((partial[i+1:], remaining))
                break
    return new_DB


def mine_prefixspan(DB, min_sup_count, prefix=None, results=None):
    """
    Hàm đệ quy chính thực thi khai phá mẫu tuần tự PrefixSpan.
    
    Input:
        DB (list): Cơ sở dữ liệu chiếu ở độ sâu hiện tại.
        min_sup_count (int): Hỗ trợ tối thiểu tuyệt đối.
        prefix (list, optional): Mẫu tiền tố hiện hành đang xét. Khởi tạo là list rỗng.
        results (list, optional): Biến lưu trữ kết quả. Khởi tạo là list rỗng.
        
    Output:
        list: Danh sách chứa tất cả các mẫu tìm được dưới dạng tuple: (pattern_list, support).
    """
    if prefix is None: prefix = []
    if results is None: results = []
        
    # --- BƯỚC 1: XỬ LÝ S-EXTENSION ---
    freq_S = get_frequent_items_S(DB, min_sup_count)
    for item in sorted(list(freq_S)):
        # Thêm item như một sự kiện mới: [..., [item]]
        new_prefix = prefix + [[item]]
        new_DB = project_S(DB, item)
        support_count = len(new_DB)
        
        # Lưu kết quả và tiếp tục đệ quy
        results.append((new_prefix, support_count))
        mine_prefixspan(new_DB, min_sup_count, new_prefix, results)
        
    # --- BƯỚC 2: XỬ LÝ I-EXTENSION ---
    if prefix:
        # Lấy item cuối cùng của sự kiện cuối cùng trong tiền tố
        last_item = prefix[-1][-1]
        freq_I = get_frequent_items_I(DB, min_sup_count, last_item)
        
        for item in sorted(list(freq_I)):
            # Clone prefix hiện tại (phải copy sâu để tránh tham chiếu bộ nhớ)
            new_prefix = [list(iset) for iset in prefix]
            # Thêm item vào cùng sự kiện cuối cùng
            new_prefix[-1].append(item)
            
            new_DB = project_I(DB, item)
            support_count = len(new_DB)
            
            # Lưu kết quả và đệ quy
            results.append((new_prefix, support_count))
            mine_prefixspan(new_DB, min_sup_count, new_prefix, results)
            
    return results


def run_prefixspan(D, min_sup_percent):
    """
    Hàm khởi tạo chạy thuật toán. Nhận đầu vào là Database và MinSup theo tỷ lệ %.
    
    Input:
        D (list): Cơ sở dữ liệu chuỗi nguyên bản.
        min_sup_percent (float): Độ hỗ trợ tối thiểu tính bằng phần trăm (ví dụ: 1.5%).
        
    Output:
        tuple: (results, execution_time). Trong đó results là danh sách kết quả,
               execution_time là thời gian chạy (giây).
    """
    total_seqs = len(D)
    
    # Tính toán Absolute Support (Số lượng chuỗi tối thiểu) từ tỷ lệ phần trăm
    min_sup_ratio = min_sup_percent / 100.0
    abs_min_sup = max(1, int(min_sup_ratio * total_seqs))
    
    print(f"[*] Tổng số chuỗi trong CSDL (n) : {total_seqs}")
    print(f"[*] Ngưỡng min_sup ({min_sup_percent}%)     : >= {abs_min_sup} chuỗi")
    
    # Khởi tạo CSDL chiếu ban đầu với partial rỗng
    initial_DB = []
    for S in D:
        # Đảm bảo các itemset bên trong chuỗi đều được sắp xếp (yêu cầu của I-Extension)
        sorted_S = [sorted(list(iset)) for iset in S]
        initial_DB.append(([], sorted_S))
        
    start_time = time.time()
    # Chạy hàm đệ quy
    results = mine_prefixspan(initial_DB, abs_min_sup)
    end_time = time.time()
    
    return results, (end_time - start_time)