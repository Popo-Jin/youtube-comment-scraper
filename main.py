from msilib.schema import CheckBox
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QRadioButton
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from tqdm import tqdm
import time
import re
import requests
import random
import os.path


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Youtube Comment Scraper')
        url = QLabel('URL')
        self.urlAddress = QLineEdit('')
        okButton = QPushButton('OK')
        cancelButton = QPushButton('Cancel')
        self.checkBox = QRadioButton('대댓글 포함')
        hbox1 = QHBoxLayout()
        hbox1.addWidget(url)
        hbox1.addWidget(self.urlAddress)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.checkBox)
        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(okButton)
        hbox3.addWidget(cancelButton)
        hbox3.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addStretch(1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addLayout(hbox3)

        okButton.clicked.connect(self.okButton)
        cancelButton.clicked.connect(self.cancelButton)


        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 200)

        # self.show()

    def okButton(self):
        #set option of selenium
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument('disable-gpu')
        options.add_argument('user')
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("lang=ko_KR")

        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        # print('Chrome Version', chrome_ver)
        try:
            driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)
        except:
            path = chromedriver_autoinstaller.install(True)
            driver = webdriver.Chrome(path, options=options)

        # driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)


        #target of crawling
        data_list = []
        # driver.get("https://www.youtube.com/watch?v=ScMzIvxBSi4")
        # driver.get("https://www.youtube.com/watch?v=_MrPvc54na0")
        
        driver.get(ex.urlAddress.text())
        
        #페이지 Open 후 기다리는 시간
        time.sleep(4.0)

        #down the scroll
        body = driver.find_element_by_tag_name('body')
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        # max size 50의 Queue 생성
        # 0.1sec * 50 = 5sec 동안 Scroll 업데이트가 없으면 스크롤 내리기 종료
        szQ = Queue(150)
        enqueue_count = 0
        
        while True:
                
            # Scroll 내리기
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            # Scroll Height를 가져오는 주기
            time.sleep(0.1)
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            
            # Queue가 꽉 차는 경우 스크롤 내리기 종료
            if(enqueue_count > szQ.maxsize):
                break
            
            # 첫 Loop 수행 (Queue가 비어있는 경우) 예외 처리
            if(szQ.isEmpty()) :
                szQ.enqueue(new_page_height)
                enqueue_count += 1
                
            # Queue에 가장 먼저 들어온 데이터와 새로 업데이트 된 Scroll Height를 비교함
            # 같으면 그대로 Enqueue, 다르면 Queue의 모든 Data를 Dequeue 후 새로운 Scroll Height를 Enqueue 함.    
            else :
                if(szQ.peek() == new_page_height) :
                    szQ.enqueue(new_page_height)
                    enqueue_count += 1
                else :
                    szQ.enqueue(new_page_height)
                    for z in range(enqueue_count) :
                        szQ.dequeue()
                    enqueue_count = 1
            
            # 기존의 Scroll 내리는 방식      
            #if new_page_height == last_page_height:
            #    break
            #last_page_height = new_page_height
            #time.sleep(2.0)
        
        # print ("[PASS] Get all comments of URL")
        if ex.checkBox.isChecked() is True:
            while True:
                buttons = driver.find_elements_by_css_selector("#more-replies > a")

                for button in buttons:
                    button.send_keys(Keys.ENTER)
                    time.sleep(1)
                    button.click()

                break



        html0 = driver.page_source
        driver.close()
        html = BeautifulSoup(html0, 'html.parser')

        comments_list = html.findAll({'ytd-comment-renderer'}, {'class':'style-scope ytd-comment-renderer'})
        replies_list = html.findAll({'ytd-comment-renderer'}, {'class':'style-scope ytd-comment-replies-renderer'})
        # print (comments_list)


        for j in range(len(comments_list)):
        #contents of comment
            comment = comments_list[j].find('yt-formatted-string',{'id':'content-text'}).text
            comment = comment.replace('\n', '') 
            comment = comment.replace('\t', '')
            #print(comment) 
            youtube_id = comments_list[j].find('a', {'id': 'author-text'}).span.text
            youtube_id = youtube_id.replace('\n', '') 
            youtube_id = youtube_id.replace('\t', '') 
            youtube_id = youtube_id.strip()
        
            raw_date = comments_list[j].find('yt-formatted-string', { 'class': 'published-time-text style-scope ytd-comment-renderer'})
            date = raw_date.a.text
            
            # try:
            #     like_num = comments_list[j].find('span', {'id': 'vote-count-middle', 'class': 'style-scope ytd-comment-action-buttons-renderer', 'aria-label': re.compile('좋아요')}).text
            #     like_num = like_num.replace('\n', '') 
            #     like_num = like_num.replace('\t', '')
            #     like_num = like_num.strip()
            # except: like_num = 0
        
            # data = {'youtube_id': youtube_id, 'comment': comment, 'date': date, 'like_num': like_num}
            data = {'youtube_id': youtube_id, 'comment': comment, 'date': date}

            data_list.append(data)
        
        for k in range(len(replies_list)):
            comment = replies_list[k].find('yt-formatted-string',{'id':'content-text'}).text
            comment = comment.replace('\n', '') 
            comment = comment.replace('\t', '')
            #print(comment) 
            youtube_id = replies_list[k].find('a', {'id': 'author-text'}).span.text
            youtube_id = youtube_id.replace('\n', '') 
            youtube_id = youtube_id.replace('\t', '') 
            youtube_id = youtube_id.strip()
        
            raw_date = replies_list[k].find('yt-formatted-string', { 'class': 'published-time-text style-scope ytd-comment-renderer'})
            date = raw_date.a.text
            
            # try:
            #     like_num = comments_list[j].find('span', {'id': 'vote-count-middle', 'class': 'style-scope ytd-comment-action-buttons-renderer', 'aria-label': re.compile('좋아요')}).text
            #     like_num = like_num.replace('\n', '') 
            #     like_num = like_num.replace('\t', '')
            #     like_num = like_num.strip()
            # except: like_num = 0
        
            # data = {'youtube_id': youtube_id, 'comment': comment, 'date': date, 'like_num': like_num}
            data = {'youtube_id': youtube_id, 'comment': comment, 'date': date}

            data_list.append(data)
        # result_df = pd.DataFrame(data_list, columns=['youtube_id','comment','date','like_num'])    
        result_df = pd.DataFrame(data_list, columns=['youtube_id','comment','date'])    
        url = ex.urlAddress.text()
        url2 = url.split('v=')
        file = f'./{url2[1]}.xlsx'
        print(f'url2 = {url2[1]}')
        print(f'file = {file}')
        if os.path.isfile(file) is False:
            result_df.to_excel(f"./{url2[1]}.xlsx", index = False)
        sys.exit()

    def cancelButton(self):
        sys.exit()

#Queue의 기본적인 기능 구현
class Queue():
    def __init__(self, maxsize):
        self.queue = []
        self.maxsize = maxsize
        
    # Queue에 Data 넣음
    def enqueue(self, data):
        self.queue.append(data)

    # Queue에 가장 먼저 들어온 Data 내보냄
    def dequeue(self):
        dequeue_object = None
        if self.isEmpty():
            print("Queue is Empty")
        else:
            dequeue_object = self.queue[0]
            self.queue = self.queue[1:]
        return dequeue_object
    
    # Queue에 가장 먼저들어온 Data return
    def peek(self):
        peek_object = None
        if self.isEmpty():
            print("Queue is Empty")
        else:
            peek_object = self.queue[0]
        return peek_object
    
    # Queue가 비어있는지 확인
    def isEmpty(self):
        is_empty = False
        if len(self.queue) == 0:
            is_empty = True
        return is_empty
    
    # Queue의 Size가 Max Size를 초과하는지 확인
    def isMaxSizeOver(self):
        queue_size = len(self.queue)
        if (queue_size > self.maxsize):
            return False
        else :
            return True

        
if __name__=="__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    
    # #set option of selenium
    # options = webdriver.ChromeOptions()
    # options.add_argument('window-size=1920x1080')
    # options.add_argument('disable-gpu')
    # options.add_argument('user')
    # options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    # options.add_argument("lang=ko_KR")

    # chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    # # print('Chrome Version', chrome_ver)
    # try:
    #     driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)
    # except:
    #     path = chromedriver_autoinstaller.install(True)
    #     driver = webdriver.Chrome(path, options=options)

    # # driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)


    # #target of crawling
    # data_list = []
    # # driver.get("https://www.youtube.com/watch?v=ScMzIvxBSi4")
    # driver.get("https://www.youtube.com/watch?v=_MrPvc54na0")
    
    # #페이지 Open 후 기다리는 시간
    # time.sleep(5.0)

    # #down the scroll
    # body = driver.find_element_by_tag_name('body')
    # last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    # # max size 50의 Queue 생성
    # # 0.1sec * 50 = 5sec 동안 Scroll 업데이트가 없으면 스크롤 내리기 종료
    # szQ = Queue(50)
    # enqueue_count = 0
    
    # while True:
    #     # Scroll 내리기
    #     driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        
    #     # Scroll Height를 가져오는 주기
    #     time.sleep(0.1)
    #     new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        
    #     # Queue가 꽉 차는 경우 스크롤 내리기 종료
    #     if(enqueue_count > szQ.maxsize):
    #         break
        
    #     # 첫 Loop 수행 (Queue가 비어있는 경우) 예외 처리
    #     if(szQ.isEmpty()) :
    #         szQ.enqueue(new_page_height)
    #         enqueue_count += 1
            
    #     # Queue에 가장 먼저 들어온 데이터와 새로 업데이트 된 Scroll Height를 비교함
    #     # 같으면 그대로 Enqueue, 다르면 Queue의 모든 Data를 Dequeue 후 새로운 Scroll Height를 Enqueue 함.    
    #     else :
    #         if(szQ.peek() == new_page_height) :
    #             szQ.enqueue(new_page_height)
    #             enqueue_count += 1
    #         else :
    #             szQ.enqueue(new_page_height)
    #             for z in range(enqueue_count) :
    #                 szQ.dequeue()
    #             enqueue_count = 1
        
    #     # 기존의 Scroll 내리는 방식      
    #     #if new_page_height == last_page_height:
    #     #    break
    #     #last_page_height = new_page_height
    #     #time.sleep(2.0)
    
    # # print ("[PASS] Get all comments of URL")

    # html0 = driver.page_source
    # driver.close()
    # html = BeautifulSoup(html0, 'html.parser')

    # comments_list = html.findAll('ytd-comment-thread-renderer', {'class':'style-scope ytd-item-section-renderer'})
    # # print (comments_list)


    # for j in range(len(comments_list)):
    #  #contents of comment
    #     comment = comments_list[j].find('yt-formatted-string',{'id':'content-text'}).text
    #     comment = comment.replace('\n', '') 
    #     comment = comment.replace('\t', '')
    #     #print(comment) 
    #     youtube_id = comments_list[j].find('a', {'id': 'author-text'}).span.text
    #     youtube_id = youtube_id.replace('\n', '') 
    #     youtube_id = youtube_id.replace('\t', '') 
    #     youtube_id = youtube_id.strip()
    
    #     raw_date = comments_list[j].find('yt-formatted-string', { 'class': 'published-time-text style-scope ytd-comment-renderer'})
    #     date = raw_date.a.text
        
    #     # try:
    #     #     like_num = comments_list[j].find('span', {'id': 'vote-count-middle', 'class': 'style-scope ytd-comment-action-buttons-renderer', 'aria-label': re.compile('좋아요')}).text
    #     #     like_num = like_num.replace('\n', '') 
    #     #     like_num = like_num.replace('\t', '')
    #     #     like_num = like_num.strip()
    #     # except: like_num = 0
    
    #     # data = {'youtube_id': youtube_id, 'comment': comment, 'date': date, 'like_num': like_num}
    #     data = {'youtube_id': youtube_id, 'comment': comment, 'date': date}

    #     data_list.append(data)
    
    # # result_df = pd.DataFrame(data_list, columns=['youtube_id','comment','date','like_num'])    
    # result_df = pd.DataFrame(data_list, columns=['youtube_id','comment','date'])    

    # result_df.to_excel("./data.xlsx", index = False)

    sys.exit(app.exec_())