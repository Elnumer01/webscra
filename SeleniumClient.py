from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from JsonClass import jsonFile
from PandasClient import PandasClient
import time

class seleniumClient(jsonFile):
    
    def __init__(self):
        super().__init__("Data.json")
        self.filename = ""
        self.driver = None
        self.options = None
        self.url = ""
        
        
    # Configuración del navegador
    def settings(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-extensions")
        
    # Inicializar el navegador con las configuraciones establecidas
    def initBrowser(self):
        service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        
    def get_page(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)
        
    #leer las intrucciones de como va obtener la informacion de la pagina
    def readConfiguration(self):
        self.settings()
        self.initBrowser()
        self.filename = 'settings.json'
        listConfiguration = self.getDataJson()
        for config in listConfiguration["settings"]:
            if config['TYPE'] == 'URL':
                self.url = (config['XPATH'])
                self.get_page()
            if config['TYPE'] == 'TABLE':
                self.extractDataTable(config['XPATH'],config['FILE'])
                time.sleep(10)
            if config['TYPE'] == 'OL' or config['TYPE'] == 'UL':
                self.extractDataList(config['XPATH'],config['FILE'])
                time.sleep(10)
            if(config['TYPE'] == 'DIV'):
                self.extractDataDiv(config['XPATH'],config['FILE'])
                time.sleep(10)
            if(config['TYPE'] == 'A'):
                self.clickLink(config['XPATH'])
                time.sleep(10)
            if(config['TYPE'] == 'BUTTON'):
                self.clickButton(config['XPATH'])
                time.sleep(10)
            if(config['TYPE'] == 'SELECT'):
                self.selectValue(config['XPATH'],config['VALUE'])
                time.sleep(10)
            if(config['TYPE'] == 'INPUT'):
                self.inputValue(config['XPATH'],config['VALUE'])
                time.sleep(10)
                
        self.driver.quit()
                
    #Extraer todos los datos de las etiquetas table            
    def extractDataTable(self, xpath, filename):
        try:
            table = self.driver.find_element(By.XPATH, xpath)
            # Intentar extraer los encabezados del thead
            try:
                thead = table.find_element(By.TAG_NAME, 'thead')
                headers = [header.text for header in thead.find_elements(By.TAG_NAME, 'th')]
            except NoSuchElementException:
                headers = None
            
            # Extraer las filas del tbody
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
            # Extraer los datos de cada fila
            data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if headers:
                    row_data = {headers[i]: cells[i].text for i in range(len(cells))}
                else:
                    row_data = [cell.text for cell in cells]
                data.append(row_data)
            
            # Estructurar los datos en formato JSON
            table_data = {
                "data": data
            }
        except NoSuchElementException as e:
            print(f"An error occurred: {e}")
            table_data = {
                "data": []
            }
        
        self.filename = f'JsonGuardados/{filename}.json'
        self.toJson(table_data)
        pandas = PandasClient(self.getDataJson())
        excel = f'ExcelGuardados/{filename}.xlsx'
        pandas.to_excel(excel)
        
    #extraer datos de las etiquetas ol o ul
    def extractDataList(self,xpath,filename):
        try:
            lista = self.driver.find_element(By.XPATH, xpath)
            items = lista.find_elements(By.TAG_NAME,'li')
            data_list = [item.text for item in items]       
            self.filename = f'JsonGuardados/{filename}.json'
            self.toJson(data_list)
        except NoSuchElementException as e:
            print(f"An error occurred: {e}")
        
    def extractDataDiv(self,xpath,filename):
        try:
            dataDiv = self.driver.find_element(By.XPATH,xpath)
            items = dataDiv.find_elements(By.TAG_NAME,'div')
            data_list = [item.text for item in items]
            self.filename = f'JsonGuardados/{filename}.json'
            self.toJson(data_list)
        except NoSuchElementException as e:
            print(f"An error occurred: {e}")
        
        
    def clickButton(self,xpath):
        button = self.driver.find_element(By.XPATH,xpath)
        button.click()
        
    def clickLink(self, xpath):
        a = self.driver.find_element(By.XPATH,xpath)
        url = a.get_attribute('href')
        self.url = url
        self.get_page()
        
    def selectValue(self,xpath,value):
        select_element = self.driver.find_element(By.XPATH,xpath)
        select = Select(select_element)
        select.select_by_value(value)
    
    def inputValue(self,xpath,value):
        input_element = self.driver.find_element(By.XPATH,xpath)
        input_element(value)
        time.sleep(4)
        
    
    
    
    