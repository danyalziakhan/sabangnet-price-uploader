from __future__ import annotations

import asyncio
import contextlib
import os

from typing import TYPE_CHECKING

from dunia import error
from dunia.browser import BrowserConfig
from dunia.login import LoginInfo
from dunia.playwright import PlaywrightBrowser, PlaywrightBrowserWithoutLogin
from playwright.async_api import async_playwright

from sabangnet_price_uploader.log import logger


if TYPE_CHECKING:
    from typing import Final

    from dunia.page import Page

    from sabangnet_price_uploader.settings import Settings

SABANGNET_LOGIN_URL: Final[str] = "https://www.sabangnet.co.kr/index.html"
DEFAULT_NAVIGATION_TIMEOUT: Final[int] = 3000000
DEFAULT_TIMEOUT: Final[int] = 300000


async def login_button_strategy(page: Page, login_button_query: str):
    if element := await page.query_selector(login_button_query):
        await element.scroll_into_view_if_needed()

    async with page.expect_navigation():
        await page.press(login_button_query, "Enter")

    async with page.expect_navigation():
        await page.click("button.bt_m_login")

    await page.wait_for_load_state(state="load")

    await page.wait_for_timeout(1000)


async def login(login_info: LoginInfo, browser: PlaywrightBrowser) -> None:
    page = await browser.new_page()
    await page.goto(login_info.login_url, wait_until="networkidle")

    await page.wait_for_selector(
        login_info.user_id_query,
        state="visible",
    )

    input_id = await page.query_selector(login_info.user_id_query)

    if input_id:
        await input_id.fill(login_info.user_id)
    else:
        raise error.LoginInputNotFound(
            f"User ID ({login_info.user_id}) could not be entered"
        )

    input_password = await page.query_selector(
        login_info.password_query,
    )
    if input_password:
        await input_password.fill(login_info.password)
    else:
        raise error.PasswordInputNotFound(
            f"Passowrd ({login_info.password}) could not be entered"
        )

    await login_info.login_button_strategy(page, login_info.login_button_query)

    logger.success(
        f"Logged in <MAGENTA><w>(ID: {login_info.user_id}, PW: {login_info.password})</></>"
    )

    await page.close()


async def upload_files(files_directory: str, settings: Settings):
    logger.log("ACTION", "Uploading files ...")

    browser_config = BrowserConfig(
        headless=settings.headless,
        default_navigation_timeout=DEFAULT_NAVIGATION_TIMEOUT,
        default_timeout=DEFAULT_TIMEOUT,
    )
    login_info = LoginInfo(
        login_url=SABANGNET_LOGIN_URL,
        user_id=settings.user_id,
        password=settings.password,
        user_id_query="#txtID",
        password_query="#txtPWD",
        login_button_query='#txtPWD ~ button[onclick="chk();"]',
        login_button_strategy=login_button_strategy,
    )

    async with async_playwright() as playwright:
        browser = await PlaywrightBrowserWithoutLogin(
            browser_config=browser_config,
            playwright=playwright,
        ).create()

        await login(login_info, browser)

        for file in os.listdir(files_directory):
            market = os.path.splitext(file)[0]
            await upload(browser, market, os.path.join(files_directory, file))


async def upload(browser: PlaywrightBrowser, market: str, file_path: str):
    logger.log("ACTION", f"Uploading <blue>{market}</> ...")

    for retries in range(1, 11):
        page = await browser.new_page()
        await page.goto(
            "https://sbadmin09.sabangnet.co.kr/#/mall/mall-separate-info",
            wait_until="load",
        )

        try:
            query = "xpath=//button[contains(./span, '대량등록')]"
            await page.wait_for_selector(query)

            async with page.page.expect_popup() as popup:
                await page.click(query)

            page2 = await popup.value

            try:
                await page2.wait_for_load_state("networkidle")
            except error.PlaywrightTimeoutError as err:
                await page2.close()
                await page.close()
                raise error.TimeoutException(
                    "Timed out when waiting for popup page"
                ) from err

            try:
                await page2.get_by_placeholder("쇼핑몰선택").click()
            except error.PlaywrightError as err:
                with contextlib.suppress(error.PlaywrightError):
                    await page2.close()
                await page.close()
                raise error.TimeoutException(
                    "Timed out when waiting for '쇼핑몰선택' button"
                ) from err

            await page2.wait_for_selector(
                'xpath=//div[contains(div/text(), "쇼핑몰선택")]/*//div[@class="ShmaSelectBox"]/*//div[contains(@class, "el-select-dropdown")]/*//li/span'
            )

            available_markets = await page2.locator(
                'xpath=//div[contains(div/text(), "쇼핑몰선택")]/*//div[@class="ShmaSelectBox"]/*//div[contains(@class, "el-select-dropdown")]/*//li/span'
            ).all_inner_texts()

            if market.lower() not in [m.lower() for m in available_markets]:
                logger.warning(
                    f"Market {market} is not present in available markets list {available_markets}"
                )
                await page2.close()
                break

            try:
                try:
                    await page2.get_by_text(f"{market}").click()
                except error.PlaywrightError:
                    await page2.get_by_text(f"{market}").nth(1).click(timeout=20000)
            except error.PlaywrightError:
                try:
                    await (
                        page2.get_by_role("listitem")
                        .filter(has_text=f"{market}")
                        .nth(1)
                        .click(timeout=20000)
                    )
                except error.PlaywrightError as err:
                    await page2.pause()
                    with contextlib.suppress(error.PlaywrightError):
                        await page2.close()
                    await page.close()
                    raise error.TimeoutException(
                        f"Timed out when waiting for market {market} selection"
                    ) from err

            # ? File selector
            try:
                async with page2.expect_file_chooser() as fc_info:
                    await page2.get_by_role("button", name="파일 선택").click()
            except error.PlaywrightError as err:
                with contextlib.suppress(error.PlaywrightError):
                    await page2.close()
                await page.close()
                raise error.TimeoutException(
                    "Timed out when waiting for selecting the file"
                ) from err

            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)

            # ? Upload
            await page2.get_by_role("button", name="저장").click()

            # ? Loading progress
            try:
                assert await page2.get_by_role("button", name="저장").is_visible()
            except AssertionError:
                logger.warning(
                    f"Loading progress didn't appear after uploading the file ({market}) ..."
                )
            else:
                while await page2.get_by_role("button", name="저장").is_visible():
                    await asyncio.sleep(1)

            # ? Close
            with contextlib.suppress(error.PlaywrightError):
                await page2.get_by_role("button", name="닫기").click()
        except error.TimeoutException as err:
            logger.warning(
                f"Retrying for {retries} times due to error message: {' '.join(str(err).split())}"
            )
        else:
            await page.close()
            break
    else:
        raise error.TimeoutException(f"Timed out waiting when uploading: {market}")
