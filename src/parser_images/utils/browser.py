#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Browser setup utilities for Parser-Images.

Provides Chrome WebDriver initialization with anti-detection measures.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_chrome_driver(headless=True, user_agent=""):
    """Create and configure Chrome WebDriver.

    Args:
        headless: Whether to run in headless mode.
        user_agent: Custom User-Agent string.

    Returns:
        Configured webdriver.Chrome instance.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.page_load_strategy = 'eager'
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver