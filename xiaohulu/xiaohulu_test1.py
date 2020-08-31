import redis
import json
import time
import datetime
import requests
'''
1.从redis中取出需要爬取的账号
2.传递进去，登录之后爬取
3.获取信息，存储相关信息
获取失败
'''


redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
redis_key = 'swd_xiaohulu_20000_list'
fail_key = 'xiaohulu:fail_kuaishou_key_1'
no_value_key = 'xiaohulu:no_value_kuaishou_key'
url = 'https://www.xiaohulu.com/apis/bd/index/anchor/anchorLiveGiftData'


lens = redis_db.llen(redis_key)
print(lens)
print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))

# for i in range(lens):
while 1:
    roomid = redis_db.lpop(redis_key)
    if isinstance(roomid, bytes):
        roomid = roomid.decode()
# roomid = '1532246462'
    data = {
        "dateId": "",
        "platId": "59",
        "roomId": roomid,
        "type": "4",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://www.xiaohulu.com",
        "Connection": "keep-alive",
        "Referer": "https://www.xiaohulu.com/liveParticularsIndex/2/%s"%roomid,
        # "Referer":"https://www.xiaohulu.com/liveParticularsIndex/2/611356916",
        "token": "140ad1799d8c4685978fe47591a8d8b1",
        "Cookie": "Hm_lvt_1c358b33dfa30c89dd3a1927a5921793=1597623380,1597629757,1598184492,1598842758; xhl_cok=11a0%2FEzL0eP5SloxLmqAnNswMxDAuX4cR5BirTRnA%2BrdbH5JvgkLPwNm5yklUQdd5IfN11IYNRZo6ksqhw; xhl_pc_token=140ad1799d8c4685978fe47591a8d8b1; Hm_lpvt_1c358b33dfa30c89dd3a1927a5921793=1598853114; www_session=eyJpdiI6Ilwva0tucFZCaHhJdVNkenlBdDB2UnpBPT0iLCJ2YWx1ZSI6InhhVUJ4UUhTTnpnSHl3bzdwVmxNd2twT3VRYkg4aUUxZ1JSbEQzTEtqSklqam9WS0tzY2FsQzlmWHNCY0IwOWoiLCJtYWMiOiJhM2Q0NDRjMjhkNTcwNWI2MjU0MDVlZDFjYmM1OWYxZDU5MmZiOWEwNTc0N2YzOThmZGFlNGRjZjEyMTlmNTE5In0%3D",




    }
    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(data), timeout=5)
        try:
            if response.status_code == 200:
                data_list = json.loads(response.text)

                gift_value_list = data_list.get('data', '').get('line', '').get('gift_value', [])
                year = datetime.datetime.now().year
                if len(gift_value_list) > 0:
                    for gift_value_temp in gift_value_list:
                        #time_area = gift_value_temp.get('time_area', '')
                        # index_num = gift_value_list.index(gift_value_temp)

                        # if index_num + 1 < len(gift_value_list):   #在列表范围内
                        #     gift_time = gift_value_temp.get('time', '')
                        #     next_gift_time = gift_value_list[index_num + 1].get('time', '')
                        #     if gift_time > next_gift_time:
                        #         gift_time = str(year) + '-' + gift_value_temp.get('time', '')
                        #         next_gift_time = str(year+1) + '-' + gift_value_list[index_num + 1].get('time', '')
                        #     else:
                        #         gift_time = str(year) + '-' + gift_value_temp.get('time', '')
                        #         next_gift_time = str(year) + '-' + gift_value_list[index_num + 1].get('time', '')
                        gift_value_temp['ori_time'] = gift_value_temp.get('time', '')
                        gift_value_temp['time'] = str(year) + '-' + gift_value_temp.get('time', '')
                        gift_value_temp['time_area'] = str(year) + '-' + gift_value_temp.get('time_area', '')
                        gift_value_temp['roomid'] = roomid
                        gift_value_temp['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                        #print(gift_value_temp)
                        with open('/mnt/data/weidong.shi/file/invs_kuaishou_xhl_gift/' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding='utf-8') as f:
                            f.write(json.dumps(gift_value_temp, ensure_ascii=False) + '\n')
                    print(roomid, '------有gift值的天数------', len(gift_value_list))
                else:
                    redis_db.lpush(no_value_key, roomid)
                    print('------礼物值为空roomid:{}-------------'.format(roomid))
                time.sleep(3)
        except:
            redis_db.lpush(fail_key, roomid)
            print('---------------roomid:{}请求失败----------------------'.format(roomid))
    except:
        redis_db.lpush(fail_key, roomid)
        print('请求异常')


print('end_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))



