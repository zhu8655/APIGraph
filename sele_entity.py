from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from tqdm import tqdm


APIMenu = {}


def findNextLine(str, p, lenth):
    while p < lenth:
        if str[p] != "\n":
            p += 1
        else:
            break
    if p == lenth:
        return -1
    else:
        return p + 1


def getWord(str, p, lenth):
    ret = ""
    while str[p] == " " or str[p] == "\t":
        p += 1
    while p < lenth:
        if str[p] != " " and str[p] != "\t" and str[p] != "\n":
            ret += str[p]
            p += 1
        else:
            break
    if p == lenth:
        p = -1
    return [ret, p]


def isPoint(str, p, lenth):
    ret = ""
    while p < lenth:
        if str[p] != "\n":
            if str[p] == "*":
                ret += "*"
            p += 1
        else:
            break
    return ret


def thirdTab(browser, url):
    browser.switch_to.window(browser.window_handles[2])

    try:
        jsonData = {}
        jsonData["Url"] = url

        # body = WebDriverWait(browser, 5).until(
        #     EC.presence_of_element_located((By.XPATH, r'//*[@id="main"]/*'))
        # )
        body = browser.find_elements_by_xpath(r'//*[@id="main"]/*')
        bodyLen = len(body)

        jsonData["Title"] = body[0].text
        jsonData["Description"] = body[3].text

        if "interface" in jsonData["Title"]:
            jsonData["Type"] = "interface"
        elif "callback function" in jsonData["Title"]:
            jsonData["Type"] = "callback function"
        elif "function" in jsonData["Title"]:
            jsonData["Type"] = "function"
        elif "structure" in jsonData["Title"]:
            jsonData["Type"] = "structure"
        elif "enumeration" in jsonData["Title"]:
            jsonData["Type"] = "enumeration"
        elif "method" in jsonData["Title"]:
            jsonData["Type"] = "method"
            jsonData["Class"] = jsonData["Title"][0:jsonData["Title"].find(
                "::")]
        elif "macro" in jsonData["Title"]:
            jsonData["Type"] = "macro"
        elif "union" in jsonData["Title"]:
            jsonData["Type"] = "union"

        idx = 0
        flag = 1
        while idx < bodyLen:
            if body[idx].tag_name == "pre" and flag == 1:
                jsonData["Syntax"] = body[idx].text
                idx += 1
                flag = 0
            elif body[idx].get_attribute("id") == "return-value":
                idx += 1
                tmp = []
                while idx < bodyLen and body[idx].tag_name == "p":
                    tmp.append(body[idx].text)
                    idx += 1
                jsonData["Return value"] = tmp
            elif body[idx].get_attribute("id") == "requirements":
                idx += 1
                tmp = {}
                rows = body[idx].find_elements_by_xpath(
                    r'./table/tbody//tr')
                for row in rows:
                    tmp[row.find_element_by_xpath(
                        r'./td[1]').text] = row.find_element_by_xpath(r'./td[2]').text
                jsonData["Requirements"] = tmp
            elif body[idx].get_attribute("id") == "see-also":
                idx += 1
                jsonData["see-also"] = {}

                tmp = []
                releation_type = "Normal"

                while idx < bodyLen:
                    if body[idx].text == "Conceptual":
                        jsonData["see-also"][releation_type] = tmp
                        tmp = []
                        releation_type = "Conceptual"
                    elif body[idx].text == "Other Resources":
                        jsonData["see-also"][releation_type] = tmp
                        tmp = []
                        releation_type = "Other Resources"
                    elif body[idx].text == "Reference":
                        jsonData["see-also"][releation_type] = tmp
                        tmp = []
                        releation_type = "Reference"
                    else:
                        try:
                            tmp.append(body[idx].find_element_by_xpath(r'./a').get_attribute("href"))
                        except:
                            idx += 1
                            continue
                    idx += 1
                jsonData["see-also"][releation_type] = tmp
                break
            else:
                idx += 1

        if "Syntax" in jsonData and "Type" in jsonData:
            jsonData["Args"] = []
            lenth = len(jsonData["Syntax"])
            p = 0

            if jsonData["Type"] == "callback function":
                p = findNextLine(jsonData["Syntax"], p, lenth)
                p = findNextLine(jsonData["Syntax"], p, lenth)
                while p != -1:
                    pair = getWord(jsonData["Syntax"], p, lenth)
                    p = pair[1]
                    if pair[0] == "const":
                        tmp = getWord(jsonData["Syntax"], p, lenth)
                        pair[0] += " " + tmp[0]
                        p = tmp[1]
                    elif pair[0] == ")" or p == -1:
                        break
                    pair[0] += isPoint(jsonData["Syntax"], p, lenth)
                    jsonData["Args"].append(pair[0])
                    p = findNextLine(jsonData["Syntax"], p, lenth)
            elif jsonData["Type"] == "function" or jsonData["Type"] == "method":
                while p != -1:
                    pair = getWord(jsonData["Syntax"], p, lenth)
                    p = pair[1]
                    if pair[0] == "const":
                        tmp = getWord(jsonData["Syntax"], p, lenth)
                        pair[0] += " " + tmp[0]
                        p = tmp[1]
                    elif pair[0] == ");" or p == -1:
                        break
                    pair[0] += isPoint(jsonData["Syntax"], p, lenth)
                    jsonData["Args"].append(pair[0])
                    p = findNextLine(jsonData["Syntax"], p, lenth)
            elif jsonData["Type"] == "structure" or jsonData["Type"] == "union":
                p = findNextLine(jsonData["Syntax"], p, lenth)
                while p != -1:
                    pair = getWord(jsonData["Syntax"], p, lenth)
                    p = pair[1]
                    if pair[0] == "const":
                        tmp = getWord(jsonData["Syntax"], p, lenth)
                        pair[0] += " " + tmp[0]
                        p = tmp[1]
                    elif pair[0] == "}" or p == -1:
                        break
                    pair[0] += isPoint(jsonData["Syntax"], p, lenth)
                    jsonData["Args"].append(pair[0])
                    p = findNextLine(jsonData["Syntax"], p, lenth)

        with open("./APIs/" + jsonData["Title"].replace("::", "@") + ".json", "w") as f:
            json.dump(jsonData, f)
    except:
        browser.close()
        browser.switch_to.window(browser.window_handles[1])
        raise Exception
    else:
        browser.close()
        browser.switch_to.window(browser.window_handles[1])


def secondTab(browser):
    browser.switch_to.window(browser.window_handles[1])

    spans = browser.find_elements_by_class_name("tree-expander")
    for span in spans:
        span.click()
        span.click()
    spans = browser.find_elements_by_class_name("tree-expander")
    for span in spans:
        span.click()

    links = browser.find_elements_by_tag_name('a')
    for link in tqdm(links):
        if link.get_attribute("aria-level") == "2" or link.get_attribute("aria-level") == "3":
            if not link.get_attribute("aria-posinset") == "1":
                for i in range(10):
                    try:
                        browser.execute_script(
                            '''window.open("{}");'''.format(link.get_attribute("href")))
                        thirdTab(browser, link.get_attribute("href"))
                    except:
                        continue
                    else:
                        break
                # break

    global APIMenu
    APIMenu["cnt"] += 1
    APIMenu[browser.find_element_by_xpath(
        r'//*[@id="affixed-left-container"]/ul/li[1]/a').text] = "Finished"
    with open("APIMenu.json", "w") as f:
        json.dump(APIMenu, f)

    browser.close()
    browser.switch_to.window(browser.window_handles[0])


with open("APIMenu.json", encoding="utf-8") as f:
    APIMenu = json.load(f)

# browser = webdriver.Chrome()
# browser.get('https://docs.microsoft.com/en-us/windows/win32/api/')

chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_experimental_option("excludeSwitches",["enable-logging"])
chrome_opt.add_argument('--headless')
chrome_opt.add_argument("--disable-gpu")
chrome_opt.add_argument('--ignore-certificate-errors')
chrome_opt.add_argument("--proxy-server=socks5://127.0.0.1:10808")
browser = webdriver.Chrome(options=chrome_opt)
browser.implicitly_wait(5)
browser.get('https://docs.microsoft.com/en-us/windows/win32/api/')

techSpan = browser.find_element_by_xpath(r'//*[@id="title-2-1"]/span')
techSpan.click()

techLinks = browser.find_elements_by_xpath(r'//*[@id="title-2-1"]/ul//a')
techLinksLen = len(techLinks)
for i in range(APIMenu["cnt"]-1, techLinksLen):
    browser.execute_script(
        '''window.open("{}");'''.format(techLinks[i].get_attribute("href")))
    secondTab(browser)
    # break
