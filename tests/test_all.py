"""
tests/test_all.py
=================
Kiểm thử toàn diện hệ thống Vietcombank Digibank Pro Simulator.

Bao gồm:
- Unit tests cho từng lớp tài khoản
- Edge Cases (Bẫy 1–4) theo yêu cầu đề bài
- Kiểm tra MRO của HybridAccount
- Kiểm tra Duck Typing qua process_payment
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.base_account import BaseAccount
from core.savings_account import SavingsAccount
from core.credit_account import CreditAccount
from core.digital_premium_mixin import DigitalPremiumMixin
from core.hybrid_account import HybridAccount
from gateways.payment_gateways import VNPayGateway, ViettelMoneyGateway, process_payment


# ======================================================================
# Test BaseAccount
# ======================================================================
class TestBaseAccount(unittest.TestCase):

    def test_edge_case_1_cannot_instantiate_abstract(self):
        """Bẫy 1: Không thể khởi tạo trực tiếp lớp trừu tượng BaseAccount."""
        with self.assertRaises(TypeError):
            _ = BaseAccount("1234567890", "Test User")  # type: ignore

    def test_validate_account_number_valid(self):
        self.assertTrue(BaseAccount.validate_account_number("0123456789"))

    def test_validate_account_number_too_short(self):
        self.assertFalse(BaseAccount.validate_account_number("123"))

    def test_validate_account_number_has_letters(self):
        self.assertFalse(BaseAccount.validate_account_number("012345678a"))

    def test_invalid_account_number_raises(self):
        with self.assertRaises(ValueError):
            SavingsAccount("999", "Test", 0.05)

    def test_owner_name_normalized(self):
        """Setter phải in hoa và bỏ khoảng trắng thừa."""
        acc = SavingsAccount("1234567890", "  hoang van duc  ", 0.05)
        self.assertEqual(acc.owner_name, "HOANG VAN DUC")

    def test_update_bank_name_classmethod(self):
        original = BaseAccount.bank_name
        BaseAccount.update_bank_name("VCB Test")
        acc = SavingsAccount("1234567890", "Test", 0.05)
        self.assertEqual(acc.bank_name, "VCB Test")
        # Khôi phục
        BaseAccount.update_bank_name(original)


# ======================================================================
# Test SavingsAccount
# ======================================================================
class TestSavingsAccount(unittest.TestCase):

    def setUp(self):
        self.acc = SavingsAccount("1234567890", "Nguyen Van A", 0.06, 10_000_000)

    def test_deposit_increases_balance(self):
        self.acc.deposit(2_000_000)
        self.assertEqual(self.acc.balance, 12_000_000)

    def test_withdraw_with_penalty(self):
        """Rút 1,000,000 → bị phạt thêm 2% = 20,000 → trừ tổng 1,020,000."""
        self.acc.withdraw(1_000_000)
        self.assertEqual(self.acc.balance, 8_980_000)

    def test_withdraw_insufficient_funds_raises(self):
        with self.assertRaises(ValueError):
            self.acc.withdraw(20_000_000)

    def test_apply_interest(self):
        """6% lãi trên 10,000,000 = 600,000 VND."""
        self.acc.apply_interest()
        self.assertEqual(self.acc.balance, 10_600_000)

    def test_deposit_zero_raises(self):
        with self.assertRaises(ValueError):
            self.acc.deposit(0)

    def test_withdraw_zero_raises(self):
        with self.assertRaises(ValueError):
            self.acc.withdraw(0)


# ======================================================================
# Test CreditAccount
# ======================================================================
class TestCreditAccount(unittest.TestCase):

    def setUp(self):
        self.acc = CreditAccount("9876543210", "Tran Thi B", 20_000_000, 0)

    def test_withdraw_into_negative_within_limit(self):
        self.acc.withdraw(5_000_000)
        self.assertEqual(self.acc.balance, -5_000_000)

    def test_edge_case_2_exceed_credit_limit(self):
        """Bẫy 2: Vượt hạn mức thấu chi phải bị từ chối."""
        with self.assertRaises(ValueError) as ctx:
            self.acc.withdraw(21_000_000)
        self.assertIn("Vượt quá hạn mức thấu chi", str(ctx.exception))

    def test_deposit_repays_debt(self):
        self.acc.withdraw(10_000_000)
        self.acc.deposit(3_000_000)
        self.assertEqual(self.acc.balance, -7_000_000)

    def test_deposit_full_repayment(self):
        self.acc.withdraw(5_000_000)
        self.acc.deposit(5_000_000)
        self.assertEqual(self.acc.balance, 0)


# ======================================================================
# Test HybridAccount + MRO
# ======================================================================
class TestHybridAccount(unittest.TestCase):

    def setUp(self):
        self.acc = HybridAccount("5555555555", "Le Van C", 0.06, 10_000_000)

    def test_mro_order(self):
        """MRO phải theo thứ tự: Hybrid → Savings → Base → Mixin → object."""
        mro_names = [cls.__name__ for cls in HybridAccount.__mro__]
        self.assertEqual(mro_names, [
            "HybridAccount",
            "SavingsAccount",
            "BaseAccount",
            "ABC",
            "DigitalPremiumMixin",
            "object",
        ])

    def test_deposit_large_triggers_cashback(self):
        """Nạp 6,000,000 > 5,000,000 → nhận thêm 1% = 60,000."""
        self.acc.deposit(6_000_000)
        expected = 10_000_000 + 6_000_000 + 60_000
        self.assertEqual(self.acc.balance, expected)

    def test_deposit_small_no_cashback(self):
        """Nạp 1,000,000 < 5,000,000 → không cashback."""
        self.acc.deposit(1_000_000)
        self.assertEqual(self.acc.balance, 11_000_000)

    def test_withdraw_still_penalizes(self):
        """Rút tiền vẫn bị phạt 2% như SavingsAccount."""
        self.acc.withdraw(1_000_000)
        self.assertEqual(self.acc.balance, 8_980_000)

    def test_apply_interest(self):
        """HybridAccount kế thừa apply_interest từ SavingsAccount."""
        self.acc.apply_interest()
        self.assertEqual(self.acc.balance, 10_600_000)

    def test_is_instance_of_savings_and_mixin(self):
        self.assertIsInstance(self.acc, SavingsAccount)
        self.assertIsInstance(self.acc, DigitalPremiumMixin)
        self.assertIsInstance(self.acc, BaseAccount)


# ======================================================================
# Test Operator Overloading
# ======================================================================
class TestOperatorOverloading(unittest.TestCase):

    def setUp(self):
        self.acc_a = SavingsAccount("1111111111", "A", 0.05, 10_000_000)
        self.acc_b = SavingsAccount("2222222222", "B", 0.05, 15_000_000)

    def test_add_two_accounts(self):
        total = self.acc_a + self.acc_b
        self.assertEqual(total, 25_000_000)

    def test_lt_comparison_true(self):
        self.assertTrue(self.acc_a < self.acc_b)

    def test_lt_comparison_false(self):
        self.assertFalse(self.acc_b < self.acc_a)

    def test_edge_case_3_add_with_non_account_returns_not_implemented(self):
        """Bẫy 3: Cộng tài khoản với số nguyên → NotImplemented."""
        result = self.acc_a.__add__(999)
        self.assertEqual(result, NotImplemented)

    def test_edge_case_3_lt_with_string_returns_not_implemented(self):
        """Bẫy 3: So sánh tài khoản với chuỗi → NotImplemented."""
        result = self.acc_a.__lt__("some string")
        self.assertEqual(result, NotImplemented)


# ======================================================================
# Test Duck Typing — Payment Gateway
# ======================================================================
class TestDuckTyping(unittest.TestCase):

    def setUp(self):
        self.acc = SavingsAccount("3333333333", "Duck Test", 0.05, 10_000_000)

    def test_vnpay_gateway(self):
        gw = VNPayGateway()
        process_payment(gw, self.acc, 500_000)
        # 500,000 + phí 2% (10,000) = 510,000 bị trừ
        self.assertEqual(self.acc.balance, 9_490_000)

    def test_viettel_money_gateway(self):
        gw = ViettelMoneyGateway()
        process_payment(gw, self.acc, 500_000)
        self.assertEqual(self.acc.balance, 9_490_000)

    def test_edge_case_4_invalid_gateway_raises(self):
        """Bẫy 4: Cổng thanh toán không có execute_pay → AttributeError."""

        class FakeGateway:
            pass  # Không có execute_pay

        with self.assertRaises(AttributeError) as ctx:
            process_payment(FakeGateway(), self.acc, 100_000)
        self.assertIn("Cổng thanh toán không hợp lệ", str(ctx.exception))


# ======================================================================
# Chạy toàn bộ test
# ======================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)
