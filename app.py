from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.config import Config
from kivy.core.window import Window
import requests
import re
import subprocess
import json
import sys
import os
import time

Window.size = (600, 200)

class MyApp(App):
    def build(self):
        self.title = 'Antonioli Desktop Parser'
        self.icon = 'logo.png'
        root = BoxLayout(orientation='vertical')

        # Labels for indicators
        self.cookies_valid_label = Label(text='Cookies валидны: ?', size_hint=(1, None), height=30)
        self.connection_label = Label(text='Подключение: ?', size_hint=(1, None), height=30)
        self.items_found_label = Label(text='Найдено возможных артикулов: ?', size_hint=(1, None), height=30)
        self.parser_status_label = Label(text='Статус парсера: ?', size_hint=(1, None), height=30)

        # Main layout
        main_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)

        left_column = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(0.5, 1))
        right_column = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(0.5, 1))

        # Input field and start button
        input_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.input_field = TextInput(hint_text='Введите Cookies Header', size_hint=(1, None), height=50)
        self.start_button = Button(text='Старт', size_hint=(1, None), height=50)
        self.start_button.bind(on_press=self.start)

        input_box.add_widget(self.input_field)
        input_box.add_widget(self.start_button)

        right_column.add_widget(input_box)

        # Indicators column
        indicators_column = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, None), height=150)
        indicators_column.add_widget(self.cookies_valid_label)
        indicators_column.add_widget(self.connection_label)
        indicators_column.add_widget(self.items_found_label)
        indicators_column.add_widget(self.parser_status_label)

        left_column.add_widget(indicators_column)

        # Add columns to main layout
        main_layout.add_widget(left_column)
        main_layout.add_widget(right_column)
        root.add_widget(main_layout)
        return root

    def start(self, instance):
        cookies_header = self.input_field.text.strip()
        if cookies_header:
            headers = {"Cookie": cookies_header}
            if self.check_connection(headers):
                self.cookies_valid_label.text = "Cookies валидны: Успешно"
                self.connection_label.text = "Подключение: Успешно"
                items_count = self.get_len_products(headers)
                self.items_found_label.text = f"Найдено возможных артикулов: {items_count}"
                data_json = json.dumps(cookies_header)
                python_executable = sys.executable
                env = os.environ.copy()
                command = [python_executable, 'main.py', data_json]
                process = subprocess.Popen(
                    command,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                self.cookies_valid_label.text = "Cookies валидны: Не удалось подключиться"
                self.connection_label.text = "Подключение: Не успешно"
                self.items_found_label.text = "Найдено возможных артикулов: Н/Д"

    def check_connection(self, headers):
        try:
            response = requests.get("https://stores.antonioli.eu/collections/woman", headers=headers)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_len_products(self, headers):
        try:
            sitemap_response = requests.get("https://stores.antonioli.eu/sitemap.xml", headers=headers)
            pages_pattern = r"https:\/\/stores\.antonioli\.eu\/sitemap_products_[^<\s]+"
            product_pattern = r"https:\/\/stores\.antonioli\.eu\/products\/[^<\s]+"

            pages_links = re.findall(pages_pattern, sitemap_response.text)
            product_links = []

            for page in pages_links:
                page_response = requests.get(page, headers=headers)
                product_links.extend(re.findall(product_pattern, page_response.text))

            return len(product_links)
        except requests.exceptions.RequestException:
            return 0

if __name__ == '__main__':
    MyApp().run()
