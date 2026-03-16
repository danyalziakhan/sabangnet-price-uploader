from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Settings:
    headless: bool
    test_mode: bool
    log_file: str
    input_file: str
    markets_data_file: str
    user_id: str
    password: str
    product_code_column: str
    price_column: str
    market_name_column: str
    percentage_column: str
