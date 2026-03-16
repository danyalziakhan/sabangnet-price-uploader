from __future__ import annotations

import math
import os
import re
import sys

from datetime import datetime
from functools import cache
from typing import TYPE_CHECKING

import pandas as pd

from sabangnet_price_uploader.log import LOGGER_FORMAT_STR, logger
from sabangnet_price_uploader.utils import upload_files


if TYPE_CHECKING:
    from sabangnet_price_uploader.settings import Settings

TODAY_DATE = f"{datetime.now().strftime('%Y%m%d')}"


@cache
def compile_regex(r: str):
    return re.compile(r)


@cache
def parse_int(text: str) -> int:
    """
    Strips the non-numeric characters in a text and convert to int

    Will throw error if string has no digit
    """
    try:
        return int("".join(compile_regex(r"(\d)").findall(text)))
    except ValueError as e:
        raise ValueError(
            f"Text don't have any digit: '{text}', so it cannot be converted to int"
        ) from e


def get_input_data(input_filename: str, product_code_column: str, price_column: str):
    df = pd.read_excel(input_filename, dtype="str")

    for column in [
        product_code_column,
        price_column,
    ]:
        try:
            df[column]
        except KeyError as e:
            error = f'"{column}" column is not present in file "{os.path.basename(input_filename)}"'
            raise KeyError(error) from e

    number_codes: list[str] = df[product_code_column].astype(str).to_list()
    prices: list[str] = df[price_column].astype(str).to_list()

    return (
        number_codes,
        prices,
    )


def get_markets(input_filename: str, market_name_column: str, percentage_column: str):
    df = pd.read_excel(input_filename, dtype="str")

    for column in [
        market_name_column,
        percentage_column,
    ]:
        try:
            df[column]
        except KeyError as e:
            error = f'"{column}" column is not present in file "{os.path.basename(input_filename)}"'
            raise KeyError(error) from e

    markets: list[str] = df[market_name_column].astype(str).to_list()
    percentages: list[str] = df[percentage_column].astype(str).to_list()

    return (
        markets,
        percentages,
    )


# ? Round up to specific decimal place
# ? See: https://stackoverflow.com/questions/2356501/how-do-you-round-up-a-number#:~:text=The%20math.,higher%20or%20equal%20to%20x%20.
def round_up(n: float, decimals: int = 0):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier


async def run(settings: Settings):
    logger.remove()
    if settings.test_mode:
        logger.add(
            sys.stderr,
            format=LOGGER_FORMAT_STR,
            level="DEBUG",
            colorize=True,
            enqueue=True,
        )
    else:
        logger.add(
            sys.stderr,
            format=LOGGER_FORMAT_STR,
            level="INFO",
            colorize=True,
            enqueue=True,
        )
    logger.add(
        settings.log_file,
        format=LOGGER_FORMAT_STR,
        enqueue=True,
        encoding="utf-8-sig",
        level="DEBUG",
    )

    logger.log("ACTION", f"Reading <blue>{settings.input_file}</> ...")

    (number_codes, prices,) = get_input_data(
        settings.input_file, settings.product_code_column, settings.price_column
    )

    logger.log("ACTION", f"Reading <blue>{settings.markets_data_file}</> ...")

    (markets, percentages,) = get_markets(
        settings.markets_data_file,
        settings.market_name_column,
        settings.percentage_column,
    )

    for market, percentage in zip(markets, percentages, strict=True):
        series_list: list[dict[str, str]] = []
        for number_code, price in zip(number_codes, prices, strict=True):
            price = parse_int(price)

            if "%" in percentage:
                percentage_ = 1 - (int(percentage.strip().split("%")[0]) / 100)
            else:
                percentage_ = 1 - float(percentage)

            final_price = (price) * (0.94) / percentage_
            final_price = int(round_up(final_price, -2))

            series: dict[str, str] = {
                settings.product_code_column: number_code,
                settings.price_column: str(round(final_price)),
            }

            series_list.append(series)

        df = pd.DataFrame(series_list)

        output_filename = os.path.join("output", TODAY_DATE, f"{market}.xlsx")

        if os.path.exists(output_filename):
            os.remove(output_filename)

        df.to_excel(output_filename, engine="openpyxl", index=False)

    logger.success("Files have been generated")

    await upload_files(os.path.join("output", TODAY_DATE), settings)

    logger.success("Program has been run successfully")
