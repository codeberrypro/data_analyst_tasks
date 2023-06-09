import time
import gspread
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium_stealth import stealth


API_GSPREAD = 'Your api key'
LINK_ORDER = 'https://sellercentral.amazon.com/orders-v3/order/'
PHONE_COMPANY = '1804964038'
QT = 1
COMPANY = ' WhiteLilyStore'  # use this if not specified for individual accounts
URL_AUTHORIZATION = 'https://sellercentral.amazon.com/ap/signin?openid.return_to=https%3A%2F%2Fsellercentral.amazon.' \
                    'com%2Forders-v3%2Forder%2F113-8041991-3543406&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fa' \
                    'uth%2F2.0%2Fidentifier_select&openid.assoc_handle=sc_na_amazon_v2&openid.mode=checkid_setup&ope' \
                    'nid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A' \
                    '%2F%2Fspecs.openid.net%2Fauth%2F2.0&mons_redirect=sign_in&ssoResponse=eyJ6aXAiOiJERUYiLCJlbmMiO' \
                    'iJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.X_9GyMvWbWamxCL6VBFyzbrdnhlRfb5jz9woie3o3Jt2M8cDoURRdA.8CjjJ' \
                    '5CJyBPezQVb.fCj92UF-dYSV_KCIZrbCDZQs_xKIJKH34t1iXbNUgwCerTCAsks5BCBmiSNaz28sf-KieC-WMj4gAGQAlLJ' \
                    'lltBQJgd_OW_8n30zkAarjrzAnULGNXpEUlEuEOdnH0Pv_fRoIGqPNT6IBspV-j1xpG9BvcEfJxKe2XPYeCl1wn90NWKy2w' \
                    'qXcBX7Lxm_jBVv4H5KQanyGWrCs-37sJBmmGc3U7TbdvygoH62otIgC41j0Z0v_6SZ0ffAs-uekLkkFgFM.p0Z69TBgDnuu' \
                    'tCXfIAi1jA'


def initialize_gspread_api():
    '''
    Initializes the Google Sheets API and returns the worksheet object to write data to.
    '''
    gc = gspread.service_account(filename='sheet.json')  # service account file name
    sh = gc.open_by_key(API_GSPREAD)  # Google Sheets ID
    worksheet = sh.worksheet('testlist')  # worksheet name
    return worksheet


def initialize_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36")

    # Set Webdriver options for fingerprint stealth using the Stealth module
    stealth_options = {
        "languages": ["en-US", "en"],
        "vendor": "Google Inc.",
        "platform": "Win32",
        "webgl_vendor": "Intel Inc.",
        "renderer": "Intel Iris OpenGL Engine",
        "fix_hairline": True,
    }
    chrome_options = stealth.chromedriver().webdriver.ChromeOptions().merge(chrome_options)
    chrome_options = stealth.add_options(chrome_options, **stealth_options)

    return webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)


def get_order_links(driver, ):
    driver.get('https://sellercentral.amazon.com/orders-v3/mfn/unshipped/ref=bb_myo_wos3_home?_encoding=UTF8&sort='
               'status_desc&shipByDate=all&communicationDeliveryId=b7c2113a-c226-4599-a762-faea56f0a631&page=1')

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    orders_table = soup.find('table', attrs={'id': 'orders-table'})
    time.sleep(2)
    tbody = orders_table.find('tbody')
    t = tbody.find_all('tr')

    for i in t:
        tds = i.find_all('td')
        buyer_name = tds[2].find('a', attrs={'data-test-id': 'buyer-name-with-link'}).text
        orders_id = tds[2].find('div', attrs={'class': 'cell-body-title'}).text
        link_orders = LINK_ORDER + orders_id

        data = tds[1].find('div', attrs={'class': 'cell-body'})
        order_data = data.find_all('div')[2].get_text(strip=True)
        product_name_table = tds[4].find('div', attrs={'class': True})

        for i in product_name_table:
            asin = i.find_all('div')[3].get_text(strip=True).split(':')[1]
            sku = i.find_all('div')[5].get_text().split(':')[1].strip()
            unit_price_split = i.find_all('div')[9].get_text().split(' ')[2]
            unit_price = unit_price_split.replace(',', '.').split('USD')[0]
            orders_item = i.find_all('div')[13].get_text(strip=True).split(' ')[4]

            list2 = [order_data, QT, sku, orders_id, buyer_name, asin, unit_price, orders_item]
            list1 = get_details_order(link_orders)
            list_total = list2 + list1

            # Заполняем пустые колонки
            list_total.insert(3, '')
            list_total.insert(4, '')
            list_total.insert(5, '')
            list_total.insert(18, '')
            list_total.insert(19, '')

            # Сортируем
            list_total[0], list_total[1] = list_total[1], list_total[0]
            list_total[0], list_total[2] = list_total[2], list_total[0]
            list_total[0], list_total[3] = list_total[3], list_total[0]

            list_total[6], list_total[7] = list_total[7], list_total[6]
            list_total[6], list_total[10] = list_total[10], list_total[6]
            list_total[6], list_total[16] = list_total[16], list_total[6]
            list_total[6], list_total[13] = list_total[13], list_total[6]
            list_total[8], list_total[11] = list_total[11], list_total[8]
            list_total[9], list_total[12] = list_total[12], list_total[9]
            list_total[11], list_total[14] = list_total[14], list_total[11]
            list_total[12], list_total[15] = list_total[15], list_total[12]
            list_total[14], list_total[17] = list_total[17], list_total[14]
            list_total[15], list_total[20] = list_total[20], list_total[15]
            list_total[18], list_total[20] = list_total[20], list_total[18]
            list_total[17], list_total[20] = list_total[20], list_total[17]

            # Записываем в гугл документы
            write_google_sheet(list_total)
            time.sleep(15)


def get_details_order(link_orders, driver):
    """We receive data from the order and separate the logic into a legal entity and an individual"""
    values_1 = []

    driver.get(link_orders)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    shipping_total_main = soup.find('div',attrs={'class': 'a-column a-span2 order-details-right-column a-span-last'})
    shipping = shipping_total_main.find('div', attrs={'class': 'a-row a-spacing-none order-details-bordered-box-sale-proceeds'})
    shipping_table = shipping.find('table', attrs={'class': 'a-normal a-spacing-none'})
    tr = shipping_table.find_all('tr')[1]
    span = tr.find('span').text
    if 'Shipping total' in span:
        td = tr.find_all('td')[1]
        shipping_total_split = td.find('span').get_text(strip=True).split(' ')[0]
        shipping_total = shipping_total_split.replace(',', '.').split('USD')[0]
        print(f'shipping_total: {shipping_total}')
    else:
        shipping_total = ''

    main_column = soup.find('div', attrs={'class': 'a-section a-spacing-medium a-spacing-top-extra-large'})

    try:
        order_details = main_column.find('span', attrs={'class': 'badge badge-grey'}).text  # result: Business customer
    except AttributeError:
        order_details = ''

    try:
        check_name = main_column.find('a', attrs={'data-test-id': 'buyer-name-with-link'}).text
        check_name = check_name.lower()
    except AttributeError:
        check_name = ''

    time.sleep(2)
    collum_left = main_column.find('div', attrs={'data-test-id': 'shipping-section-buyer-address'})
    table = collum_left.find_all('span')
    company = main_column.find('span', attrs={'data-test-id': 'shipping-section-recipient-name'}).text

    check_name_table_0 = table[1].text
    check_name_table_0 = check_name_table_0.lower()

    try:
        phone = main_column.find('span', attrs={'data-test-id': 'shipping-section-phone'}).get_text(strip=True).split('ext')[0]
    except AttributeError:
        phone = ''

    if 'Business customer' in order_details:
        name = table[0].text.split(' ')[0]
        try:
            last_name = table[0].text.split(' ')[1]
        except:
            last_name = table[0].text.split(' ')[0]

        company = main_column.find('span', attrs={'data-test-id': 'shipping-section-recipient-name'}).text
        if company == '':
            company = table[0].text
            name = check_name
        address = table[1].text
        city = table[2].text.replace(',', '')
        city_one = table[4].text
        zip_code = table[-1].text

        values_1.append(company)
        values_1.append(last_name)
        values_1.append(shipping_total)
        values_1.append(address)
        values_1.append(city)
        values_1.append(city_one)
        values_1.append(zip_code)
        values_1.append(phone)

    elif company == '' and check_name in check_name_table_0:
        company = table[0].text

        name = table[1].text.split(' ')[0]
        try:
            last_name = table[1].text.split(' ')[1]
        except:
            last_name = table[0].text.split(' ')[0]

        address = table[2].text
        city = table[3].text.replace(',', '')
        city_one = 'zzz'
        zip_code = table[-1].text

        values_1.append(company)
        values_1.append(last_name)
        values_1.append(shipping_total)
        values_1.append(address)
        values_1.append(city)
        values_1.append(city_one)
        values_1.append(zip_code)
        values_1.append(phone)

    else:
        company = 'WhiteLilyStore'

        name = table[0].text.split(' ')[0]
        try:
            last_name = table[0].text.split(' ')[1]
        except:
            last_name = table[0].text.split(' ')[0]


        address = table[1].text
        city = table[2].text.replace(',', '')
        city_one = table[4].text
        zip_code = table[-1].text

        values_1.append(company)
        values_1.append(last_name)
        values_1.append(shipping_total)
        values_1.append(address)
        values_1.append(city)
        values_1.append(city_one)
        values_1.append(zip_code)
        values_1.append(phone)

    return values_1


def write_google_sheet(values):
    worksheet.append_row(values, table_range="B6:B")


def main():
    driver_initialize = initialize_driver()
    initialize_gspread = initialize_gspread_api()
    list2 = get_order_links(initialize_driver)

if __name__ == '__main__':
    main()


