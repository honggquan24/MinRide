# MinRide  
Hệ thống quản lý và tự động ghép cặp chuyến đi

Dự án mô phỏng hệ thống gọi xe, bao gồm: quản lý tài xế, khách hàng, chuyến đi và tính năng tự động ghép cặp.  
Được viết bằng Python và hỗ trợ giao diện trực quan thông qua Streamlit.

## Cấu trúc dự án

```
├── driver_manager.py       # Quản lý tài xế
├── customer_manager.py     # Quản lý khách hàng
├── find_driver_system.py   # Tìm tài xế theo vị trí và tiêu chí
├── ride.py                 # Quản lý chuyến đi (Ride & RideManagementSystem)
├── booking_system.py       # Đặt chuyến (BookingSystem)
├── auto_matching.py        # Tự động ghép cặp (AutoMatchingSystem)
├── undo_stack.py           # Lưu lịch sử thao tác (UndoStack)
├── main.py                 # Giao diện Streamlit / điểm chạy chính
├── rides.csv               # Dữ liệu chuyến đi
└── README.md
```

## Tính năng chính

- Quản lý tài xế và khách hàng: thêm, sửa, xóa, tra cứu nhanh (độ phức tạp tra cứu theo ID là $O(1)$ nhờ sử dụng `dict`).
- Tìm tài xế trong bán kính cho trước, hỗ trợ lọc và sắp xếp theo nhiều tiêu chí: khoảng cách, đánh giá, số chuyến, kinh nghiệm.
- Tự động ghép cặp khách hàng với tài xế rảnh gần nhất.
- Quản lý chuyến đi: lưu trữ thông tin chi tiết, đọc/ghi file CSV, truy vấn theo thời gian hoặc tài xế.
- Đặt, xác nhận hoặc hủy chuyến; tính toán giá dựa trên quãng đường.
- Lưu lịch sử thao tác người dùng để hỗ trợ chức năng undo.
- Giao diện người dùng đơn giản qua Streamlit.

## Công thức tính toán

Khoảng cách giữa hai điểm $(x_1, y_1)$ và $(x_2, y_2)$ được tính theo công thức Euclidean:

$$
\text{distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
$$

Giá chuyến đi được tính như sau:

$$
\text{fare} = (\text{pickup\_distance} + \text{trip\_distance}) \times \text{FARE\_RATE}
$$

với $\text{FARE\_RATE} = 12000$ VND/km (mặc định).

## Cách chạy chương trình

Chạy bằng terminal:
```bash
streamlit run .\main.py
```