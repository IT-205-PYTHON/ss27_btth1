"""
core/digital_premium_mixin.py
==============================
Lớp Mixin cung cấp tính năng dịch vụ số cao cấp (Premium Digital).

Kỹ thuật OOP:
- Mixin: lớp độc lập, không kế thừa từ BaseAccount
- Được thiết kế để "ghép" vào lớp khác thông qua đa kế thừa
- Không tự dùng độc lập được (không có __init__ riêng)

Lưu ý MRO: Mixin nên đứng TRƯỚC lớp chính trong danh sách kế thừa
để Python tìm phương thức Mixin trước, ví dụ:
    class HybridAccount(SavingsAccount, DigitalPremiumMixin): ...
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Chỉ import khi type-check, tránh circular import lúc runtime
    from core.base_account import BaseAccount


class DigitalPremiumMixin:
    """
    Mixin bổ sung tính năng hoàn tiền (cashback) cho các giao dịch trực tuyến
    lớn hơn 5,000,000 VND.

    Lớp này KHÔNG kế thừa từ BaseAccount. Nó chỉ hoạt động đúng khi được
    ghép với một lớp có phương thức _set_balance() và thuộc tính balance.
    """

    # Ngưỡng giao dịch được hoàn tiền
    CASHBACK_THRESHOLD: float = 5_000_000
    # Tỷ lệ hoàn tiền
    CASHBACK_RATE: float = 0.01  # 1%

    def cashback_reward(self, amount: float) -> float:
        """
        Tính và áp dụng hoàn tiền 1% nếu giao dịch > 5,000,000 VND.

        Parameters
        ----------
        amount : float — số tiền giao dịch vừa thực hiện

        Returns
        -------
        float — số tiền được hoàn (0 nếu không đủ điều kiện)
        """
        if amount > self.CASHBACK_THRESHOLD:
            cashback = round(amount * self.CASHBACK_RATE, 0)
            # Cộng cashback vào số dư thông qua _set_balance (kế thừa từ BaseAccount)
            self._set_balance(self.balance + cashback)  # type: ignore[attr-defined]
            print(
                f"[Ưu đãi Premium]: Bạn được hoàn tiền 1% "
                f"({cashback:,.0f} VND) vào tài khoản!"
            )
            return cashback
        return 0.0
