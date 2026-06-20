"""
core/credit_account.py
======================
Lớp CreditAccount — Tài khoản Tín dụng (tiêu trước trả sau).

Kỹ thuật OOP:
- Kế thừa đơn từ BaseAccount
- Cho phép số dư âm trong giới hạn credit_limit
- Method Overriding: deposit (trả nợ), withdraw (thấu chi)
- Edge Case: từ chối vượt hạn mức
"""

from core.base_account import BaseAccount


class CreditAccount(BaseAccount):
    """
    Tài khoản Tín dụng — số dư có thể âm nhưng không vượt credit_limit.

    Attributes
    ----------
    credit_limit : float — hạn mức thấu chi tối đa (giá trị dương, ví dụ 20_000_000)
    """

    def __init__(
        self,
        account_number: str,
        owner_name: str,
        credit_limit: float,
        initial_balance: float = 0.0,
    ):
        """
        Parameters
        ----------
        credit_limit : float — hạn mức tín dụng, ví dụ 20_000_000 VND
        """
        super().__init__(account_number, owner_name, initial_balance)
        if credit_limit <= 0:
            raise ValueError("Hạn mức tín dụng phải lớn hơn 0.")
        self.credit_limit: float = credit_limit

    # ------------------------------------------------------------------
    # Method Overriding: deposit — logic trả nợ
    # ------------------------------------------------------------------
    def deposit(self, amount: float) -> None:
        """
        Nạp tiền / trả nợ tín dụng.
        Nếu số dư đang âm, tiền nạp sẽ giảm khoản nợ trước tiên.
        """
        if amount <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0.")
        self._set_balance(self.balance + amount)
        print(f"Nạp tiền thành công!")
        if self.balance <= 0:
            print(f"Số dư hiện tại: {self.balance:,.0f} VND (còn nợ)")
        else:
            print(f"Số dư mới: {self.balance:,.0f} VND")

    # ------------------------------------------------------------------
    # Method Overriding: withdraw — thấu chi trong hạn mức
    # ------------------------------------------------------------------
    def withdraw(self, amount: float) -> None:
        """
        Rút/chi tiêu — cho phép số dư về âm trong giới hạn credit_limit.

        Edge Case (Bẫy 2): nếu balance - amount < -credit_limit → từ chối.
        """
        if amount <= 0:
            raise ValueError("Số tiền rút phải lớn hơn 0.")

        projected_balance = self.balance - amount
        if projected_balance < -self.credit_limit:
            raise ValueError(
                f"Vượt quá hạn mức thấu chi cho phép! "
                f"Hạn mức: {self.credit_limit:,.0f} VND | "
                f"Số dư hiện tại: {self.balance:,.0f} VND | "
                f"Yêu cầu rút: {amount:,.0f} VND."
            )

        self._set_balance(projected_balance)
        print(f"Rút tiền thành công! (Sử dụng hạn mức thấu chi)")
        print(f"Số tiền rút: {amount:,.0f} VND")
        print(f"Số dư hiện tại: {self.balance:,.0f} VND")
