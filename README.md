<p align="center">
  <h1 align="center">Sabangnet Price Uploader</h1>
  <p align="center">
    A Python automation tool for uploading product prices to Sabangnet
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2F3.11-blue">
  <img src="https://img.shields.io/badge/license-MIT-green">
</p>

---

Sabangnet Price Uploader is a Python tool that reads product pricing data,
applies market-specific adjustments, and automates uploads to the
[Sabangnet](https://www.sabangnet.co.kr/) platform. It uses Playwright
to perform browser automation and supports secure CLI-based workflows.

## Features

- Read Excel `.xlsx` input files with product codes and base prices
- Apply percentage-based adjustments for different markets
- Generate separate Excel files for each market
- Automate login and upload to Sabangnet using Playwright
- Pass credentials securely via command line
- CLI-only workflow for automation pipelines

## Installation

Clone the repository:

```bash
git clone https://github.com/danyalziakhan/sabangnet-price-uploader.git
cd sabangnet-price-uploader
```

Install the `uv` package manager:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

Or install via pip:

```bash
pip install uv
```

Create a virtual environment and install dependencies:

```bash
uv venv
uv sync
```

## Running the Tool

Use the provided batch file (Windows):

```bash
run.bat
```

Or run manually from the command line:

```bash
python run.py \
  --headful \
  --input_file "INPUT_FILE.xlsx" \
  --markets_data_file "MARKETS_DATA.xlsx" \
  --user_id "your_sabangnet_id" \
  --password "your_sabangnet_password" \
  --product_code_column "품번코드" \
  --price_column "판매가" \
  --market_name_column "shoppingmall name" \
  --percentage_column "percentage"
```

Replace `--headful` with `--headless` for invisible browser automation.

## Output

Generated market files are saved under:

```
output/YYYY-MM-DD/
```

Logs are saved in the `logs/` directory if enabled.

## Project Structure

```
sabangnet-price-uploader/
│
├── run.py
├── run.bat
├── pyproject.toml
├── README.md
│
└── sabangnet_price_uploader/
    ├── main.py
    ├── settings.py
    ├── utils.py
    ├── log.py
```

## Requirements

- Python 3.10 or 3.11
- Playwright (installed via `pyproject.toml`)
- Excel files in `.xlsx` format

## Why this tool exists

Uploading prices manually for multiple markets is time-consuming and error-prone.
This tool automates the process, calculates adjusted prices for each market,
and handles Sabangnet uploads in a repeatable way.

## License

MIT License