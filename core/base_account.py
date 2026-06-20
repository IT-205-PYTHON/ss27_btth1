"""
core/base_account.py
====================
Định nghĩa lớp trừu tượng BaseAccount — bộ khung chuẩn cho mọi loại tài khoản
trong hệ thống Vietcombank Digibank Pro Simulator.

Kỹ thuật OOP được áp dụng:
- ABC (Abstract Base Class)    : ép các lớp con phải triển khai deposit/withdraw
- @property                    : đóng gói __balance, chỉ đọc từ ngoài
- @staticmethod                : validate_account_number — không cần trạng thái
- @classmethod                 : update_bank_name — thao tác trên class attribute
- Operator Overloading (__add__, __lt__): so sánh và gộp số dư hai tài khoản
"""

from abc import ABC, abstractmethod


class BaseAccount(ABC):
    """Lớp trừu tượng — bộ khung cho mọi loại tài khoản Vietcombank."""

    # Class attribute: dùng chung toàn hệ thống
    bank_name: str = "Vietcombank"

    def __init__(self, account_number: str, owner_name: str, initial_balance: float = 0.0):
        """
        Khởi tạo tài khoản cơ sở.

        Parameters
        ----------
        account_number  : str   — mã số tài khoản (10 chữ số)
        owner_name      : str   — tên chủ tài khoản (sẽ được chuẩn hóa hoa)
        initial_balance : float — số dư ban đầu (mặc định 0)
        """
        # Validate trước khi lưu
        if not BaseAccount.validate_account_number(account_number):
            raise ValueError("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")

        self.account_number: str = account_number
        # Setter chuẩn hóa tên (in hoa, bỏ khoảng trắng thừa)
        self.owner_name = owner_name
        # Đóng gói số dư bằng name-mangled attribute
        self.__balance: float = initial_balance

    # ------------------------------------------------------------------
    # Property: đọc số dư từ bên ngoài nhưng không có setter trực tiếp
    # ------------------------------------------------------------------
    @property
    def balance(self) -> float:
        """Trả về số dư hiện tại (chỉ đọc từ ngoài lớp)."""
        return self.__balance

    # Phương thức nội bộ để các lớp con cập nhật __balance một cách kiểm soát
    def _set_balance(self, value: float) -> None:
        """Protected setter — chỉ dùng trong nội bộ class hierarchy."""
        self.__balance = value

    # ------------------------------------------------------------------
    # Property + Setter: chuẩn hóa tên chủ tài khoản
    # ------------------------------------------------------------------
    @property
    def owner_name(self) -> str:
        return self.__owner_name

    @owner_name.setter
    def owner_name(self, name: str) -> None:
        """Tự động in hoa và loại bỏ khoảng trắng thừa khi gán tên."""
        self.__owner_name = " ".join(name.strip().split()).upper()

    # ------------------------------------------------------------------
    # Abstract Methods — bắt buộc lớp con phải triển khai
    # ------------------------------------------------------------------
    @abstractmethod
    def deposit(self, amount: float) -> None:
        """Nạp tiền vào tài khoản."""
        ...

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        """Rút tiền khỏi tài khoản."""
        ...

    # ------------------------------------------------------------------
    # Static Method — kiểm tra định dạng số tài khoản (không cần self/cls)
    # ------------------------------------------------------------------
    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        """
        Kiểm tra số tài khoản phải đúng 10 chữ số (chỉ chữ số, không có ký tự khác).

        Returns
        -------
        bool — True nếu hợp lệ, False nếu không
        """
        return account_number.isdigit() and len(account_number) == 10

    # ------------------------------------------------------------------
    # Class Method — cập nhật tên ngân hàng cho toàn hệ thống
    # ------------------------------------------------------------------
    @classmethod
    def update_bank_name(cls, new_name: str) -> None:
        """
        Cập nhật bank_name trên toàn bộ class hierarchy.
        Dùng cls thay vì self để thay đổi có hiệu lực với mọi lớp con.
        """
        cls.bank_name = new_name
        print(f"[Hệ thống] Tên ngân hàng đã được cập nhật thành: {new_name}")

    # ------------------------------------------------------------------
    # Operator Overloading
    # ------------------------------------------------------------------
    def __add__(self, other: "BaseAccount") -> float:
        """
        __add__: cộng số dư hai tài khoản, trả về tổng dạng số.
        Edge Case: nếu other không phải BaseAccount → trả về NotImplemented.
        """
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance + other.balance

    def __lt__(self, other: "BaseAccount") -> bool:
        """
        __lt__: so sánh số dư tài khoản này < tài khoản kia.
        Edge Case: nếu other không phải BaseAccount → trả về NotImplemented.
        """
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"[{self.__class__.__name__}] {self.owner_name} | "
            f"STK: {self.account_number} | "
            f"Số dư: {self.balance:,.0f} VND"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"account_number='{self.account_number}', "
            f"owner_name='{self.owner_name}', "
            f"balance={self.balance})"
        )
