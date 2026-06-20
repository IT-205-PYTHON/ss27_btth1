# Tài liệu Thiết kế — Vietcombank Digibank Pro Simulator

## 1. Sơ đồ kiến trúc kế thừa

```
                    ┌─────────────────────────────────┐
                    │         BaseAccount (ABC)        │
                    │  bank_name = "Vietcombank"       │
                    │  __balance (private)             │
                    │  @property balance               │
                    │  @staticmethod validate_number() │
                    │  @classmethod update_bank_name() │
                    │  @abstractmethod deposit()       │
                    │  @abstractmethod withdraw()      │
                    │  __add__, __lt__ (Overloading)   │
                    └──────────────┬──────────────────┘
                                   │ (kế thừa đơn)
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
  ┌──────────▼──────────┐    ┌─────▼────────────┐        │
  │   SavingsAccount    │    │  CreditAccount   │        │
  │  interest_rate      │    │  credit_limit    │        │
  │  deposit()          │    │  deposit()       │        │
  │  withdraw()+phí 2%  │    │  withdraw()+thấu │        │
  │  apply_interest()   │    │  chi âm          │        │
  └──────────┬──────────┘    └──────────────────┘        │
             │                                           │
             │   ┌───────────────────────────┐           │
             │   │   DigitalPremiumMixin     │           │
             │   │  cashback_reward()        │           │
             │   │  (KHÔNG kế thừa Base)     │           │
             └───┤                           │
  (Đa kế thừa)  └──────────┬────────────────┘
             │              │
    ┌─────────▼──────────────▼──────┐
    │        HybridAccount          │
    │  MRO: Hybrid→Savings→Base     │
    │       →Mixin→object           │
    │  deposit() + cashback         │
    │  withdraw() (kế thừa Savings) │
    │  apply_interest() (kế thừa)   │
    └───────────────────────────────┘
```

---

## 2. Mô tả vai trò từng lớp

| Lớp | Loại | Vai trò |
|-----|------|---------|
| `BaseAccount` | ABC | Bộ khung chuẩn — ép khai báo deposit/withdraw, đóng gói __balance, cung cấp Operator Overloading |
| `SavingsAccount` | Concrete | Tiết kiệm — sinh lãi, phạt 2% rút trước hạn |
| `CreditAccount` | Concrete | Tín dụng — thấu chi trong hạn mức, số dư âm hợp lệ |
| `DigitalPremiumMixin` | Mixin | Bổ trợ cashback 1% cho giao dịch > 5 triệu |
| `HybridAccount` | Concrete (đa kế thừa) | Kết hợp Savings + Mixin, thế hệ tài khoản đa năng |

---

## 3. Giải thích MRO của HybridAccount

Python sử dụng thuật toán **C3 Linearization** để xác định thứ tự tra cứu phương thức.

```python
class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    ...

# Kết quả HybridAccount.__mro__:
[HybridAccount, SavingsAccount, BaseAccount, DigitalPremiumMixin, object]
```

**Quy trình Python tìm phương thức `deposit()` trong `HybridAccount`:**

1. Tìm ở `HybridAccount` → **Có** (override với cashback) → **Dừng**
2. Nếu không có → tìm ở `SavingsAccount` → Có → Dừng
3. Nếu không có → tìm ở `BaseAccount` → Có (abstract) → Dừng
4. Nếu không có → tìm ở `DigitalPremiumMixin` → Không → tiếp tục
5. Cuối cùng → `object`

**Tại sao `SavingsAccount` đứng trước `DigitalPremiumMixin` trong MRO?**

Vì trong khai báo `class HybridAccount(SavingsAccount, DigitalPremiumMixin)`,
Python C3 ưu tiên lớp được liệt kê trước. `SavingsAccount` kế thừa từ `BaseAccount`,
nên toàn bộ chuỗi `SavingsAccount → BaseAccount` được chèn trước `DigitalPremiumMixin`.

---

## 4. Phân tích Duck Typing — Hệ thống thanh toán mở rộng

### Cơ chế hiện tại

```python
def process_payment(payment_gateway, account, amount):
    payment_gateway.execute_pay(account, amount)  # Chỉ cần có method này
```

`process_payment()` không kiểm tra `isinstance(payment_gateway, SomeBaseClass)`.
Nó chỉ gọi `.execute_pay()` — nếu đối tượng có method đó → chạy được.

### Ưu điểm khi mở rộng hệ thống

Để tích hợp **100 cổng thanh toán mới** (MoMo, ZaloPay, PayPal, Stripe...):

```python
# Không cần sửa process_payment() hay bất kỳ lớp tài khoản nào!
class MoMoGateway:
    def execute_pay(self, account, amount):
        # Logic riêng của MoMo
        account.withdraw(amount)

class StripeGateway:
    def execute_pay(self, account, amount):
        # Logic riêng của Stripe
        account.withdraw(amount)
```

Chỉ cần tạo class mới với `execute_pay()` → tự động tương thích với toàn hệ thống.

**Nguyên tắc được tuân thủ:**
- **Open/Closed Principle**: Mở để mở rộng, đóng để sửa đổi
- **Dependency Inversion**: Hàm cấp cao (`process_payment`) không phụ thuộc vào class cụ thể
- **Loose Coupling**: Các cổng thanh toán hoàn toàn độc lập với hệ thống tài khoản

---

## 5. Bảng Edge Cases và cách xử lý

| Bẫy | Tình huống | Cơ chế xử lý |
|-----|-----------|--------------|
| 1 | Khởi tạo `BaseAccount()` trực tiếp | `ABC` tự động ném `TypeError` |
| 2 | Rút vượt hạn mức `CreditAccount` | `if projected < -credit_limit: raise ValueError` |
| 3 | `__add__` / `__lt__` với sai kiểu | `if not isinstance(other, BaseAccount): return NotImplemented` |
| 4 | Cổng thanh toán thiếu `execute_pay` | `except AttributeError` trong `process_payment()` |

---

## 6. Cấu trúc thư mục project

```
vietcombank_digibank/
├── main.py                        # Điểm khởi chạy
├── DESIGN.md                      # Tài liệu thiết kế (file này)
├── core/
│   ├── __init__.py
│   ├── base_account.py            # ABC: BaseAccount
│   ├── savings_account.py         # SavingsAccount
│   ├── credit_account.py          # CreditAccount
│   ├── digital_premium_mixin.py   # DigitalPremiumMixin
│   └── hybrid_account.py          # HybridAccount (đa kế thừa)
├── gateways/
│   ├── __init__.py
│   └── payment_gateways.py        # VNPay, ViettelMoney, process_payment
├── utils/
│   ├── __init__.py
│   └── menu.py                    # Hệ thống menu CLI (Chức năng 1–7)
└── tests/
    ├── __init__.py
    └── test_all.py                # Unit tests toàn diện
```

---

## 7. Hướng dẫn chạy

### Chạy chương trình chính
```bash
cd vietcombank_digibank
python main.py
```

### Chạy toàn bộ unit tests
```bash
cd vietcombank_digibank
python -m pytest tests/test_all.py -v
# hoặc
python tests/test_all.py
```

### Yêu cầu
- Python 3.8+
- Không cần cài thêm thư viện ngoài (chỉ dùng standard library)
