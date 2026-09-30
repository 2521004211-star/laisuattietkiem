import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Công Cụ Tính Lãi Tiết Kiệm", page_icon="💰", layout="centered")

st.title("💰 Ứng dụng Tính Lãi Tiết Kiệm")
st.markdown("Công cụ giúp bạn tính toán số tiền lãi nhận được theo phương pháp **Lãi đơn** hoặc **Lãi kép**.")

# Form nhập liệu
with st.container():
    st.subheader("📝 Thông tin gửi tiết kiệm")
    col1, col2 = st.columns(2)
    
    with col1:
        principal = st.number_input("Số tiền gửi (VNĐ)", min_value=0.0, value=100000000.0, step=1000000.0, format="%.0f")
        term_months = st.number_input("Kỳ hạn gửi (tháng)", min_value=1, value=12, step=1)
        
    with col2:
        rate_annual = st.number_input("Lãi suất (%/năm)", min_value=0.0, value=6.0, step=0.1)
        interest_type = st.radio("Loại lãi suất", options=["Lãi đơn", "Lãi kép (Lãi nhập gốc)"])
        
    payment_method = st.selectbox(
        "Hình thức lãnh lãi / nhập gốc", 
        options=["Hàng tháng", "Hàng quý", "Cuối kỳ"]
    )

# Hàm định dạng tiền tệ
def format_currency(amount):
    return f"{amount:,.0f} VNĐ"

# Xử lý tính toán khi bấm nút
if st.button("🧮 Tính Toán", use_container_width=True):
    # Khởi tạo các biến toán học
    r = rate_annual / 100.0
    t_years = term_months / 12.0
    
    # Xác định số kỳ trong năm (n) dựa trên hình thức lãnh lãi
    if payment_method == "Hàng tháng":
        n = 12
        periods = term_months
        period_name = "Tháng"
    elif payment_method == "Hàng quý":
        n = 4
        periods = int(term_months / 3) if term_months >= 3 else 1
        period_name = "Quý"
    else: # Cuối kỳ
        n = 1
        periods = 1
        period_name = "Kỳ (Cuối kỳ)"
        
    # Tính toán
    if interest_type == "Lãi đơn":
        total_interest = principal * r * t_years
        total_amount = principal + total_interest
        
        # Tiền lãi định kỳ (đều nhau)
        if payment_method == "Hàng tháng":
            periodic_interest = (principal * r) / 12
        elif payment_method == "Hàng quý":
            periodic_interest = (principal * r) / 4
        else:
            periodic_interest = total_interest
            
        periodic_interest_display = format_currency(periodic_interest)
        
    else: # Lãi kép
        if payment_method == "Cuối kỳ":
            # Cuối kỳ lãi kép thì thực tế giống lãi đơn cho 1 chu kỳ gửi, hoặc ghép lãi theo năm
            # Ở đây tính ghép lãi 1 lần vào cuối kỳ
            total_amount = principal * (1 + r * t_years)
        else:
            # Lãi kép: A = P * (1 + r/n)^(n*t)
            total_amount = principal * (1 + r/n)**(n * t_years)
            
        total_interest = total_amount - principal
        first_period_interest = principal * (r/n)
        
        if payment_method == "Cuối kỳ":
            periodic_interest_display = format_currency(total_interest)
        else:
            periodic_interest_display = f"{format_currency(first_period_interest)} (Tăng dần ở các kỳ sau do lãi nhập gốc)"

    # --- HIỂN THỊ KẾT QUẢ ---
    st.divider()
    st.subheader("📊 Kết Quả Tính Toán")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Tiền lãi định kỳ", periodic_interest_display.split(" (")[0])
    res_col2.metric("Tổng tiền lãi", format_currency(total_interest))
    res_col3.metric("Tổng gốc + lãi", format_currency(total_amount))
    
    if interest_type == "Lãi kép" and payment_method != "Cuối kỳ":
        st.caption(f"*Lưu ý: Tiền lãi định kỳ ở trên là của {period_name.lower()} đầu tiên. Số tiền lãi sẽ tăng dần ở các kỳ tiếp theo do lãi được cộng dồn vào gốc.*")

    # --- BẢNG CHI TIẾT ---
    st.subheader("📅 Bảng chi tiết dòng tiền")
    schedule_data = []
    current_balance = principal
    cumulative_interest = 0
    
    for i in range(1, periods + 1):
        if interest_type == "Lãi đơn":
            interest_this_period = periodic_interest
            # Lãi đơn rút ra nên số dư gốc không đổi
            cumulative_interest += interest_this_period
            end_balance = current_balance
        else: # Lãi kép
            interest_this_period = current_balance * (r/n) if payment_method != "Cuối kỳ" else total_interest
            cumulative_interest += interest_this_period
            current_balance += interest_this_period
            end_balance = current_balance
            
        schedule_data.append({
            f"{period_name}": i,
            "Tiền gốc đầu kỳ": round(current_balance - (interest_this_period if interest_type == "Lãi kép" else 0)),
            "Lãi sinh ra": round(interest_this_period),
            "Tổng lãi tích luỹ": round(cumulative_interest),
            "Số dư cuối kỳ (Gốc + Lãi)": round(end_balance + (cumulative_interest if interest_type == "Lãi đơn" else 0))
        })
        
    df_schedule = pd.DataFrame(schedule_data)
    
    # Format hiển thị cho dataframe
    st.dataframe(
        df_schedule, 
        use_container_width=True,
        hide_index=True,
    )
