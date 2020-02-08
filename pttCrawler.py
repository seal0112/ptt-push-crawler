import requests
from bs4 import BeautifulSoup
import re
import time


def crawlPostLink(board, userNames, continuePage=None):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    url = 'https://www.ptt.cc/bbs/%s' % board

    data = requests.get(url, headers)
    soup = BeautifulSoup(data.text, 'lxml')

    btnPage = soup.find('div', {'class': 'btn-group-paging'})
    prePageLink = btnPage.find_all('a')[1]
    if continuePage is None:
        totalPage = int(prePageLink['href'].split('index')[1].split('.')[0]) + 1
    else:
        totalPage = continuePage

    pageUrl = 'https://www.ptt.cc/bbs/%s/index' % board
    for page in range(totalPage, 0, -1):
        print(page)
        nextPage = '%s%s.html' % (pageUrl,page)
        newData = requests.get(nextPage, headers)
        newSoup = BeautifulSoup(newData.text, 'lxml')

        titleLink = newSoup.find_all('div', {'class': 'title'})
        for i in range(len(titleLink)-1, -1, -1):
            if titleLink[i].a is not None:
                articleUrl = 'https://www.ptt.cc/%s' % titleLink[i].a['href']
                crawlUserPush(articleUrl, userNames)
                time.sleep(0.1)

def crawlUserPush(url, userNames):
    print(url)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

    data = requests.get(url, headers)
    soup = BeautifulSoup(data.text, 'lxml')

    # print(soup.prettify())
    result = []
    pushes = soup.find_all('div', {'class': 'push'})

    for push in pushes:
        user = push.find('span', {'class': 'push-userid'})
        if user is not None and user.text in userNames:
            content = push.find('span', {'class': 'push-content'})
            phcebusPush = {
                'user_id': user.text,
                'content': content.text
            }
            result.append(phcebusPush)

    if len(result) > 0:
        link = soup.find('link', {'href': re.compile('https://www.ptt.cc/bbs/Option/*')})
        try:
            time = soup.find_all('span', {'class': 'article-meta-value'})[3].text
        except:
            time = 'None Time'

        with open("./%s.html" % ('&'.join(userNames)),"a+") as f:
            f.write('<div>\n')
            f.write('\t<h3>%s</h3>\n' % soup.title.text)
            f.write('\t<span>%s </span>\n'% time)
            f.write('\t<a href="%s" target="_blank">文章連結</a>\n' % link['href'])
            for push in result:
                f.write("\t<p>%s%s</p>\n" % (push['user_id'], push['content']))
            f.write('</div>\n')
            f.write('<hr>\n\n')
            f.close()


if __name__ == '__main__':
