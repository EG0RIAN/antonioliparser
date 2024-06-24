from setuptools import setup

APP = ['app.py']
DATA_FILES = ['logo.png']  # Добавьте сюда все файлы, которые нужны вашему приложению
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'logo.icns',  # Укажите ваш файл иконки, если он есть
    'packages': ['requests', 'requests_html', 'kivy'],
    'plist': {
        'CFBundleName': 'Antonioli Desktop Parser',
        'CFBundleDisplayName': 'Antonioli Desktop Parser',
        'CFBundleGetInfoString': 'Antonioli Desktop Parser',
        'CFBundleIdentifier': 'com.parser',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
