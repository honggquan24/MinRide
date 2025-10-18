import streamlit as st
import pandas as pd
from datetime import datetime
from driver import *
from customer import *
from ride import *
from booking import *
from find_driver import *
from auto_matching import *
from undo_stack import *
from session_state import *
from theme import *

# MAIN APP
st.set_page_config(
    page_title="MinRide - Hệ thống Quản lý Đặt Xe",
    layout="wide"
)

st.markdown(get_css(THEME_DARKMODE), unsafe_allow_html=True)

st.markdown("""
            <div style="text-align: center;">
                <h1>Hệ thống Quản lý Đặt Xe Công Nghệ MinRide</h1>
            </div>
            """, unsafe_allow_html=True)
st.markdown("<br></br>", unsafe_allow_html=True)

# KHỞI TẠO SESSION STATE
session_state_manager = ManageSessionState()
driver_manager = session_state_manager.get_driver_manager()
customer_manager = session_state_manager.get_customer_manager()
ride_manager = session_state_manager.get_ride_manager()

# Undo Stack
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = UndoStack(limit=10)
undo_stack = st.session_state.undo_stack

# Hệ thống chính
if "find_driver_system" not in st.session_state:
    st.session_state.find_driver_system = FindDriverSystem(driver_manager, customer_manager)
if "booking_system" not in st.session_state:
    st.session_state.booking_system = BookingSystem(driver_manager, customer_manager, ride_manager)
if "auto_matching_system" not in st.session_state:
    st.session_state.auto_matching_system = AutoMatchingSystem(driver_manager, customer_manager, st.session_state.booking_system)

find_driver_system = st.session_state.find_driver_system
booking_system = st.session_state.booking_system
auto_matching_system = st.session_state.auto_matching_system

# SIDEBAR
st.sidebar.header("Hệ thống quản lý")
if st.sidebar.button("↩ Hoàn tác", use_container_width=True):
    session_state_manager.undo()

# ==================== MAIN TABS ====================
# Tạo các tab chính
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Quản lý tài xế", 
    "Quản lý khách hàng", 
    "Lịch sử chuyến đi", 
    "Tìm tài xế", 
    "Đặt xe",
    "Tự động ghép cặp"
])

# 1. Quản lý Tài xế
with tab1:        
    # THÊM TÀI XẾ MỚI
    st.subheader("THÊM TÀI XẾ MỚI")
    
    with st.form("add_driver_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Tên tài xế", value="Nguyễn Văn A")
            rating = st.number_input("Rating", 0.0, 5.0, 4.0, 0.1, help="Từ 0.0 đến 5.0")
        
        with col2:
            x = st.number_input("X", value=10.0, format="%.2f")
            y = st.number_input("Y", value=20.0, format="%.2f")
        
        submitted = st.form_submit_button("Thêm tài xế", type="primary", use_container_width=True)
        
        if submitted:
            if name.strip():
                session_state_manager.save_state()
                new_driver = driver_manager.add_driver(name, rating, x, y)
                st.success(f"Đã thêm tài xế: **{new_driver.name}** (ID: {new_driver.id})")
                st.rerun()
            else:
                st.error("Vui lòng nhập tên tài xế!")
    
    
    
    st.subheader("HIỂN THỊ TOP K TÀI XẾ")

    # --- Tùy chọn sắp xếp ---
    col1, col2 = st.columns([2, 2])
    with col1:
        sort_order = st.radio(
            "Sắp xếp theo rating",
            ["Giảm dần (Cao → Thấp)", "Tăng dần (Thấp → Cao)"],
            horizontal=True,
            key="sort_order_radio"
        )
    with col2:
        position = st.radio("Vị trí hiển thị", ["Đầu danh sách", "Cuối danh sách"], horizontal=True)

    # --- Nhập K & nút hiển thị ---
    col1, col2 = st.columns([3, 1])
    with col1:
        k = st.number_input(
            "Nhập K",
            min_value=1,
            max_value=len(driver_manager.drivers) or 1,
            value=min(5, len(driver_manager.drivers)) if driver_manager.drivers else 1,
            key="top_k_drivers"
        )
    with col2:
        show_top_k = st.button("Hiển thị", use_container_width=True, key="show_top_k_btn")

    # --- Xử lý hiển thị ---
    if show_top_k:
        session_state_manager.save_state()
        ascending = (sort_order == "Tăng dần (Thấp → Cao)")
        driver_manager.sort_by_rating(ascending=ascending)

        result = driver_manager.display_top_k(k, from_top=(position == "Đầu danh sách"))
        if result:
            st.write(f"**Hiển thị {len(result)} tài xế (đã sắp xếp {sort_order.lower()}):**")
            import pandas as pd
            df_top = pd.DataFrame(result).rename(columns={
                'ID': 'ID', 'Ten': 'Tên', 'Rating': 'Đánh giá', 'X': 'X', 'Y': 'Y'
            })
            st.dataframe(df_top, use_container_width=True, hide_index=True)

    
    
    # TÌM KIẾM TÀI XẾ 
    st.subheader("TÌM KIẾM TÀI XẾ")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_keyword = st.text_input(
            "Nhập ID hoặc Tên", 
            placeholder="VD: 1 hoặc Nguyen Van A",
            key="search_driver_input"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        search_btn = st.button("Tìm kiếm", use_container_width=True, key="search_driver_btn")
    
    if search_btn and search_keyword:
        results = driver_manager.search_driver(search_keyword)
        if results:
            st.success(f"Tìm thấy **{len(results)}** kết quả:")
            
            import pandas as pd
            df_search = pd.DataFrame(results)
            df_search = df_search.rename(columns={
                'ID': 'ID', 'Ten': 'Tên', 'Rating': 'Đánh giá',
                'X': 'X', 'Y': 'Y',
            })
            
            st.dataframe(df_search, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Không tìm thấy: **{search_keyword}**")
    
    
    
    # CẬP NHẬT TÀI XẾ 
    st.subheader("CẬP NHẬT TÀI XẾ")
    
    with st.form("update_driver_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            update_id = st.number_input("ID tài xế cần cập nhật *", min_value=1, step=1, key="update_id")
            new_name = st.text_input("Tên mới", placeholder="Để trống nếu không đổi")
            new_rating = st.number_input("Rating mới", 0.0, 5.0, 4.0, 0.1)
        
        with col2:
            new_x = st.number_input("X mới", value=10.8, format="%.2f")
            new_y = st.number_input("Y mới", value=16.7, format="%.2f")
            update_note = st.text_input("Ghi chú", placeholder="Lý do cập nhật...")
        
        submitted = st.form_submit_button("Cập nhật", type="primary", use_container_width=True)
        
        if submitted:
            session_state_manager.save_state()
            success = driver_manager.update_driver(
                update_id,
                new_name=new_name if new_name else None,
                new_rating=new_rating,
                new_x=new_x,
                new_y=new_y
            )
            if success:
                st.success(f"Đã cập nhật tài xế ID: **{update_id}**")
                st.rerun()
            else:
                st.error(f"Không tìm thấy tài xế ID: **{update_id}**")
    
    
    
    # XÓA TÀI XẾ 
    st.subheader("XÓA TÀI XẾ")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        delete_id = st.number_input(
            "ID tài xế cần xóa", 
            min_value=1, 
            step=1, 
            key="delete_id",
            help="Hành động này không thể hoàn tác!"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        
        # Hiển thị thông tin tài xế trước khi xóa
        if delete_id in driver_manager.id_index:
            driver_to_delete = driver_manager.id_index[delete_id]
            st.info(f"Sẽ xóa: **{driver_to_delete.name}**")
        
        delete_btn = st.button("Xóa", type="secondary", use_container_width=True, key="delete_driver_btn")
    
    if delete_btn:
        # Xác nhận trước khi xóa
        if delete_id in driver_manager.id_index:
            driver_name = driver_manager.id_index[delete_id].name
            session_state_manager.save_state()
            success = driver_manager.delete_driver(delete_id)
            if success:
                st.success(f"Đã xóa tài xế: **{driver_name}** (ID: {delete_id})")
                st.rerun()
        else:
            st.error(f"Không tìm thấy tài xế ID: **{delete_id}**")
    
    

# 2. Quản lý Khách hàng
with tab2:
    # --- THÊM KHÁCH HÀNG MỚI ---
    st.subheader("THÊM KHÁCH HÀNG MỚI")

    with st.form("add_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Tên khách hàng", value="Nguyễn Thị B")
            location = st.text_input("Quận", value="Q1")
        with col2:
            x = st.number_input("X", value=10.80, format="%.2f")
            y = st.number_input("Y", value=8.70, format="%.2f")

        submitted = st.form_submit_button("Thêm khách hàng", type="primary", use_container_width=True)

        if submitted:
            if name.strip() and location.strip():
                session_state_manager.save_state()
                new_customer = customer_manager.add_customer(name, location, x, y)
                st.success(f"Đã thêm khách hàng: **{new_customer.name}** (ID: {new_customer.id})")
                st.rerun()
            else:
                st.error("Vui lòng nhập đầy đủ thông tin!")

    

    # --- HIỂN THỊ TOP K KHÁCH HÀNG ---
    st.subheader("HIỂN THỊ TOP K KHÁCH HÀNG")

    col1, col2 = st.columns([3, 1])
    with col1:
        k = st.number_input(
            "Nhập K",
            min_value=1,
            max_value=len(customer_manager.customers) or 1,
            value=min(5, len(customer_manager.customers)) if customer_manager.customers else 1,
            key="top_k_customers"
        )
    with col2:
        position = st.radio("Vị trí hiển thị", ["Đầu danh sách", "Cuối danh sách"], horizontal=True, key= "position")

    show_top_k = st.button("Hiển thị", use_container_width=True, key="show_top_k_customer_btn")

    if show_top_k:
        result = customer_manager.top_k_customers(k, from_top=(position == "Đầu danh sách"))
        if result:
            st.write(f"**Hiển thị {len(result)} khách hàng ở {position.lower()} danh sách:**")
            df_top = pd.DataFrame(result).rename(columns={
                "ID": "ID", "Ten": "Tên", "Quan": "Quận", "X": "X", "Y": "Y"
            })
            st.dataframe(df_top, use_container_width=True, hide_index=True)
        else:
            st.warning("Không có dữ liệu để hiển thị.")

    

    # --- TÌM KIẾM KHÁCH HÀNG ---
    st.subheader("TÌM KIẾM KHÁCH HÀNG")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_keyword = st.text_input(
            "Nhập ID hoặc Tên",
            placeholder="VD: 1 hoặc Nguyễn Thị B",
            key="search_customer_input"
        )
    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("Tìm kiếm", use_container_width=True, key="search_customer_btn")

    if search_btn and search_keyword:
        results = customer_manager.search_customer(search_keyword)
        if results:
            st.success(f"Tìm thấy **{len(results)}** kết quả:")
            df_search = pd.DataFrame(results).rename(columns={
                "ID": "ID", "Ten": "Tên", "Quan": "Quận", "X": "X", "Y": "Y"
            })
            st.dataframe(df_search, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Không tìm thấy: **{search_keyword}**")

    

    # --- CẬP NHẬT KHÁCH HÀNG ---
    st.subheader("CẬP NHẬT KHÁCH HÀNG")

    with st.form("update_customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            update_id = st.number_input("ID khách hàng cần cập nhật *", min_value=1, step=1, key="update_customer_id")
            new_name = st.text_input("Tên mới", placeholder="Để trống nếu không đổi")
            new_location = st.text_input("Quận mới", placeholder="Để trống nếu không đổi")
        with col2:
            new_x = st.number_input("X mới", value=10.8, format="%.2f")
            new_y = st.number_input("Y mới", value=106.7, format="%.2f")
            update_note = st.text_input("Ghi chú", placeholder="Lý do cập nhật...")

        submitted = st.form_submit_button("Cập nhật", type="primary", use_container_width=True)

        if submitted:
            session_state_manager.save_state()
            success = customer_manager.update_customer(
                update_id,
                name=new_name if new_name else None,
                location=new_location if new_location else None,
                x=new_x,
                y=new_y
            )
            if success:
                st.success(f"Đã cập nhật khách hàng ID: **{update_id}**")
                st.rerun()
            else:
                st.error(f"Không tìm thấy khách hàng ID: **{update_id}**")

    

    # --- XÓA KHÁCH HÀNG ---
    st.subheader("XÓA KHÁCH HÀNG")

    col1, col2 = st.columns([2, 1])
    with col1:
        delete_id = st.number_input(
            "ID khách hàng cần xóa",
            min_value=1,
            step=1,
            key="delete_customer_id",
            help="Hành động này không thể hoàn tác!"
        )
    with col2:
        st.write("")
        st.write("")
        if delete_id in customer_manager.customers:
            customer_to_delete = customer_manager.customers[delete_id]
            st.info(f"Sẽ xóa: **{customer_to_delete.name}**")
        delete_btn = st.button("Xóa", type="secondary", use_container_width=True, key="delete_customer_btn")

    if delete_btn:
        if delete_id in customer_manager.customers:
            customer_name = customer_manager.customers[delete_id].name
            session_state_manager.save_state()
            success = customer_manager.delete_customer(delete_id)
            if success:
                st.success(f"Đã xóa khách hàng: **{customer_name}** (ID: {delete_id})")
                st.rerun()
        else:
            st.error(f"Không tìm thấy khách hàng ID: **{delete_id}**")

    

    # --- LIỆT KÊ KHÁCH HÀNG THEO QUẬN ---
    st.subheader("LIỆT KÊ KHÁCH HÀNG THEO QUẬN")

    col1, col2 = st.columns([3, 1])
    with col1:
        location_search = st.text_input("Nhập tên quận", placeholder="VD: Q7, Q9, Q1...", key="location_search_input")
    with col2:
        st.write("")
        st.write("")
        search_loc_btn = st.button("Tìm kiếm theo Quận", use_container_width=True, key="search_location_btn")

    if search_loc_btn and location_search:
        results, total = customer_manager.list_by_location(location_search, limit=10)
        if results:
            st.write(f"**Tổng số khách hàng tại {location_search}: {total}**")
            df_location = pd.DataFrame(results).rename(columns={
                "ID": "ID", "Ten": "Tên", "Quan": "Quận", "X": "X", "Y": "Y"
            })
            st.dataframe(df_location, use_container_width=True, hide_index=True)

            if total > 10 and st.button("Xem thêm", key="show_more_customers"):
                all_results, _ = customer_manager.list_by_location(location_search, limit=None)
                st.write(f"**Tất cả khách hàng tại {location_search}:**")
                df_all = pd.DataFrame(all_results).rename(columns={
                    "ID": "ID", "Ten": "Tên", "Quan": "Quận", "X": "X", "Y": "Y"
                })
                st.dataframe(df_all, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Không tìm thấy khách hàng tại: **{location_search}**")

# 3. LỊCH SỬ CHUYẾN ĐI
with tab3:
    st.subheader("HIỂN THỊ TOÀN BỘ CHUYẾN ĐI")

    if ride_manager.rides:
        # --- Tùy chọn sắp xếp theo thời gian ---
        sort_order = st.radio(
            "Sắp xếp theo thời gian",
            ["Mới nhất", "Cũ nhất"],
            horizontal=True,
            key="ride_sort_order"
        )

        # --- Lấy dữ liệu & sắp xếp ---
        rides = ride_manager.get_all_rides()
        rides_sorted = sorted(
            rides,
            key=lambda x: datetime.strptime(x["StartTime"], "%Y-%m-%d %H:%M:%S"),
            reverse=(sort_order == "Mới nhất")
        )

        # --- Hiển thị ---
        df_all = pd.DataFrame(rides_sorted).rename(columns={
            "RideID": "Mã chuyến",
            "CustomerID": "Khách hàng (ID)",
            "DriverID": "Tài xế (ID)",
            "Distance": "Quãng đường (km)",
            "Fare": "Chi phí (VND)",
            "StartTime": "Thời gian bắt đầu",
            "EndTime": "Thời gian kết thúc"
        })

        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.caption(f"Đang hiển thị {len(df_all)} chuyến đi – sắp xếp theo **{sort_order.lower()}**.")
    else:
        st.info("Chưa có chuyến đi nào trong hệ thống.")

    

# 4. TÌM TÀI XẾ PHÙ HỢP
with tab4:
    # --- THÔNG TIN TÌM KIẾM ---
    st.subheader("THÔNG TIN TÌM KIẾM")
    col1, col2 = st.columns(2)
    with col1:
        customer_id = st.number_input("Nhập ID Khách hàng", min_value=1, step=1, key="find_customer_id")
        radius = st.number_input("Bán kính tìm kiếm (km)", min_value=0.1, max_value=100.0, value=5.0, step=0.5)
    with col2:
        top_k = st.number_input("Hiển thị Top K tài xế gần nhất", min_value=1, max_value=50, value=5, step=1)

    

    # --- TIÊU CHÍ SẮP XẾP ---
    st.subheader("TIÊU CHÍ SẮP XẾP")
    col1, col2 = st.columns(2)
    with col1:
        sort_distance = st.radio("Khoảng cách", ["Tăng dần", "Giảm dần"], horizontal=True, key="sort_distance")
    with col2:
        sort_rating = st.radio("Đánh giá", ["Giảm dần", "Tăng dần"], horizontal=True, key="sort_rating")

    # Quy định thứ tự sắp xếp
    sort_priority = [
        "distance" if sort_distance == "Tăng dần" else "-distance",
        "-rating" if sort_rating == "Giảm dần" else "rating",
        "-trips",
        "-experience"
    ]

    

    # --- TÌM KIẾM TÀI XẾ ---
    if st.button("TÌM KIẾM TÀI XẾ", type="primary", use_container_width=True):
        results, error = find_driver_system.find_drivers_within_radius(
            customer_id=customer_id,
            radius=radius,
            sort_priority=sort_priority,
            top_k=top_k
        )

        if error:
            st.error(error)
        elif not results:
            st.warning("Không tìm thấy tài xế nào trong phạm vi yêu cầu.")
        else:
            st.success(f"Tìm thấy {len(results)} tài xế phù hợp!")

            # --- KẾT QUẢ TÌM KIẾM ---
            st.subheader("KẾT QUẢ TÌM KIẾM")

            # Thông tin khách hàng
            customer = customer_manager.customers[customer_id]
            st.info(
                f"Khách hàng: **{customer.name}** (ID: {customer.id}) – "
                f"Vị trí: ({customer.x:.2f}, {customer.y:.2f})"
            )

            import pandas as pd
            df_results = pd.DataFrame(results).rename(columns={
                "ID": "ID",
                "Ten": "Tên",
                "Distance": "Khoảng cách (km)",
                "Rating": "Đánh giá",
                "Trips": "Số chuyến",
                "Experience": "Kinh nghiệm (năm)",
                "X": "X",
                "Y": "Y"
            })
            st.dataframe(df_results, use_container_width=True, hide_index=True)

# 5. CHỨC NĂNG ĐẶT XE
with tab5:
    # --- ĐẶT CHUYẾN MỚI ---
    st.subheader("TẠO CHUYẾN MỚI")

    with st.form("new_booking"):
        col1, col2 = st.columns(2)
        with col1:
            customer_id = st.number_input("ID Khách hàng", min_value=1, step=1)
            driver_id = st.number_input("ID Tài xế", min_value=1, step=1)
        with col2:
            trip_distance = st.number_input("Quãng đường chuyến đi (km)", min_value=0.1, value=10.0, step=0.5)

        submit = st.form_submit_button("Đặt xe", type="primary")

        if submit:
            booking, error = booking_system.create_booking(customer_id, driver_id, trip_distance)
            if error:
                st.error(error)
            else:
                st.success("Đặt xe thành công!")
                st.write(f"**Tổng quãng đường:** {booking['total_distance']:.2f} km")
                st.write(f"**Chi phí:** {booking['fare']:,.0f} VND")
                st.write(f"Trạng thái: {booking['status']}")
                st.rerun()

    

    # --- QUẢN LÝ CHUYẾN ĐI ---
    st.subheader("QUẢN LÝ CHUYẾN ĐI")

    pending = booking_system.get_pending()
    if not pending:
        st.info("Không có chuyến nào đang chờ.")
    else:
        import pandas as pd
        df = pd.DataFrame(pending)[["booking_id", "customer_name", "driver_name", "total_distance", "fare", "status"]]
        st.dataframe(df, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Xác nhận tất cả", use_container_width=True):
                session_state_manager.save_state()
                n = booking_system.confirm_all()
                st.success(f"Đã xác nhận {n} chuyến.")
                st.rerun()
        with c2:
            if st.button("Hủy tất cả", use_container_width=True):
                session_state_manager.save_state()
                n = booking_system.cancel_all()
                st.warning(f"Đã hủy {n} chuyến.")
                st.rerun()

    

    # --- LỊCH SỬ ---
    st.subheader("LỊCH SỬ ĐẶT XE")
    all_b = booking_system.get_all()
    if not all_b:
        st.info("Chưa có dữ liệu lịch sử.")
    else:
        df_all = pd.DataFrame(all_b)[["booking_id", 
                                      "customer_name", 
                                      "driver_name", 
                                      "total_distance", 
                                      "fare", 
                                      "status"]]
        st.dataframe(df_all, use_container_width=True, hide_index=True)

# 6. TỰ ĐỘNG GHÉP CẶP
with tab6:
    # --- TẠO YÊU CẦU ---
    st.subheader("TẠO YÊU CẦU ĐẶT XE")
    c1, c2 = st.columns(2)
    with c1:
        customer_id = st.number_input("ID Khách hàng", min_value=1, step=1)
    with c2:
        trip_distance = st.number_input("Quãng đường chuyến đi (km)", min_value=0.1, value=5.0, step=0.5)
    
    if st.button("Thêm yêu cầu"):
        session_state_manager.save_state()
        req, err = auto_matching_system.create_request(customer_id, trip_distance)
        if err: st.error(err)
        else: st.success(f"Tạo yêu cầu #{req['id']} thành công!")

    

    # --- GHÉP CẶP TỰ ĐỘNG ---
    st.subheader("GHÉP CẶP TỰ ĐỘNG")
    if st.button("Bắt đầu ghép cặp", type="primary"):
        session_state_manager.save_state()
        results = auto_matching_system.auto_match_all()
        if not results:
            st.warning("Không có yêu cầu chờ hoặc không có tài xế rảnh.")
        else:
            st.success(f"Đã ghép thành công {len(results)} yêu cầu.")
            import pandas as pd
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    

    # --- DANH SÁCH YÊU CẦU ---
    st.subheader("DANH SÁCH YÊU CẦU")
    all_reqs = auto_matching_system.get_all()
    if not all_reqs:
        st.info("Chưa có yêu cầu nào.")
    else:
        df = pd.DataFrame([
            {
                "RequestID": r["id"],
                "CustomerID": r["customer_id"],
                "DriverID": r["driver"].id if r["driver"] else "-",
                "DriverName": r["driver"].name if r["driver"] else "-",
                "State": r["state"],
                "Trip(km)": r["trip_distance"]
            }
            for r in all_reqs
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
