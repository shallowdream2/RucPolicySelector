from ruclogin import RUC_LOGIN
import os.path as osp
import pandas as pd
from json import loads
from ruclogin import RUC_LOGIN
from selenium.common.exceptions import (
    ElementClickInterceptedException,
)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
import json

def get_cookies_as_dict(driver):
    cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict




def collect_activities(rate,type):
    print("start !")
    df = pd.read_csv("result.csv")
    #input("按任意键继续...")
    login = RUC_LOGIN(debug=False)
    login.initial_login("v")
    login.login()
    driver = login.driver
    wait = WebDriverWait(driver, 30)
    

    def try_click(wait, by, value):
        ele = wait.until(EC.element_to_be_clickable((by, value)))
        while True:
            try:
                ele.click()
            except ElementClickInterceptedException:
                driver.implicitly_wait(0.1)
                continue
            break
        return ele
    

    def register_activity(activity_id):
        try:
            url = f'https://v.ruc.edu.cn/campus#/activity/partakedetail/{activity_id}/show'
            driver.get(url)
            try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/button[2]')
            try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div/div[3]/button[2]')
        except Exception as e:
            print(f"报名失败: {e}")


    def process_activities(df,response_body):
        activities = json.loads(response_body)["data"]["data"]
        with open("log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"\ntime: {time.strftime('%Y-%m-%d %H:%M:%S')},start processing activities\n")
            for activity in activities:
                if activity["aid"] not in df["ID"].values and activity["progressname"] == "报名中" and activity["registname"] != "已满员" and activity["typelevel2"] == 22 and (type == 0 or activity['typelevel3'] == type):
                    # with open("result.txt", "a", encoding="utf-8") as result_file:
                    #     result_file.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n报名成功的活动: {activity['aname']} (ID: {activity['aid']})\n")
                    #     print(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n 报名成功的活动: {activity['aname']} (ID: {activity['aid']})\n")
                    #     register_activity(activity["aid"])
                    activity_type = "研讨" if activity["typelevel3"] == 24 else "讲座"
                    register_activity(activity["aid"])
                    # time,name,ID,type
                    new_row = pd.DataFrame([{
                        "time": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "name": activity["aname"],
                        "ID": activity["aid"],
                        "type": activity_type
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    # df是 pd.DataFrame
                    #df = df.
                    # time,name,ID,type
                    print(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n 报名成功的活动: {activity['aname']} (ID: {activity['aid']}) (Type: {activity_type})\n")
        df.to_csv("result.csv", index=False, encoding="utf-8")
        return df
                    
                    

    while True:
        response_body = ""
        driver.get("https://v.ruc.edu.cn/campus#/search")
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[2]/div')
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[2]/div/ul/li[2]/a') # 素质拓展
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[3]/div')
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[3]/div/ul/li[2]/a') # 形势与政策
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[5]/div') # 活动状态
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[5]/div/ul/li[2]/a') #报名中
        try_click(wait, By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/div/div/div[2]/div/div[7]/div/button[2]') #查询
        for request in driver.requests:
            if request.url == "https://v.ruc.edu.cn/campus/v2/search":
                try:
                    response_body = request.response.body.decode('utf-8', errors='ignore')
                    # 尝试解析 JSON 并解码 Unicode 转义序列
                    try:
                        response_json = json.loads(response_body)
                        response_body = json.dumps(response_json, ensure_ascii=False, indent=4)
                    except json.JSONDecodeError:
                        pass
                except UnicodeDecodeError:
                    response_body = "无法解码的响应体内容"
        
        df = process_activities(df,response_body)
        time.sleep(rate)
                
    print("等待浏览器被关闭...")
    driver.quit()


if __name__ == "__main__":
    # 读取设置settings.json
    if osp.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as settings_file:
            settings = loads(settings_file.read())
    else:
        settings = {}
    rate = settings.get("rate", 5)
    type = settings.get("type", 0) # 24： 讲座，108: 活动 0: 全部
    collect_activities(rate, type)