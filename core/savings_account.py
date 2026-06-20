"""
core/savings_account.py
=======================
Lớp SavingsAccount — Tài khoản Tiết kiệm.

Kỹ thuật OOP:
- Kế thừa đơn từ BaseAccount
- super().__init__() để tái sử dụng khởi tạo lớp cha
- Method Overriding: deposit, withdraw (phạt 2% rút trước hạn)
- Instance method: apply_interest()
"""

from core.base_account import BaseAccount


class SavingsAccount(BaseAccount):
    """
    Tài khoản Tiết kiệm — sinh lãi định kỳ, phạt phí khi rút trước hạn.

    Attributes
    ----------
    interest_rate : float — lãi suất năm (0.05 = 5%)
    EARLY_WITHDRAWAL_FEE : float — hằng số phí phạt rút trước hạn (2%)
    """

    # Hằng số nghiệp vụ — đặt tại class để dễ thay đổi chính sách
    EARLY_WITHDRAWAL_FEE: float = 0.02  # 2%

    def __init__(
        self,
        account_number: str,
        owner_name: str,
        interest_rate: float,
        initial_balance: float = 0.0,
    ):
        """
        Parameters
        ----------
        interest_rate   : float — lãi suất năm, ví dụ 0.06 = 6%
        """
        # Gọi __init__ lớp cha để thiết lập account_number, owner_name, balance
        super().__init__(account_number, owner_name, initial_balance)
        self.interest_rate: float = interest_rate

    # ------------------------------------------------------------------
    # Method Overriding: deposit
    # ------------------------------------------------------------------
    def deposit(self, amount: float) -> None:
        """Nạp tiền bình thường vào số dư (không có phí)."""
        if amount <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0.")
        self._set_balance(self.balance + amount)
        print(f"Nạp tiền thành công! Số dư mới: {self.balance:,.0f} VND")

    # ------------------------------------------------------------------
    # Method Overriding: withdraw — áp dụng phí phạt 2%
    # ------------------------------------------------------------------
    def withdraw(self, amount: float) -> None:
        """
        Rút tiền tiết kiệm — bị phạt 2% phí rút trước hạn.
        Tổng tiền bị trừ = amount + 2% * amount.
        """
        if amount <= 0:
            raise ValueError("Số tiền rút phải lớn hơn 0.")

        penalty = round(amount * self.EARLY_WITHDRAWAL_FEE, 0)
        total_deducted = amount + penalty

        if total_deducted > self.balance:
            raise ValueError(
                f"Số dư không đủ. Cần {total_deducted:,.0f} VND "
                f"(bao gồm phí phạt {penalty:,.0f} VND), "
                f"hiện có {self.balance:,.0f} VND."
            )

        self._set_balance(self.balance - total_deducted)
        print(f"Rút tiền thành công!")
        print(f"Số tiền rút: {amount:,.0f} VND")
        print(f"Phí phạt rút trước hạn (2%): {penalty:,.0f} VND")
        print(f"Số dư còn lại: {self.balance:,.0f} VND")

    # ------------------------------------------------------------------
    # Instance Method: apply_interest
    # ------------------------------------------------------------------
    def apply_interest(self) -> None:
        """
        Tính và cộng lãi vào tài khoản.
        Tiền lãi = balance * interest_rate (lãi suất năm đơn giản).
        """
        interest_earned = round(self.balance * self.interest_rate, 0)
        print(f"Số dư trước tính lãi: {self.balance:,.0f} VND")
        print(f"Lãi suất năm: {self.interest_rate * 100:.1f}%")
        print(f"Tiền lãi nhận được: +{interest_earned:,.0f} VND")
        self._set_balance(self.balance + interest_earned)
        print(f"Số dư mới sau khi cộng lãi: {self.balance:,.0f} VND")
