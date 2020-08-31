# '''
# 1.打开首页
# 2.获取分类  ---分类id
# 3、分类下的页数
# https://study.163.com/p/search/studycourse.json
# {
#     activityId: 0
#     frontCategoryId: "480000003121024"   ---分类id
#     keyword: ""
#     orderType: 50
#     pageIndex: 1
#     pageSize: 50   ---每页展示
#     priceType: -1
#     relativeOffset: 0
#     searchTimeType: -1
# }
#
# 获取里面的页数进行翻页
# totlePageCount
# resulr  query   totlePageCount
#
# 同时获取class信息
# {
#         productId
#         courseId
#         productName
#         productType
#         startTime
#         endTime
#         description
#         provider
#         score
#         scoreLevel
#         learnerCount
#         lessonCount
#         imgUrl
#         bigImgUrl
#         lectorName
#         originalPrice
#         discountPrice
#         discountRate
#         forumTagLector
#         tagLectorTime
#         schoolShortName
#         tagIap
#         gmtModified
#         firstPublishTime
#         displayType
#         courseCardProps
#         published
#         activityIds
#         isPromStatus
#         machineGrade
#         vipContentType
#         vipStartTime
#         vipEndTime
#         vipPrice
#         viewCount
#         termType
#         compositeType
#         parentName
#         scheduleType
#         advertiseSearchUuid
#         advertiseFlag
#         webOneDesc
#         categoryNames
#       },
#
# {"code":0,"message":"ok",
# "result":{
# "query":
#
#
# '''
#
#
# #-------------------test1-------------------
# # {
# #     "productId": 1003271002,
# #     "courseId": 1003271002,
# #     "productName": "职场加速器 | 加速职场成长",
# #     "productType": 0,
# #     "startTime": -1,
# #     "endTime": 9223372036854775807,
# #     "description": "【课程亮点】\n一张全脑优势脑图，可视化你的天赋优势；\n一套DISC行为理论，让你看懂自己更懂他人；\n三条发展路线，锁定你的修炼方向；\n六层晋升金字塔，带你看透组织框架，\n十二字真言，祝你砥砺前行；\n近百道作业，结合理论落地实操；\n老师指点，一对一作业辅导。\n【学习须知】\n1. 建议学习方式：\n第一轮，网易云课堂APP上的离线观看。\n第二轮，电脑网页端在线观看并记录笔记。\n第三轮，整体了解之后，再来提交作业。\n3.收费课程带有作业，以作业交流的方式，个性优化成长。",
# #     "provider": "八运会",
# #     "score": 4.9,
# #     "scoreLevel": 3,
# #     "learnerCount": 1717,
# #     "lessonCount": 99,
# #     "imgUrl": "https://edu-image.nosdn.127.net/4c23629f8054417e85b70ef23cb143ee.jpg?imageView&quality=100&crop=0_0_800_451",
# #     "bigImgUrl": "https://edu-image.nosdn.127.net/4c23629f8054417e85b70ef23cb143ee.jpg?imageView&quality=100&crop=0_0_800_451",
# #     "lectorName": "职场教练柏永辉",
# #     "originalPrice": 249.00,
# #     "discountPrice": null,
# #     "discountRate": null,
# #     "forumTagLector": 1,
# #     "tagLectorTime": 1518431391176,
# #     "schoolShortName": null,
# #     "tagIap": null,
# #     "gmtModified": null,
# #     "firstPublishTime": null,
# #     "displayType": 0,
# #     "courseCardProps": null,
# #     "published": null,
# #     "activityIds": "",
# #     "isPromStatus": false,
# #     "machineGrade": 2,
# #     "vipContentType": -1,
# #     "vipStartTime": -1,
# #     "vipEndTime": -1,
# #     "vipPrice": null,
# #     "viewCount": null,
# #     "termType": null,
# #     "compositeType": null,
# #     "parentName": null,
# #     "scheduleType": null,
# #     "advertiseSearchUuid": "0f162855-b337-4389-9511-e0c37f6ea741",
# #     "advertiseFlag": null,
# #     "webOneDesc": null,
# #     "categoryNames": null
# # },
#
#
# # url:https://study.163.com/course/introduction/1003271002.htm
#
# # https://study.163.com/dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr?1591424320919
# '''
# -------
# Request Payload:
#
# callCount=1
# scriptSessionId=${scriptSessionId}190
# httpSessionId=772c9d99af3e4802834d71d3cb45054d    ----从cookie的NTESSTUDYSI=获取
# c0-scriptName=PlanNewBean
# c0-methodName=getPlanCourseDetail
# c0-id=0
# c0-param0=string:1003271002     ----原链接中的id---从课程中获取productId
# c0-param1=number:0
# c0-param2=null:null
# batchId=1591424319380   ----毫秒级的时间戳
# '''
# '''
# ------
# Request Headers:
# :authority: study.163.com
# :method: POST
# :path: /dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr?1591424320919
# :scheme: https
# accept: */*
# accept-encoding: gzip, deflate, br
# accept-language: zh-CN,zh;q=0.9,ja;q=0.8
# content-length: 253
# content-type: text/plain
# cookie: _ntes_nnid=76410239530f84672f253871d9e50005,1590491808608; _ntes_nuid=76410239530f84672f253871d9e50005; NTESSTUDYSI=772c9d99af3e4802834d71d3cb45054d; EDUWEBDEVICE=b986ee343fd2412bbb999a3d5a76dd48; eds_utm=eyJjIjoiIiwiY3QiOiIiLCJpIjoiIiwibSI6IiIsInMiOiIiLCJ0IjoiIn0=|aHR0cHM6Ly93d3cuYmFpZHUuY29tL2xpbms/dXJsPW1Wc1oxNUZHdXNPdlRZYTc5bjk4N1RSeWFmeF91LWxjTXFxQzBiQ0twUk8md2Q9JmVxaWQ9OTZhY2RlYmEwMDA2NjNmMjAwMDAwMDAzNWVkNzllYjM=; hb_MA-BFF5-63705950A31C_source=www.baidu.com; __utmc=129633230; __utmz=129633230.1591323192.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; EDU-YKT-MODULE_GLOBAL_PRIVACY_DIALOG=true; CPS_REFERER=; NTES_STUDY_ORDER_NEW_CPS=400000000485142|2; utm=eyJjIjoiIiwiY3QiOiIiLCJpIjoiIiwibSI6IiIsInMiOiIiLCJ0IjoiIn0=|aHR0cHM6Ly9zdHVkeS4xNjMuY29tL2NvdXJzZS9pbnRyb2R1Y3Rpb24vMTAwMzIyMTAxOC5odG0=; __utma=129633230.1436456731.1591323192.1591417629.1591422986.8; STUDY_UUID=ff734b31-d7cd-4b41-8809-00a37bf88f72; __utmb=129633230.14.9.1591424261564; UTM_CPS=400000000485142|2
# origin: https://study.163.com
# providerid: 4713712
# referer: https://study.163.com/course/introduction.htm?courseId=1003271002
# sec-fetch-dest: empty
# sec-fetch-mode: cors
# sec-fetch-site: same-origin
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36
# '''

import requests,json
# 尝试请求
url = 'https://study.163.com/dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr'
headers = {
    ':authority': 'study.163.com',
    ':method': 'POST',
    ':path': '/dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr?1591424320919',
    ':scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8',
    'content-length': '253',
    'content-type': 'text/plain',
    'cookie': '_ntes_nnid=76410239530f84672f253871d9e50005,1590491808608; _ntes_nuid=76410239530f84672f253871d9e50005; NTESSTUDYSI=772c9d99af3e4802834d71d3cb45054d; EDUWEBDEVICE=b986ee343fd2412bbb999a3d5a76dd48; eds_utm=eyJjIjoiIiwiY3QiOiIiLCJpIjoiIiwibSI6IiIsInMiOiIiLCJ0IjoiIn0=|aHR0cHM6Ly93d3cuYmFpZHUuY29tL2xpbms/dXJsPW1Wc1oxNUZHdXNPdlRZYTc5bjk4N1RSeWFmeF91LWxjTXFxQzBiQ0twUk8md2Q9JmVxaWQ9OTZhY2RlYmEwMDA2NjNmMjAwMDAwMDAzNWVkNzllYjM=; hb_MA-BFF5-63705950A31C_source=www.baidu.com; __utmc=129633230; __utmz=129633230.1591323192.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; EDU-YKT-MODULE_GLOBAL_PRIVACY_DIALOG=true; CPS_REFERER=; NTES_STUDY_ORDER_NEW_CPS=400000000485142|2; utm=eyJjIjoiIiwiY3QiOiIiLCJpIjoiIiwibSI6IiIsInMiOiIiLCJ0IjoiIn0=|aHR0cHM6Ly9zdHVkeS4xNjMuY29tL2NvdXJzZS9pbnRyb2R1Y3Rpb24vMTAwMzIyMTAxOC5odG0=; __utma=129633230.1436456731.1591323192.1591417629.1591422986.8; STUDY_UUID=ff734b31-d7cd-4b41-8809-00a37bf88f72; __utmb=129633230.14.9.1591424261564; UTM_CPS=400000000485142|2',
    'origin': 'https://study.163.com',
    'providerid': '4713712',
    'referer': 'https://study.163.com/course/introduction.htm?courseId=1003271002',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
}
data_info0 = {
    'callCount': '1',
    'scriptSessionId': '${scriptSessionId}190',
    'httpSessionId': '772c9d99af3e4802834d71d3cb45054d',
    'c0-scriptName': 'PlanNewBean',
    'c0-methodName': 'getPlanCourseDetail',
    'c0-id': '0',
    'c0-param0': 'string: 1003271002',
    'c0-param1': 'number: 0',
    'c0-param2': 'null: null',
    'batchId': '1591424319380',
}
response = requests.post(url=url, headers=headers, data=json.dumps(data_info0))#,verify = False headers=headers
# response = requests.get(url=url, headers=headers)
print(response.text)












