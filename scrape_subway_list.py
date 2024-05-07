# Variables
urlToScrape = "https://subway.com.my/find-a-subway"
searchFilter = "kuala lumpur"
xp_searchbox = '//input[@id="fp_searchAddress"]'
xp_searchbtn = '//button[@id="fp_searchAddressBtn"]'
xp_locationlist = '//div[@id="fp_locationlist"]/div/div[contains(@class, "fp_listitem")]'
xp_outlet_name = ".//div[@class='location_left']/h4"
xp_info_list = ".//div[@class='location_left']/div[@class='infoboxcontent']/p"
xp_waze_link = ".//div[@class='location_right']//a[contains(@href, 'waze')]"
sqlite_filename = "subwaykl.db"


from classes import WebDriver, SubwayDB, getOutletInfo
from sys import argv

with WebDriver(headless=False if "--debug" in argv else True) as driver:
    driver.get(urlToScrape)
    driver.inputKeys(xp_searchbox, searchFilter)
    driver.waitElement(xp_searchbtn).click()
    elemList = driver.waitElement(xp_locationlist, how='all')
    elemList = [i for i in elemList if i.is_displayed()]
    elemList = sorted(elemList, key=lambda x: int(x.value_of_css_property("order")))

    with SubwayDB(sqlite_filename) as db:
        db.insert_outlet_data([getOutletInfo(
            elem,
            xp_outlet_name,
            xp_info_list,
            xp_waze_link
        ) for elem in elemList])