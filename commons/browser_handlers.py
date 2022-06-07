import webbrowser


CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(CHROME_PATH))


def register_to_webbrowser(key, path):
    webbrowser.register(key, None, webbrowser.BackgroundBrowser(path))


def set_chrome_path(path):
    global CHROME_PATH
    CHROME_PATH = path


def open_tab(url):
    webbrowser.get('chrome').open_new_tab(url)
