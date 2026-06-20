"""
gateways/payment_gateways.py
============================
Các lớp Cổng thanh toán độc lập — minh họa Duck Typing.

Kỹ thuật OOP / Design:
- Duck Typing: hàm process_payment() không kiểm tra kiểu đối tượng,
  chỉ cần đối tượng có phương thức execute_pay(account, amount).
- Hai class VNPayGateway và ViettelMoneyGateway KHÔNG kế thừa từ nhau
  hay từ bất kỳ lớp cơ sở chung nào — vẫn hoạt động được nhờ Duck Typing.
- Edge Case (Bẫy 4): nếu gateway không có execute_pay → bắt AttributeError.

Tại sao Duck Typing tốt cho hệ thống thanh toán?
─────────────────────────────────────────────────
Để tích hợp thêm 100 cổng thanh toán mới (MoMo, ZaloPay, PayPal...),
lập trình viên chỉ cần tạo class mới với phương thức execute_pay().
Không cần sửa hàm process_payment(), không cần sửa lớp tài khoản.
→ Tuân thủ Open/Closed Principle (mở rộng nhưng không sửa đổi).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.base_account import BaseAccount


# ======================================================================
# Cổng 1: VNPayGateway
# ======================================================================
class VNPayGateway:
    """Cổng thanh toán VNPay — tích hợp hệ sinh thái ngân hàng Việt."""

    def execute_pay(self, account: "BaseAccount", amount: float) -> None:
        """
        Thực hiện thanh toán qua VNPay.
        Duck Typing contract: cần account.account_number và account.withdraw().
        """
        print(f"[Hệ thống VNPay]: Đang kết nối tới tài khoản {account.account_number}...")
        print("Xác thực thanh toán bằng Duck Typing thành công!")
        account.withdraw(amount)
        print(f"Tài khoản đã thanh toán hóa đơn giá trị: {amount:,.0f} VND.")
        print(f"Số dư mới: {account.balance:,.0f} VND.")


# ======================================================================
# Cổng 2: ViettelMoneyGateway
# ======================================================================
class ViettelMoneyGateway:
    """Cổng thanh toán Viettel Money — kết nối ví điện tử Viettel."""

    def execute_pay(self, account: "BaseAccount", amount: float) -> None:
        """
        Thực hiện thanh toán qua Viettel Money.
        Cùng contract với VNPay nhưng là class hoàn toàn độc lập.
        """
        print(f"[Viettel Money]: Đang xác thực STK {account.account_number}...")
        print("Kết nối ví Viettel Money thành công!")
        account.withdraw(amount)
        print(f"Tài khoản đã thanh toán hóa đơn giá trị: {amount:,.0f} VND.")
        print(f"Số dư mới: {account.balance:,.0f} VND.")


# ======================================================================
# Hàm toàn cục: process_payment — trung tâm Duck Typing
# ======================================================================
def process_payment(payment_gateway, account: "BaseAccount", amount: float) -> None:
    """
    Xử lý thanh toán qua một cổng trung gian bất kỳ.

    Hàm này KHÔNG kiểm tra kiểu của payment_gateway (không isinstance()).
    Nó chỉ gọi execute_pay() — nếu object có method đó thì chạy được.
    Đây chính là tinh thần Duck Typing: "Nếu nó đi như vịt, kêu như vịt
    → ta coi nó là vịt."

    Edge Case (Bẫy 4): nếu payment_gateway thiếu execute_pay
    → bắt AttributeError và thông báo lỗi rõ ràng.

    Parameters
    ----------
    payment_gateway : any   — đối tượng cổng thanh toán (bất kỳ class nào)
    account         : BaseAccount — tài khoản cần thanh toán
    amount          : float — số tiền hóa đơn
    """
    try:
        payment_gateway.execute_pay(account, amount)
    except AttributeError:
        raise AttributeError(
            "Cổng thanh toán không hợp lệ hoặc chưa được tích hợp. "
            "Đảm bảo class cổng thanh toán có phương thức execute_pay(account, amount)."
        )
