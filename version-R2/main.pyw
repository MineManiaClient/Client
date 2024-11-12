import os
import sys
import subprocess
import logging
import json
import base64
import configparser
import random_username
from random_username.generate import generate_username
from PySide6.QtWidgets import (
    QSplashScreen, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton,
    QComboBox, QLineEdit, QProgressBar, QTextEdit, QFileDialog, QTabWidget, QSlider, QFormLayout, QCheckBox
)
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QTimer, QByteArray, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView  # Импортируем QWebEngineView для веб-просмотра
from PySide6.QtGui import QPalette
import minecraft_launcher_lib
import webbrowser
from PySide6.QtWidgets import QMessageBox
import qdarktheme
import darkdetect
import uuid
import time
import requests
logging.basicConfig(filename='launcher.log', level=logging.INFO)
# Задайте текущую версию вашего приложения
current_app_version = "version-1R0"  # Замените на актуальную версию WWH2

url = "https://raw.githubusercontent.com/MineManiaClient/Client/refs/heads/main/current_version.txt"

try:
    response = requests.get(url)
    response.raise_for_status()  # Проверка на наличие ошибок
    
    latest_version = response.text.strip()
    
    if current_app_version != latest_version:
        webbrowser.open("https://github.com/MineManiaClient/Client/tree/main")
        sys.exit()
        logging.info(f"Программа не запустился иза того что версия клиента устарела.")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при запросе версии: {e}")
# Логирование

# Настройки лаунчера
local_appdata = os.path.join(os.getenv('LOCALAPPDATA'))
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
MINECRAFT_DIR = os.path.join(local_appdata, '.minecraft')
VERSIONS_INI_PATH = os.path.join(SCRIPT_DIR, 'minecraft_versions.ini')
CUSTOM_VERSIONS_INI_PATH = os.path.join(SCRIPT_DIR, 'custom.ini')
LAST_PLAY_INI_PATH = os.path.join(SCRIPT_DIR, 'last_play.ini')
def generate_uuid():
    return str(uuid.uuid4())
lol = generate_username()[0]
generated_uuid = generate_uuid()
def get_system_theme():
    """Определяет текущую системную тему (светлую или тёмную)."""
    return 'dark' if darkdetect.isDark() else 'light'
theme = get_system_theme()
class MinecraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.show_piracy_warning()

        # Установка основных параметров окна
        self.setWindowTitle("MineMania - Legacy Minecraft Launcher")
        self.setGeometry(300, 300, 800, 600)
        self.setFixedSize(800, 600)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Установка фона для центрального виджета
        
        if theme == "dark":
            central_widget.setStyleSheet("background-image: url(image/background.jpg);")
        elif theme == "light":
            central_widget.setStyleSheet("background-image: url(image/background1.jpg);")
            

        # Вертикальная компоновка
        layout = QVBoxLayout(central_widget)

        # Вкладки
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Вкладка игры
        self.game_tab = QWidget()
        self.tabs.addTab(self.game_tab, "Игра")

        # Вкладка настроек
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Настройки")

        # Основной игровой виджет
        self.init_game_tab()

        # Виджет настроек
        self.init_settings_tab()

        self.add_forge_mods_tab()

        # Переменная для хранения пути к JAR-файлу
        self.jar_path = None

        # Загрузка списка версий и установка последней запущенной версии и имени пользователя
        self.load_versions()
        self.load_last_played_data()
    def show_piracy_warning(self):
            if theme == "dark":
                self.setStyleSheet("background-image: url(image/background.jpg);")
            elif theme == "light":
                self.setStyleSheet("background-image: url(image/background1.jpg);")
                
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Предупреждение")
            msg_box.setText("Вы используете пиратскую версию Minecraft. Это незаконно и нарушает авторские права Mojang.")
            msg_box.setInformativeText("Что вы хотите сделать?")

        # Кнопки
            close_warning_button = msg_box.addButton("Закрыть предупреждение", QMessageBox.NoRole)
            quit_button = msg_box.addButton("Выйти", QMessageBox.RejectRole)
            buy_license_button = msg_box.addButton("Купить лицензию", QMessageBox.AcceptRole)

            msg_box.exec()

            if msg_box.clickedButton() == quit_button:
                sys.exit(0)
            elif msg_box.clickedButton() == buy_license_button:
                webbrowser.open("https://www.minecraft.net/store/minecraft-java-edition")
                sys.exit(0)
            elif msg_box.clickedButton() == close_warning_button:
                pass

    def add_forge_mods_tab(self):
        # Create Forge Mods tab
        forge_mods_tab = QWidget()
        forge_mods_layout = QVBoxLayout()

        # Create and add a label for Forge Mods section
        label = QLabel("Ищем ;)")
        forge_mods_layout.addWidget(label)

        # Create and add a QWebEngineView widget to display the website
        self.web_view = QWebEngineView()
        url = "https://www.curseforge.com/MINECRAFT/search?page=1&pageSize=20&sortBy=relevancy&class=mc-mods"
        self.web_view.setUrl(QUrl(url))
        forge_mods_layout.addWidget(self.web_view)

        # Create and add a button to open the URL in a default web browser
        open_button = QPushButton("Скачать")
        open_button.clicked.connect(self.open_url_in_browser)
        forge_mods_layout.addWidget(open_button)

        forge_mods_tab.setLayout(forge_mods_layout)

        # Add the tab to the tab widget
        self.tabs.addTab(forge_mods_tab, "Forge")

    def open_url_in_browser(self):
        # Extract URL from the QWebEngineView and open it
        url = self.web_view.url().toString()
        QDesktopServices.openUrl(QUrl(url))


    def init_game_tab(self):
    # Создаем макет
            game_layout = QVBoxLayout(self.game_tab)
            

    # Метка выбора версии
            self.version_label = QLabel("Выберите версию Minecraft:", self)
            game_layout.addWidget(self.version_label)

    # Выпадающий список выбора версии
            self.version_combo = QComboBox(self)
            game_layout.addWidget(self.version_combo)

    # Поле для ввода имени пользователя
            self.username_label = QLabel("Имя пользователя:", self)
            game_layout.addWidget(self.username_label)

            self.username_input = QLineEdit(self)
            game_layout.addWidget(self.username_input)

    # Кнопка выбора JAR-файла
            self.select_jar_button = QPushButton("Выбрать JAR файл", self)
            game_layout.addWidget(self.select_jar_button)
            self.select_jar_button.clicked.connect(self.select_jar_file)

    # Кнопка запуска
            self.launch_button = QPushButton("Запустить Minecraft", self)
            game_layout.addWidget(self.launch_button)
            self.launch_button.clicked.connect(self.launch_minecraft)

    # Прогрессбар
            self.progress_bar = QProgressBar(self)
            game_layout.addWidget(self.progress_bar)

    # Лог ошибок и событий
            self.log_output = QTextEdit(self)
            self.log_output.setReadOnly(True)
            game_layout.addWidget(self.log_output)
            if not os.path.exists(MINECRAFT_DIR):
                os.makedirs(MINECRAFT_DIR)
                logging.info(f"Создана папка: {MINECRAFT_DIR}")
                self.log_output.append(f"Папка с игровыми ресурсами создана: {MINECRAFT_DIR}")

    def init_settings_tab(self):
        settings_layout = QFormLayout(self.settings_tab)
        self.java_console_checkbox = QCheckBox("Java консоль при запуске майнкрафта", self.settings_tab)
        settings_layout.addRow(self.java_console_checkbox)
        self.button = QPushButton("Открыть папку майнкрафта")
        self.button.clicked.connect(self.open_minecraft_folder)
        settings_layout.addWidget(self.button)
    def open_minecraft_folder(self):
        # Путь к каталогу .minecraft
        minecraft_path = MINECRAFT_DIR
        # Проверка существования каталога
        if os.path.exists(minecraft_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(minecraft_path))
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(f"Папка {MINECRAFT_DIR} не может быть найдена! Попробуйте перезапустить лаунчер.")
            msg_box.show()


    def load_versions(self):
        try:
            # Загрузка версий из custom.ini
            custom_versions = self.load_custom_versions()

            # Загрузка версий Minecraft из официального списка
            version_list = minecraft_launcher_lib.utils.get_version_list()

            # Проверка версий в папке MINECRAFT_DIR/versions/
            local_versions = self.load_local_versions()

            # Создание множества для хранения уникальных версий
            unique_versions = set()

            # Добавление кастомных версий
            for version in custom_versions:
                unique_versions.add(version)

            # Добавление локальных версий
            for version in local_versions:
                unique_versions.add(version)

            # Добавление стандартных версий
            for version in version_list:
                unique_versions.add(version['id'])

            # Добавление уникальных версий в ComboBox
            self.version_combo.clear()
            for version in sorted(unique_versions):
                self.version_combo.addItem(version)

            if self.version_combo.count() == 0:
                raise Exception("Не удалось загрузить ни одну версию Minecraft.")

            logging.info("Все доступные версии успешно загружены.")
            self.log_output.append("Все доступные версии успешно загружены.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке версий: {e}")
            self.log_output.append(f"Ошибка при загрузке версий: {e}")

    def load_local_versions(self):
        local_versions = []
        if os.path.exists(MINECRAFT_DIR):
            versions_dir = os.path.join(MINECRAFT_DIR, 'versions')
            if os.path.exists(versions_dir):
                for folder in os.listdir(versions_dir):
                    folder_path = os.path.join(versions_dir, folder)
                    if os.path.isdir(folder_path):
                        local_versions.append(folder)
        return local_versions

    def save_versions_to_ini(self, version_list, local_versions):
        config = configparser.ConfigParser()

        # Загрузка уже сохраненных версий
        if os.path.exists(VERSIONS_INI_PATH):
            config.read(VERSIONS_INI_PATH)

        if 'Minecraft Versions' not in config:
            config.add_section('Minecraft Versions')

        # Добавляем стандартные версии в секцию
        for version in version_list:
            if version['id'] not in config['Minecraft Versions']:
                config.set('Minecraft Versions', version['id'], '')

        # Добавляем локальные версии в секцию
        for version in local_versions:
            if version not in config['Minecraft Versions']:
                config.set('Minecraft Versions', version, '')

        # Записываем в .ini файл
        with open(VERSIONS_INI_PATH, 'w') as configfile:
            config.write(configfile)

        logging.info(f"Сохранено {len(version_list) + len(local_versions)} версий Minecraft в {VERSIONS_INI_PATH}.")
        self.log_output.append(
            f"Сохранено {len(version_list) + len(local_versions)} версий Minecraft в {VERSIONS_INI_PATH}.")

    def load_custom_versions(self):
        custom_versions = []
        if os.path.exists(CUSTOM_VERSIONS_INI_PATH):
            config = configparser.ConfigParser()
            config.read(CUSTOM_VERSIONS_INI_PATH)

            if 'Custom Versions' in config:
                custom_versions = config['Custom Versions']
        return custom_versions

    def save_last_played_data(self, version, username):
        config = configparser.ConfigParser()
        config['Last Played'] = {
            'version': version,
            'username': username
        }

        with open(LAST_PLAY_INI_PATH, 'w') as configfile:
            config.write(configfile)

        # Создание launcher_profiles.json
        profiles_path = os.path.join(MINECRAFT_DIR, 'launcher_profiles.json')
        profiles_data = {
            "profiles": {
                "Player": {
                    "name": username,
                    "lastVersionId": version,
                    "created": "2024-08-09T00:00:00.000Z",
                    "lastUsed": "2024-08-09T00:00:00.000Z"
                }
            }
        }

        # Запись данных в launcher_profiles.json
        with open(profiles_path, 'w') as profiles_file:
            json.dump(profiles_data, profiles_file, indent=4)

        logging.info(
            f"Сохранены последняя версия: {version} и имя пользователя: {username} в {LAST_PLAY_INI_PATH} и {profiles_path}.")
        self.log_output.append(
            f"Сохранены последняя версия: {version} и имя пользователя: {username} в {LAST_PLAY_INI_PATH} и {profiles_path}.")

    def load_last_played_data(self):
        if os.path.exists(LAST_PLAY_INI_PATH):
            config = configparser.ConfigParser()
            config.read(LAST_PLAY_INI_PATH)

            # Загружаем последнюю версию
            if 'Last Played' in config and 'version' in config['Last Played']:
                last_version = config['Last Played']['version']
                index = self.version_combo.findText(last_version)
                if index != -1:
                    self.version_combo.setCurrentIndex(index)
                    self.log_output.append(f"Последняя запущенная версия {last_version} выбрана по умолчанию.")
                    logging.info(f"Последняя запущенная версия {last_version} выбрана по умолчанию.")

            # Загружаем последнее имя пользователя
            if 'Last Played' in config and 'username' in config['Last Played']:
                last_username = config['Last Played']['username']
                self.username_input.setText(last_username)
                self.log_output.append(f"Имя пользователя {last_username} выбрано по умолчанию.")
                logging.info(f"Имя пользователя {last_username} выбрано по умолчанию.")
        else:
            logging.info("Файл last_play.ini не найден. Выбор версии и имени пользователя по умолчанию невозможен.")

    def select_jar_file(self):
        options = QFileDialog.Options()
        self.jar_path, _ = QFileDialog.getOpenFileName(self, "Выберите JAR файл", "", "JAR Files (*.jar)",
                                                       options=options)
        if self.jar_path:
            self.log_output.append(f"Выбран JAR файл: {self.jar_path}")
            logging.info(f"Выбран JAR файл: {self.jar_path}")

    def launch_minecraft(self):
        version = self.version_combo.currentText()
        username = self.username_input.text() or f"{lol}"

        self.log_output.append(f"Запуск версии: {version}")
        logging.info(f"Запуск версии: {version}")

        # Сохранение последней запущенной версии и имени пользователя
        self.save_last_played_data(version, username)

        try:
            if self.jar_path:
                self.log_output.append(f"Запуск Minecraft с кастомным JAR файлом: {self.jar_path}")
                logging.info(f"Запуск Minecraft с кастомным JAR файлом: {self.jar_path}")
                self.run_command_in_background(command)
                self.log_output.append("Java не установлена или не найдена.")
                logging.error("Java не установлена или не найдена.")
            else:
                # Установка Minecraft версии и запуск
                minecraft_launcher_lib.install.install_minecraft_version(version, MINECRAFT_DIR)
                logging.info(f"Версия {version} успешно установлена.")
                self.log_output.append(f"Версия {version} успешно установлена.")

                options = {
                    "username": username,
                    "uuid": f"{generated_uuid}",
                    "token": "0"
                }

                launch_command = minecraft_launcher_lib.command.get_minecraft_command(version, MINECRAFT_DIR, options)
                logging.info(f"Команда запуска: {' '.join(launch_command)}")
                print(generated_uuid)

                self.progress_bar.setValue(100)

                # Скрыть лаунчер и запустить Minecraft
                self.hide()
                self.run_command_in_background(launch_command)
        except Exception as e:
            logging.error(f"Ошибка при запуске Minecraft: {e}")
            self.log_output.append(f"Ошибка при запуске Minecraft: {e}")
            
    def on_ready_read(self):
        output = self.process.readAll().data().decode()
        self.log_output.append(output)


    def run_command_in_background(self, command):
        try:
            if self.java_console_checkbox.isChecked():
                self.process = subprocess.Popen(command)
            else:    
                self.process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Отслеживание завершения процесса Minecraft
            QTimer.singleShot(1000, self.check_process)
        except Exception as e:
            logging.error(f"Ошибка при запуске команды: {e}")
            self.log_output.append(f"Ошибка при запуске команды: {e}")

    def check_process(self):
        # Проверка, работает ли процесс Minecraft
        if self.process.poll() is None:  # Процесс все еще работает
            QTimer.singleShot(1000, self.check_process)
        else:  # Процесс завершился
            self.show()  # Показать лаунчер
            self.log_output.append("Minecraft завершен.")


def main():
    app = QApplication(sys.argv)
    if theme == 'dark':
        app.setStyleSheet(qdarktheme.load_stylesheet('dark'))
    elif theme == 'light':
        app.setStyleSheet(qdarktheme.load_stylesheet('light'))

    launcher = MinecraftLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
