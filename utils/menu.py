"""
utils/menu.py
=============
Hệ thống Menu CLI cho Vietcombank Digibank Pro Simulator.

Mỗi chức năng (1–7) được tách thành một hàm riêng để dễ bảo trì.
State toàn cục được truyền qua dictionary `state` để tránh biến global.
"""

from core.base_account import BaseAccount
from core.savings_account import SavingsAccount
from core.credit_account import CreditAccount
from core.hybrid_account import HybridAccount
from gateways.payment_gateways import VNPayGateway, ViettelMoneyGateway, process_payment


# ======================================================================
# Helpers hiển thị
# ======================================================================
def print_header():
    print("\n" + "=" * 46)
    print("  VIETCOMBANK DIGIBANK PRO SIMULATOR")
    print("=" * 46)
    print("1. Mở tài khoản mới (Chọn loại tài khoản)")
    print("2. Xem thông tin & Kiểm tra MRO")
    print("3. Giao dịch Nạp / Rút tiền & Điểm thưởng")
    print("4. Tích lũy / Áp dụng lãi suất định kỳ")
    print("5. Gộp tài khoản & So sánh (Overloading)")
    print("6. Thanh toán hóa đơn qua Cổng trung gian")
    print("7. Thoát chương trình")
    print("=" * 46)


def _require_current_account(state: dict) -> bool:
    """Kiểm tra đã có tài khoản đang hoạt động chưa."""
    if state["current_account"] is None:
        print("\nHệ thống chưa có thông tin tài khoản. "
              "Vui lòng mở tài khoản ở Chức năng 1 trước.")
        return False
    return True


def _input_amount(prompt: str) -> float:
    """Nhập số tiền, cho phép cả dấu phẩy lẫn dấu chấm."""
    raw = input(prompt).strip().replace(",", "")
    return float(raw)


# ======================================================================
# Chức năng 1: Mở tài khoản mới
# ======================================================================
def feature_open_account(state: dict) -> None:
    print("\n--- CHỌN LOẠI TÀI KHOẢN ---")
    print("1. Savings Account  (Tài khoản Tiết kiệm)")
    print("2. Credit Account   (Tài khoản Tín dụng)")
    print("3. Hybrid Account   (Tài khoản Đa năng)")

    try:
        choice = input("Chọn loại tài khoản (1-3): ").strip()

        acc_number = input("Nhập số tài khoản 10 chữ số: ").strip()
        if not BaseAccount.validate_account_number(acc_number):
            print("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")
            return

        # Kiểm tra trùng số tài khoản
        for acc in state["accounts"]:
            if acc.account_number == acc_number:
                print("Số tài khoản đã tồn tại trong hệ thống!")
                return

        owner = input("Nhập tên chủ tài khoản: ")

        if choice == "1":
            rate = float(input("Nhập lãi suất năm (ví dụ 0.05): ").strip())
            account = SavingsAccount(acc_number, owner, rate)
            print(f"\nMở tài khoản Tiết kiệm thành công!")

        elif choice == "2":
            limit = _input_amount("Nhập hạn mức tín dụng (VND, ví dụ 20000000): ")
            account = CreditAccount(acc_number, owner, limit)
            print(f"\nMở tài khoản Tín dụng thành công!")

        elif choice == "3":
            rate = float(input("Nhập lãi suất năm (ví dụ 0.05): ").strip())
            account = HybridAccount(acc_number, owner, rate)
            print(f"\nMở tài khoản Hybrid thành công!")

        else:
            print("Lựa chọn không hợp lệ!")
            return

        print(f"Chủ tài khoản: {account.owner_name}")
        print(f"Số tài khoản : {account.account_number}")

        state["accounts"].append(account)
        state["current_account"] = account

    except ValueError as e:
        print(f"Lỗi: {e}")


# ======================================================================
# Chức năng 2: Xem thông tin & MRO
# ======================================================================
def feature_view_info(state: dict) -> None:
    if not _require_current_account(state):
        return

    acc = state["current_account"]
    print("\n--- THÔNG TIN TÀI KHOẢN HIỆN TẠI ---")
    print(f"Loại tài khoản : {acc.__class__.__name__}")
    print(f"Ngân hàng      : {acc.bank_name}")
    print(f"Số tài khoản   : {acc.account_number}")
    print(f"Chủ tài khoản  : {acc.owner_name}")
    print(f"Số dư          : {acc.balance:,.0f} VND")

    if isinstance(acc, SavingsAccount):
        print(f"Lãi suất       : {acc.interest_rate * 100:.1f}% / năm")
    if isinstance(acc, CreditAccount):
        print(f"Hạn mức tín dụng: {acc.credit_limit:,.0f} VND")

    # Hiển thị MRO
    print(f"\n--- MRO ({acc.__class__.__name__}) ---")
    for i, cls in enumerate(acc.__class__.__mro__):
        print(f"  {i}: {cls.__name__}")

    # Nếu có nhiều tài khoản, cho phép chuyển tài khoản active
    if len(state["accounts"]) > 1:
        print("\n--- DANH SÁCH TÀI KHOẢN TRONG HỆ THỐNG ---")
        for i, a in enumerate(state["accounts"]):
            marker = "  [ĐANG CHỌN]" if a is acc else ""
            print(f"  {i + 1}. {a.account_number} - {a.owner_name} "
                  f"({a.__class__.__name__}){marker}")
        try:
            sel = input("Chuyển sang tài khoản (Enter để bỏ qua): ").strip()
            if sel:
                idx = int(sel) - 1
                state["current_account"] = state["accounts"][idx]
                print(f"Đã chuyển sang: {state['current_account'].owner_name}")
        except (ValueError, IndexError):
            print("Lựa chọn không hợp lệ, giữ nguyên tài khoản hiện tại.")


# ======================================================================
# Chức năng 3: Nạp / Rút tiền
# ======================================================================
def feature_transaction(state: dict) -> None:
    if not _require_current_account(state):
        return

    acc = state["current_account"]
    print("\n--- GIAO DỊCH NẠP / RÚT TIỀN ---")
    print("1. Nạp tiền")
    print("2. Rút tiền")

    try:
        txn = input("Chọn giao dịch (1-2): ").strip()
        amount = _input_amount("Nhập số tiền: ")

        if txn == "1":
            acc.deposit(amount)
        elif txn == "2":
            acc.withdraw(amount)
        else:
            print("Lựa chọn không hợp lệ!")

    except ValueError as e:
        print(f"Giao dịch thất bại: {e}")


# ======================================================================
# Chức năng 4: Áp dụng lãi suất
# ======================================================================
def feature_apply_interest(state: dict) -> None:
    if not _require_current_account(state):
        return

    acc = state["current_account"]

    # Đa hình: chỉ các loại có apply_interest() mới hỗ trợ
    if not isinstance(acc, SavingsAccount):
        print("\nTính năng áp dụng lãi suất không được hỗ trợ cho loại tài khoản này.")
        return

    print("\n--- TÍNH LÃI ĐỊNH KỲ ---")
    try:
        acc.apply_interest()
    except Exception as e:
        print(f"Lỗi: {e}")


# ======================================================================
# Chức năng 5: Gộp & So sánh (Operator Overloading)
# ======================================================================
def feature_merge_compare(state: dict) -> None:
    if not _require_current_account(state):
        return

    if len(state["accounts"]) < 2:
        print("\nCần ít nhất 2 tài khoản trong hệ thống để dùng tính năng này.")
        return

    acc_a = state["current_account"]
    print("\n--- ĐỒNG BỘ & SO SÁNH TÀI KHOẢN (OPERATOR OVERLOADING) ---")
    print(f"Tài khoản hiện tại (A): {acc_a.owner_name} "
          f"(Số dư: {acc_a.balance:,.0f} VND)")
    print("\nChọn tài khoản đối ứng (B):")

    others = [a for a in state["accounts"] if a is not acc_a]
    for i, a in enumerate(others):
        print(f"  {i + 1}. {a.account_number} - {a.owner_name} "
              f"(Số dư: {a.balance:,.0f} VND)")

    try:
        idx = int(input("Chọn (số thứ tự): ").strip()) - 1
        acc_b = others[idx]

        # __lt__: so sánh
        result_lt = acc_a < acc_b
        if result_lt:
            cmp_text = "NHỎ HƠN"
        elif acc_a.balance == acc_b.balance:
            cmp_text = "BẰNG"
        else:
            cmp_text = "LỚN HƠN"

        total = acc_a + acc_b  # __add__

        print(f"\n[Kết quả So sánh (__lt__)]: "
              f"Số dư tài khoản A {cmp_text} số dư tài khoản B.")
        print(f"[Kết quả Tổng hợp (__add__)]: "
              f"Tổng số tiền sở hữu của cả 2 tài khoản là: {total:,.0f} VND.")

    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ!")
    except TypeError as e:
        # Bẫy 3: so sánh sai kiểu
        print(f"Lỗi kiểu dữ liệu khi thực hiện Operator Overloading: {e}")


# ======================================================================
# Chức năng 6: Thanh toán qua Duck Typing
# ======================================================================
def feature_payment_gateway(state: dict) -> None:
    if not _require_current_account(state):
        return

    acc = state["current_account"]
    print("\n--- THANH TOÁN HÓA ĐƠN QUA CỔNG TRUNG GIAN ---")
    print("1. Thanh toán qua VNPay")
    print("2. Thanh toán qua Viettel Money")

    try:
        gw_choice = input("Chọn cổng thanh toán (1-2): ").strip()
        amount = _input_amount("Nhập số tiền hóa đơn: ")

        if gw_choice == "1":
            gateway = VNPayGateway()
        elif gw_choice == "2":
            gateway = ViettelMoneyGateway()
        else:
            print("Lựa chọn không hợp lệ!")
            return

        process_payment(gateway, acc, amount)

    except ValueError as e:
        print(f"Giao dịch thất bại: {e}")
    except AttributeError as e:
        # Bẫy 4: cổng không có execute_pay
        print(f"Lỗi cổng thanh toán: {e}")


# ======================================================================
# Vòng lặp chính Menu
# ======================================================================
def run_menu() -> None:
    """Khởi chạy vòng lặp chính của hệ thống CLI."""
    state = {
        "accounts": [],        # Danh sách tất cả tài khoản
        "current_account": None,  # Tài khoản đang active
    }

    DISPATCH = {
        "1": feature_open_account,
        "2": feature_view_info,
        "3": feature_transaction,
        "4": feature_apply_interest,
        "5": feature_merge_compare,
        "6": feature_payment_gateway,
    }

    while True:
        print_header()
        choice = input("Chọn chức năng (1-7): ").strip()

        if choice == "7":
            print("\nCảm ơn đã trải nghiệm hệ thống Vietcombank Digibank Pro Simulator!")
            break
        elif choice in DISPATCH:
            DISPATCH[choice](state)
        else:
            print("Lựa chọn không hợp lệ! Vui lòng chọn từ 1 đến 7.")
