from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from datetime import datetime
from os import makedirs, path
import sqlite3

class WebDriver(Chrome):
    def __init__(self, headless=True, log_folder="logs"):
        chromedriver_autoinstaller.install()
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        makedirs(log_folder, exist_ok=True)
        service = ChromeService(log_output=path.join(log_folder, f"{timestamp}.txt"))
        super().__init__(options=options, service=service)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
    def findElement(self, xpath, how='first'):
        if how=='first':
            return self.find_element(By.XPATH, xpath)
        elif how=='all':
            return self.find_elements(By.XPATH, xpath)
    def waitElement(self, xpath, timeout=60, how='first'):
        wait = WebDriverWait(self, timeout)
        elem = self.findElement(xpath, how)
        if isinstance(elem, list):
            elem_check = elem[-1]
        else:
            elem_check = elem
        wait.until(EC.visibility_of(elem_check))
        return elem
    def inputKeys(self, xpath, keys, clear=True):
        elem = self.waitElement(xpath)
        if clear:
            elem.clear()
        elem.send_keys(keys)

class SubwayDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.outlet_table = 'outlets'
        self.outlet_columns = [
            ('outlet_name', 'TEXT'),
            ('outlet_address', 'TEXT'),
            ('outlet_hours', 'TEXT'),
            ('outlet_waze', 'TEXT')
        ]
        self.outlet_primary_key = ('outlet_id', 'INTEGER')
        if not self.table_exists(self.outlet_table):
            self.create_table(self.outlet_table, self.outlet_columns)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    def table_exists(self, table_name):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return self.cursor.fetchone() is not None
    def create_table(self, table_name, columns):
        self.cursor.execute(f"""
            CREATE TABLE {table_name} (
                {' '.join(self.outlet_primary_key)} PRIMARY KEY AUTOINCREMENT,
                {', '.join(' '.join(col) for col in columns)}
            )
        """)
        self.conn.commit()
    def insert_outlet_data(self, data):
        placeholders = ', '.join(['?' for _ in self.outlet_columns])
        self.cursor.executemany(f"""
            INSERT INTO {self.outlet_table} (
                {', '.join([i[0] for i in self.outlet_columns])}
            )
            VALUES (
                {placeholders}
            )
        """, data)
        self.conn.commit()

def getOutletInfo(webElem, xp_outlet_name, xp_info_list, xp_waze_link):
    outlet_name = webElem.find_element(By.XPATH, xp_outlet_name).text
    infoList = webElem.find_elements(By.XPATH, xp_info_list)
    outlet_address = infoList[0].text
    outlet_hours = []
    for e in infoList[1:]:
        if e.get_attribute("class") == "infoboxcontent":
            break
        elif e.text == '':
            continue
        else:
            outlet_hours.append(e.text)
    outlet_waze = webElem.find_element(By.XPATH, xp_waze_link).get_attribute('href')
    return outlet_name, outlet_address, '\n'.join(outlet_hours), outlet_waze