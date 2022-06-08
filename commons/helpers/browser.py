import webbrowser


CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
CHROME_KEY = 'chrome'
webbrowser.register(CHROME_KEY, None, webbrowser.BackgroundBrowser(CHROME_PATH))


def register_to_webbrowser(key, path):
    webbrowser.register(key, None, webbrowser.BackgroundBrowser(path))


def set_chrome_path(path):
    global CHROME_PATH
    CHROME_PATH = path


def open_tab(url, key=CHROME_KEY):
    webbrowser.get(key).open_new_tab(url)
