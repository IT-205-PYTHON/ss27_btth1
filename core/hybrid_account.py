"""
core/hybrid_account.py
======================
Lớp HybridAccount — Tài khoản Đa năng thế hệ mới.

Kỹ thuật OOP:
- Đa kế thừa (Multiple Inheritance): SavingsAccount + DigitalPremiumMixin
- MRO (Method Resolution Order): Python dùng thuật toán C3 Linearization
  → HybridAccount → SavingsAccount → BaseAccount → DigitalPremiumMixin → object
- Override deposit: gọi super().deposit() (SavingsAccount) rồi thưởng cashback
- Tích hợp apply_interest từ SavingsAccount và cashback_reward từ Mixin

MRO của HybridAccount (kiểm tra bằng HybridAccount.__mro__):
  [HybridAccount, SavingsAccount, BaseAccount, DigitalPremiumMixin, object]
"""

from core.savings_account import SavingsAccount
from core.digital_premium_mixin import DigitalPremiumMixin


class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    """
    Tài khoản Hybrid = Tiết kiệm (sinh lãi + phí rút) + Premium (cashback).

    Thứ tự kế thừa: SavingsAccount đứng trước DigitalPremiumMixin
    → Python tra MRO theo thứ tự: HybridAccount → SavingsAccount → BaseAccount
    → DigitalPremiumMixin → object.
    """

    def __init__(
        self,
        account_number: str,
        owner_name: str,
        interest_rate: float,
        initial_balance: float = 0.0,
    ):
        """
        Gọi super().__init__() theo chuỗi MRO, cuối cùng chạy đến
        BaseAccount.__init__() và SavingsAccount.__init__().
        """
        # super() tự động theo MRO — SavingsAccount.__init__ được gọi
        super().__init__(account_number, owner_name, interest_rate, initial_balance)

    # ------------------------------------------------------------------
    # Override deposit: nạp tiền + tặng cashback nếu đủ điều kiện
    # ------------------------------------------------------------------
    def deposit(self, amount: float) -> None:
        """
        Nạp tiền vào Hybrid Account:
        1. Gọi SavingsAccount.deposit() để tăng số dư bình thường
        2. Áp dụng cashback_reward() từ DigitalPremiumMixin nếu đủ điều kiện
        """
        if amount <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0.")

        # Bước 1: nạp tiền chuẩn (kế thừa từ SavingsAccount)
        self._set_balance(self.balance + amount)
        print(f"Nạp tiền thành công!")

        # Bước 2: kiểm tra và áp dụng cashback (từ DigitalPremiumMixin)
        self.cashback_reward(amount)

        print(f"Số dư mới: {self.balance:,.0f} VND")

    # withdraw kế thừa nguyên xi từ SavingsAccount (phạt 2% rút trước hạn)
    # apply_interest kế thừa nguyên xi từ SavingsAccount
