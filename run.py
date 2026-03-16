import asyncio
import os

from argparse import ArgumentParser
from multiprocessing import freeze_support

from sabangnet_price_uploader.main import TODAY_DATE, run
from sabangnet_price_uploader.settings import Settings


if __name__ == "__main__":
    freeze_support()

    parser = ArgumentParser()

    parser.add_argument(
        "--headless",
        help="Headless mode",
        action="store_true",
    )
    parser.add_argument(
        "--headful",
        help="Headful mode",
        action="store_true",
    )
    parser.add_argument(
        "--test_mode",
        help="Run the program with verbose logging output",
        action="store_true",
    )
    parser.add_argument(
        "--log_file",
        help="Log file path which will override the default path",
        type=str,
        default=os.path.join("logs", f"{TODAY_DATE}.log"),
    )
    parser.add_argument(
        "--input_file",
        help="Input file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--markets_data_file",
        help="Markets data file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--user_id",
        help="Sabangnet User ID",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--password",
        help="Sabangnet User Password",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--product_code_column",
        help="Product Code Column",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--price_column",
        help="Price Column",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--market_name_column",
        help="Market Name Column",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--percentage_column",
        help="Percentage Column",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    os.makedirs(os.path.join("output", TODAY_DATE), exist_ok=True)

    if args.headless:
        headless = True
    elif args.headful:
        headless = False
    else:
        headless = False

    settings = Settings(
        headless=headless,
        test_mode=args.test_mode,
        log_file=args.log_file,
        input_file=args.input_file,
        markets_data_file=args.markets_data_file,
        user_id=args.user_id,
        password=args.password,
        product_code_column=args.product_code_column,
        price_column=args.price_column,
        market_name_column=args.market_name_column,
        percentage_column=args.percentage_column,
    )

    asyncio.run(run(settings))
