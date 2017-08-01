# -*- coding: utf-8 -*-

import time
import logging
import pychrome
import functools


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def close_all_tabs(browser):
    if len(browser.list_tab()) == 0:
        return

    logging.debug("[*] recycle")
    for tab in browser.list_tab():
        try:
            tab.stop()
        except pychrome.RuntimeException:
            pass

        browser.close_tab(tab)

    time.sleep(1)
    assert len(browser.list_tab()) == 0


def setup_function(function):
    browser = pychrome.Browser()
    close_all_tabs(browser)


def teardown_function(function):
    browser = pychrome.Browser()
    close_all_tabs(browser)


def new_multi_tabs(browser, n):
    tabs = []
    for i in range(n):
        tabs.append(browser.new_tab())

    return tabs


def test_normal_callmethod():
    browser = pychrome.Browser()
    tabs = new_multi_tabs(browser, 10)

    for tab in tabs:
        result = tab.Page.navigate(url="http://www.fatezero.org")
        assert result['frameId']

    time.sleep(3)

    for tab in tabs:
        result = tab.Runtime.evaluate(expression="document.domain")
        assert result['result']['type'] == 'string'
        assert result['result']['value'] == 'www.fatezero.org'


def test_set_event_listener():
    browser = pychrome.Browser()
    tabs = new_multi_tabs(browser, 10)

    def request_will_be_sent(tab, **kwargs):
        tab.stop()

    for tab in tabs:
        tab.Network.requestWillBeSent = functools.partial(request_will_be_sent, tab)
        tab.Network.enable()
        try:
            tab.Page.navigate(url="chrome://newtab/")
        except pychrome.UserAbortException:
            pass

    for tab in tabs:
        if not tab.wait(timeout=5):
            assert False, "never get here"


def test_reuse_tab():
    browser = pychrome.Browser()
    tabs = new_multi_tabs(browser, 10)

    def request_will_be_sent(tab, **kwargs):
        tab.stop()

    for tab in tabs:
        tab.Network.requestWillBeSent = functools.partial(request_will_be_sent, tab)
        tab.Network.enable()
        try:
            tab.Page.navigate(url="chrome://newtab/")
        except pychrome.UserAbortException:
            pass

    for tab in tabs:
        if not tab.wait(timeout=5):
            assert False, "never get here"

    tabs = browser.list_tab()
    for tab in tabs:
        tab.Network.requestWillBeSent = functools.partial(request_will_be_sent, tab)
        tab.Network.enable()
        try:
            tab.Page.navigate(url="http://www.fatezero.org/")
        except pychrome.UserAbortException:
            pass

    for tab in tabs:
        if not tab.wait(timeout=5):
            assert False, "never get here"

