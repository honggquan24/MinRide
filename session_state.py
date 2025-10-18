import copy
import streamlit as st
from driver import DriverManagementSystem
from customer import CustomerManagementSystem
from ride import RideManagementSystem


class ManageSessionState:
    def __init__(self):
        """Khởi tạo dữ liệu chính và bộ nhớ Undo"""
        # Quản lý tài xế
        if 'driver_manager' not in st.session_state:
            driver_manager = DriverManagementSystem()
            driver_manager.load_from_file("data\drivers.csv")
            st.session_state.driver_manager = driver_manager

        # Quản lý khách hàng
        if 'customer_manager' not in st.session_state:
            customer_manager = CustomerManagementSystem()
            customer_manager.load_from_file("data\customers.csv")
            st.session_state.customer_manager = customer_manager

        # Quản lý chuyến đi
        if 'ride_manager' not in st.session_state:
            ride_manager = RideManagementSystem()
            ride_manager.load_from_file("data\\rides.csv")
            st.session_state.ride_manager = ride_manager

        # Lịch sử undo
        if 'history' not in st.session_state:
            st.session_state.history = []

    # Các hàm getter
    def get_driver_manager(self):
        return st.session_state.driver_manager

    def get_customer_manager(self):
        return st.session_state.customer_manager

    def get_ride_manager(self):
        return st.session_state.ride_manager

    # Lưu hành động trước khi thao tác
    def save_state(self):
        """Lưu lại toàn bộ dữ liệu hiện tại (deepcopy)"""
        snapshot = {
            "drivers": copy.deepcopy(st.session_state.driver_manager.drivers),
            "customers": copy.deepcopy(st.session_state.customer_manager.customers),
            "rides": copy.deepcopy(st.session_state.ride_manager.rides),
        }
        st.session_state.history.append(snapshot)

        # Giới hạn 10 bước undo
        if len(st.session_state.history) > 10:
            st.session_state.history.pop(0)

    # Khôi phục hành động gần nhất
    def undo(self):
        """Khôi phục dữ liệu về bước trước"""
        if not st.session_state.history:
            st.warning("⚠ Không có thao tác nào để hoàn tác.")
            return False

        last_state = st.session_state.history.pop()

        # Phục hồi dữ liệu
        st.session_state.driver_manager.drivers = last_state["drivers"]
        st.session_state.customer_manager.customers = last_state["customers"]
        st.session_state.ride_manager.rides = last_state["rides"]

        st.success("Đã hoàn tác thao tác gần nhất.")
        st.rerun()
        return True
