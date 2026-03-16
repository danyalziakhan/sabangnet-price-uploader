chcp 65001
@echo off
rem get current this batch file directory
set dir=%~dp0

CALL .venv\Scripts\activate
CALL .venv\Scripts\python run.py --headful --input_file "INPUT_FILE.xlsx" --markets_data_file "MARKETS_DATA.xlsx" --user_id "user_id" --password "password" --product_code_column "품번코드" --price_column "판매가" --market_name_column "shoppingmall name" --percentage_column "percentage"

pause