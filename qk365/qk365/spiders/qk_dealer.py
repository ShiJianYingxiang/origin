# -*- coding: utf-8 -*-
'''

'''
import scrapy
import re
import math
import json
import time
from qk365.items import Qk365Item
from qk365.items import Qk365DealerItem
from qk365.items import Qk365CommunityItem

from urllib import parse

class QkHotelSpider(scrapy.Spider):
    name = 'qk_dealer_hotel'
    # allowed_domains = ['qk365.com']
    # start_urls = ['https://www.qk365.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; KIW-AL10 Build/HONORKIW-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm64',

    }
    headers1 = {
        "Host": "mp.qk365.com",
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; KIW-AL10 Build/HONORKIW-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm64',
        'content-type': 'application/json',
    }
    item = Qk365Item()
    dealeritem = Qk365DealerItem()
    communityitem = Qk365CommunityItem()
    dealer_url = "https://tj.qk365.com/ajaxTitleHouseManager.do"
    room_url = "https://mp.qk365.com/room/queryRoomDetail"
    # roomid_set = set()
    def start_requests(self):
        dealer_id_list = [4731, 13046, 11361, 15940, 16579, 7640, 5143, 10801, 4820, 3847, 3603, 15820, 16236, 11878, 6446, 1491, 12986,
         5688, 15658, 15653, 4519, 15992, 4677, 15038, 7706, 11874, 15356, 17057, 1278, 4352, 10745, 13976, 12366,
         17103, 10265, 13898, 15100, 5838, 16448, 3630, 5113, 6698, 14773, 4485, 2273, 4746, 1523, 16531, 17115, 8934,
         5730, 3882, 17414, 14207, 6177, 12901, 2427, 16537, 11342, 10181, 15236, 1603, 14669, 2513, 11593, 1954, 16130,
         16144, 11211, 15809, 10620, 918, 14985, 8424, 5255, 7823, 15382, 13805, 11201, 12914, 12291, 3628, 1697, 14637,
         14297, 4311, 4809, 13830, 15611, 9222, 2022, 4701, 4423, 4578, 15257, 11287, 4884, 1518, 6931, 16974, 14214,
         8275, 5415, 13146, 13661, 16134, 13067, 16096, 13069, 17090, 16174, 15725, 11297, 16613, 12445, 14258, 11982,
         15875, 5753, 12778, 1002, 14554, 3624, 3124, 3565, 13869, 6431, 7966, 7223, 14046, 16106, 1229, 14692, 14597,
         2500, 13475, 5830, 16079, 4581, 2822, 9233, 16855, 8473, 3981, 15728, 4765, 15679, 6716, 9525, 10559, 1647,
         16250, 17193, 15084, 11038, 12209, 4539, 15352, 4253, 16053, 10596, 12674, 17004, 16561, 3986, 1276, 3917,
         14585, 4349, 15470, 16583, 14740, 2550, 5335, 5423, 13963, 15483, 15027, 4217, 16891, 4048, 6808, 7817, 15994,
         16185, 3229, 5210, 5843, 14576, 999, 1601, 17111, 14780, 8199, 9468, 14486, 5543, 15258, 17095, 11158, 17105,
         3542, 6957, 6519, 15325, 220, 12755, 4276, 15541, 17227, 14862, 1213, 6337, 1347, 11360, 5222, 5667, 15175,
         1709, 13993, 6444, 9234, 16239, 12915, 16795, 14735, 14836, 2829, 2930, 6443, 15265, 16220, 9570, 5258, 16001,
         12760, 14011, 13932, 12349, 916, 17251, 989, 4214, 1665, 12612, 16742, 11629, 17281, 14801, 7386, 16996, 15794,
         15624, 11249, 3557, 1600, 2755, 16508, 8615, 16971, 4588, 16643, 16536, 15293, 3787, 15001, 15109, 2354, 6643,
         14616, 3364, 16715, 14792, 15250, 3282, 9139, 6362, 5030, 11215, 16683, 14663, 13961, 15207, 16739, 12137,
         14510, 12903, 15701, 1677, 2231, 14079, 17036, 17381, 3914, 4821, 14114, 1287, 15676, 17122, 16526, 15887,
         6830, 8620, 6960, 14135, 5367, 15885, 3053, 17293, 6216, 13014, 4890, 14598, 17072, 15275, 5452, 12477, 14872,
         6058, 16889, 15666, 16647, 4835, 2217, 15812, 8732, 15165, 14770, 16112, 12626, 17472, 9635, 16463, 4804,
         13853, 1727, 1562, 16915, 15291, 6553, 7709, 3495, 5223, 16973, 4136, 1413, 5998, 6324, 16681, 1285, 2813,
         2454, 16539, 12920, 7505, 12600, 15952, 9024, 15599, 10949, 14362, 16675, 16533, 15849, 14160, 15639, 2908,
         16684, 2535, 17118, 8008, 15673, 14948, 16874, 9178, 2133, 15172, 4398, 11142, 11569, 1038, 8272, 14645, 3558,
         15042, 15040, 15269, 16609, 12657, 14105, 15248, 11466, 1515, 15742, 15752, 5373, 922, 14719, 1536, 16813,
         5333, 14739, 3832, 14668, 4862, 10992, 16167, 5905, 14756, 2543, 15300, 5361, 3443, 13919, 10226, 5022, 1345,
         17216, 17164, 5889, 15320, 5390, 2841, 3164, 12273, 13525, 5625, 16866, 5339, 15458, 6653, 16661, 9167, 5840,
         16501, 15739, 15013, 15930, 12646, 1224, 17246, 14650, 15508, 2352, 16596, 10465, 17002, 16097, 16589, 17231,
         17079, 8170, 2824, 17226, 5445, 12111, 1605, 16716, 5926, 15523, 12956, 4518, 16165, 11720, 8368, 16189, 14730,
         4019, 6314, 14406, 4131, 6315, 16938, 4162, 16182, 14874, 16937, 17285, 6766, 4289, 3014, 16945, 2335, 14363,
         10606, 15706, 4347, 17081, 2516, 11671, 15763, 16191, 5050, 2245, 2525, 2491, 1257, 16988, 5353, 8045, 11251,
         16914, 1470, 15225, 6786, 16585, 1546, 15400, 2098, 10484, 13719, 15185, 4958, 7757, 5372, 12261, 12003, 2518,
         15058, 16924, 14333, 14129, 17117, 16449, 2524, 7258, 17067, 11325, 2529, 6128, 7681, 2456, 16493, 11299,
         16218, 3144, 16816, 12566, 13703, 10901, 15586, 16608, 16670, 11999, 14290, 2455, 12945, 17410, 11194, 9346,
         4206, 17143, 16451, 16671, 7894, 10963, 13769, 1283, 16836, 1948, 13152, 2101, 8713, 4606, 17120, 3968, 4514,
         2953, 13803, 15467, 2257, 4913, 16032, 1379, 15086, 10612, 16051, 14733, 4786, 14642, 13811, 15560, 3299, 3161,
         13968, 10394, 3833, 14159, 16926, 16321, 15691, 1602, 17154, 8088, 13956, 4812, 16682, 17017, 5376, 5444,
         14656, 7298, 982, 3991, 1252, 14030, 4792, 13902, 6517, 15525, 14519, 17373, 1191, 8604, 1304, 15213, 14285,
         17141, 16629, 11828, 16766, 15093, 3757, 2063, 3450, 5583, 10428, 1220, 4796, 13589, 15316, 13863, 14687,
         11997, 3269, 3856, 15363, 14099, 921, 15721, 16649, 13745, 3458, 10191, 11164, 7296, 17153, 97, 7601, 4123,
         17198, 2731, 15589, 11267, 3888, 11385, 12164, 15026, 2351, 16498, 6638, 3908, 16039, 15572, 14324, 985, 17056,
         15957, 14032, 2432, 14998, 13807, 10851, 16610, 11218, 10987, 10237, 7448, 4816, 3684, 2452, 14764, 15883,
         15008, 14422, 14540, 6096, 16139, 5011, 5977, 12195, 17142, 2331, 15450, 2189, 7016, 15442, 17302, 16446,
         15446, 13988, 14190, 15901, 16888, 5352, 16548, 17402, 11117, 4334, 15747, 12961, 11951, 4736, 13454, 2903,
         15574, 15039, 1823, 17172, 6321, 16233, 3669, 2548, 1110, 16962, 15713, 14857, 15771, 2261, 14675, 3261, 15420,
         7311, 16799, 2556, 1221, 14632, 15788, 16599, 14944, 1435, 17191, 4888, 16590, 14975, 14222, 16824, 1730, 1384,
         13626, 17070, 5580, 17394, 4583, 16574, 11207, 14204, 4058, 16932, 15361, 17089, 1352, 16822, 13214, 5969,
         17003, 5160, 11896, 3724, 7907, 17133, 1728, 6316, 17012, 13681, 14334, 15011, 15, 13800, 17129, 17107, 16607,
         15401, 15242, 6020, 12730, 16188, 4197, 11834, 1616, 11442, 5651, 16651, 17161, 16851, 3070, 14097, 13059,
         5614, 16518, 15630, 14714, 11365, 1412, 2460, 7985, 16861, 5773, 16318, 14023, 5512, 2486, 14749, 1389, 5184,
         17062, 11623, 16021, 2262, 15246, 7377, 13773, 4819, 3899, 14717, 15411, 11884, 2140, 16067, 2338, 13611,
         13798, 1668, 17128, 12865, 12150, 2749, 5665, 3997, 15712, 11192, 11767, 986, 14419, 10398, 16685, 17215,
         15568, 17000, 16901, 4827, 17140, 9100, 2523, 4085, 2876, 12780, 3271, 3516, 16207, 16511, 3099, 2827, 16547,
         15099, 13622, 15437, 16322, 16546, 16474, 13529, 2260, 15582, 2961, 8770, 14686, 6127, 16171, 15939, 3215,
         16913, 15765, 14697, 11930, 3851, 8595, 16520, 14542, 7366, 15003, 10624, 9556, 7089, 15177, 1680, 11691, 4777,
         14785, 14688, 4524, 16486, 11822, 16586, 11491, 16575, 16057, 15457, 15881, 16789, 10168, 12218, 2426, 4511,
         16277, 12114, 3918, 14830, 12820, 3877, 7777, 12062, 3768, 9297, 14013, 4721, 17351, 9686, 8133, 5296, 1263,
         3550, 16981, 4406, 2935, 16606, 6461, 10499, 5232, 15662, 3947, 6276, 14755, 16262, 5588, 16688, 4526, 8340,
         4161, 8250, 16471, 15971, 2558, 2777, 14503, 15872, 4920, 6386, 9144, 13020, 5469, 12047, 16099, 14873, 14472,
         13396, 16276, 11574, 11484, 4923, 3170, 17085, 9347, 8209, 3274, 15532, 3265, 10405, 14768, 5362, 15221, 16196,
         14647, 15588, 14751, 5684, 14734, 17145, 11301, 4462, 17006, 5906, 17267, 16885, 14421, 15648, 14906, 11960,
         1248, 10618, 10380, 15766, 9467, 4517, 3883, 13437, 12042, 16164, 5953, 15831, 15743, 14367, 16720, 2310,
         10411, 15719, 8415, 12356, 9208, 7158, 2877, 11713, 4513, 17395, 17201, 16823, 14563, 12727, 10945, 6711,
         14808, 2339, 6410, 1971, 4675, 16530, 13885, 17228, 4147, 15184, 14961, 14806, 6015, 6452, 15469, 10585, 17213,
         1235, 13669, 14920, 5758, 13975, 3519, 2537, 12160, 10044, 17301, 10883, 15334, 15251, 14720, 15959, 12881,
         4818, 1364, 12211, 15942, 7775, 12416, 1222, 16646, 13937, 2254, 1959, 4205, 16093, 2268, 15877, 17040, 15247,
         14869, 12794, 4338, 6363, 16621, 17189, 17239, 14771, 990, 4646, 7012, 1357, 17266, 15923, 7635, 3771, 3676,
         15751, 9165, 11402, 12692, 14504, 11857, 3562, 16676, 3948, 14617, 15583, 16950, 15749, 2347, 11115, 2413,
         15549, 11223, 7139, 12659, 3976, 2417, 9316, 16157, 15716, 12362, 17104, 11876, 2306, 11950, 14578, 14641,
         3828, 1475, 11682, 16808, 2816, 17236, 17157, 4417, 11757, 11716, 4165, 13757, 5299, 5531, 7785, 14025, 17144,
         14140, 16232, 15909, 9065, 14811, 14223, 17175, 13772, 15377, 3979, 17197, 10931, 14177, 3400, 3744, 16678,
         13438, 12196, 14498, 1040, 10556, 15513, 9121, 11483, 6962, 14702, 13812, 13802, 13786, 14154, 1426, 14689,
         16138, 4251, 10193, 13672, 1253, 1953, 16984, 5055, 16519, 7380, 16710, 12489, 14026, 5442, 2871, 14594, 15301,
         12199, 14883, 15326, 16255, 14929, 61, 4096, 16497, 15873, 16997, 16972, 12757, 15020, 15795, 11770, 5796,
         17411, 16772, 1815, 15022, 14646, 7423, 2559, 14683, 11347, 7838, 17212, 15722, 1455, 12044, 5456, 14791,
         17073, 1411, 4801, 13677, 13881, 1657, 11110, 6347, 15949, 13009, 17221, 7986, 16538, 2773, 5623, 5051, 2916,
         15727, 15035, 17363, 16192, 15631, 14775, 17249, 3068, 7972, 13784, 2034, 1686, 2176, 3977, 12733, 15388, 9425,
         9705, 15681, 16995, 1396, 4712, 2767, 2333, 9266, 3239, 13621, 6187, 1835, 14583, 17247, 12156, 13867, 14932,
         12081, 6147, 17114, 16246, 7977, 7463, 14053, 13663, 2081, 14890, 4184, 13186, 1272, 4218, 15542, 5021, 8102,
         3797, 2453, 10099, 1170, 15545, 17492, 3428, 10950, 10511, 14725, 15176, 4238, 10337, 17112, 16712, 17195,
         3160, 1273, 1687, 15466, 8643, 14553, 5779, 16071, 16135, 16107, 17297, 17034, 15634, 1012, 15495, 16983,
         15477, 15830, 10978, 2993, 10408, 11050, 14798, 14477, 15374, 15194, 8331, 11078, 16168, 8555, 14083, 16226,
         1563, 16626, 14897, 6853, 17385, 1351, 15839, 1658, 5377, 14794, 15399, 10902, 13086, 10818, 13668, 3549,
         13552, 1729, 15504, 16927, 4681, 16740, 14623, 5480, 3843, 11832, 5385, 3698, 15950, 6380, 5259, 4370, 1517,
         16826, 15581, 15452, 12168, 15854, 13103, 5626, 4174, 15271, 15796, 15179, 2863, 15521, 4441, 15208, 16730,
         16256, 7956, 10239, 12148, 11677, 17420, 14911, 14070, 14879, 17217, 11497, 2102, 8966, 14820, 14949, 5151,
         16598, 10792, 15383, 16961, 16004, 15272, 4071, 10623, 3444, 16523, 2199, 1105, 7715, 15222, 12898, 16066,
         15680, 14708, 9728, 14600, 15380, 16055, 6240, 1696, 1327, 8712, 4911, 15370, 12415, 4979, 17250, 10581, 10746,
         5302, 12680, 1789, 11816, 16723, 14848, 15481, 16500, 14653, 14412, 4350, 16056, 1284, 9399, 11760, 14221,
         2748, 16759, 13864, 14602, 11302, 14950, 15068, 15914, 16726, 14682, 12083, 1667, 16943, 2853, 15187, 2750,
         15256, 11246, 12138, 17001, 12932, 13175, 15629, 3544, 12382, 9069, 2033, 14090, 16992, 10991, 5777, 14346,
         14715, 13813, 11190, 3038, 11627, 13783, 11398, 3092, 2316, 15960, 4893, 7561, 15162, 14168, 3414, 2476, 3051,
         17323, 17438, 12761, 10163, 16031, 5618, 3112, 15976, 2136, 13855, 17462, 13084, 6580, 15002, 16259, 15622,
         16234, 14721, 4694, 13892, 14903, 2885, 4737, 14666, 16663, 6101, 7759, 16944, 15124, 8837, 7499, 12259, 11981,
         1664, 14441, 14420, 16145, 15717, 14545, 3858, 12567, 17375, 3963, 15404, 8025, 14971, 11068, 13397, 15461,
         5441, 9385, 14910, 6581, 11160, 8851, 16269, 14471, 15941, 12384, 8716, 2497, 15324, 11464, 16963, 11416, 5909,
         4000, 11463, 14728, 15932, 11829, 13828, 11377, 15239, 8044, 16750, 7438, 1617, 3231, 9427, 3141, 3656, 3712,
         9175, 15845, 12917, 10604, 16156, 15206, 14564, 16872, 3930, 14103, 16040, 5167, 8768, 5670, 16327, 10262,
         8037, 4684, 11362, 3618, 11854, 17319, 16070, 11735, 14630, 11447, 3345, 14502, 11446, 16454, 4541, 15938]

        for dealer_id in dealer_id_list:
        # dealer_id = '10237'   #获取所有的经纪人id
            data = {
                'currentPage': '1',
                'index': 'a',
                'adminid': dealer_id,
                'searchColumn': '',
            }
            data = parse.urlencode(data)
            yield scrapy.Request(url=self.dealer_url, headers=self.headers, body=data, meta={'dealer_id': dealer_id}, method='post', callback=self.parse)


            # https://www.qk365.com/ajaxHouserInfo.do?romAdminId=13919
            old_dealer_url = 'https://www.qk365.com/ajaxHouserInfo.do?romAdminId=%s'%dealer_id
            yield scrapy.Request(url=old_dealer_url, headers=self.headers, meta={'dealer_id': dealer_id}, callback=self.old_dealer_info)
            # yield scrapy.Request(url=,)
        # https: // www.qk365.com / roomAdmin / 15622

    def parse(self,response):
        dealer_id = response.meta.get('dealer_id', '')
        # 获取经纪人下房源数的最大页数
        next_page_num_href = response.xpath('''(//div[@class="paging"]//ul//li/a)[last()]/@href''').get()
        next_page_num = re.search('(\d+)', next_page_num_href).group()  #获取总页数
        for page in range(1, int(next_page_num)+1):  #翻页发送
            data = {
                'currentPage': page,
                'index': 'a',
                'adminid': dealer_id,
                'searchColumn': '',
            }
            data = parse.urlencode(data)
            yield scrapy.Request(url=self.dealer_url, headers=self.headers, body=data, method='post',
                                 callback=self.get_all_roomid)

    def get_all_roomid(self, response):
        '''获取所有房子的id'''
        roomid_list = response.xpath('''//div[@id="houseRight"]//ul[@class="easyList keeperList"]//li/a/@href''').getall()

        for room_id_temp in roomid_list:
            room_id = re.search('room/(\d+)', room_id_temp).group(1)
            if room_id:
                data = {'roomId': room_id}   #小程序入口比APP多一些字段，发送所有房屋的详情请求
                yield scrapy.Request(url=self.room_url, headers=self.headers1, body=json.dumps(data), meta={"room_id":room_id}, method='post', callback=self.parse_detail_roomid)

                room_url = 'https://www.qk365.com/room/%s' % str(room_id)  #获取小区信息和房管员信息
                yield scrapy.Request(url=room_url, headers=self.headers, meta={'roomId': room_id}, callback=self.pc_room_detail)

    def parse_detail_roomid(self,response):
        data = json.loads(response.text).get('data', '')
        page_roomid = response.meta.get('room_id', '')
        roomid = data.get('roomId', '')

        if not roomid:
            self.logger.error(page_roomid)
        else:
            self.item['crawl_source'] = 'dealer'
            for temp_key, temp_value in data.items():
                self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.item[temp_key] = temp_value
                if temp_key == 'ceaId':
                    self.item['ceaId'] = 'k' + str(data.get('ceaId', ''))
                if temp_key == 'prcId':
                    self.item['prcId'] = 'a' + str(data.get('prcId', ''))
                if temp_key == 'villageId':
                    self.item['villageId'] = 'v' + str(data.get('villageId', ''))
                if temp_key == 'rentDateName':
                    rent_status = data.get('rentDateName', '')
                    #print(rent_status, '--------', type(rent_status))
                    if rent_status:
                        if '立即' in rent_status:
                            self.item['rent_status'] = '待租'
                        else:
                            self.item['rent_status'] = '已租'
            yield self.item


    def pc_room_detail(self, response):
        '''============公有的====================='''
        roomid = response.meta.get('roomid', '')
        region = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/text()''').get()  #房山区

        region_id_content = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/@href''').get()  # 需要正则

        if region_id_content:
            region_id = re.search('list/(\w+\d+)', region_id_content).group(1)
        else:
            return
        district = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[2]/text()''').get()  #地区
        district_id_content = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[2]/@href''').get()  # 需要正则
        if district_id_content:
            district_id = re.search('-(\w+\d+)', district_id_content).group(1)
        else:
            district_id = ''


        detail_url = response.xpath('''//p[@class="stewPhotName"]//a/@href''').get()  #房管员url---id
        dealer_code = response.xpath('''//input[@id="romAdminId"]/@value''').get()  #房管员id
        dealer_name = response.xpath('''//p[@class="stewPhotName"]//a/text()''').get()   #房管员名称---房管员：刘英迪1
        dealer_name = str(dealer_name).replace('房管员：', '').strip()
        rent_turnover_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[last()]/text()''').get()  #8间
        rent_house_count_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[1]/text()''').get()  #127间
        service_people_count_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[2]/text()''').get()  #36人
        try:
            rent_turnover = re.search('\d+', rent_turnover_content).group() if rent_turnover_content else 0
        except:
            rent_turnover = 0
        try:
            rent_house_count = re.search('\d+', rent_house_count_content).group() if rent_house_count_content else 0
        except:
            rent_house_count = 0
        try:
            service_people_count = re.search('\d+', service_people_count_content).group() if service_people_count_content else 0
        except:
            service_people_count = 0
        self.dealeritem['roomId'] = roomid
        self.dealeritem['region'] = region
        self.dealeritem['region_id'] = region_id
        self.dealeritem['district'] = district
        self.dealeritem['district_id'] = district_id
        self.dealeritem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.dealeritem['detail_url'] = detail_url
        self.dealeritem['dealer_code'] = dealer_code
        self.dealeritem['dealer_name'] = dealer_name
        self.dealeritem['rent_turnover'] = rent_turnover
        self.dealeritem['rent_house_count'] = rent_house_count
        self.dealeritem['service_people_count'] = service_people_count
        yield self.dealeritem
        # ###############################
        community_code_content = response.xpath('''//div[@class="survey-left fL"]//dd/a/@href''').get()  #
        if community_code_content:
            community_code = re.search('xiaoqu/(\w+\d+)', community_code_content).group(1)    #小区id
        else:
            community_code = ''
        community_name = response.xpath('''//div[@class="survey-left fL"]//dd/a/text()''').get()  # 小区名称
        longitude = response.xpath('''//input[@id="cucLongitude"]/@value''').get()  # 经度
        latitude = response.xpath('''//input[@id="cucLatitude"]/@value''').get()  # 纬度
        self.communityitem['roomId'] = roomid
        self.communityitem['region'] = region
        self.communityitem['region_id'] = region_id
        self.communityitem['district'] = district
        self.communityitem['district_id'] = district_id
        self.communityitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.communityitem['community_code'] = community_code
        self.communityitem['community_name'] = community_name
        self.communityitem['longitude'] = longitude
        self.communityitem['latitude'] = latitude
        yield self.communityitem


    def old_dealer_info(self,response):
        dealer_id = response.meta.get('dealer_id', '')
        print(dealer_id,'=================')
        dealer_name = response.xpath('''//div[@class="manage-pep"]//h3/text()''').get()
        dealer_name = str(dealer_name).replace('房管员：', '').strip()
        rent_turnover_content = response.xpath('''(//div[@class="manage-pep"]//p//span)[2]/i''').get()
        rent_house_count_content = response.xpath('''(//div[@class="manage-pep"]//p//span)[1]/i''').get()
        service_people_count_content = response.xpath('''//div[@class="manage-pep"]//p//em/i''').get()
        try:
            rent_turnover = re.search('\d+', rent_turnover_content).group() if rent_turnover_content else 0
        except:
            rent_turnover = 0
        try:
            rent_house_count = re.search('\d+', rent_house_count_content).group() if rent_house_count_content else 0
        except:
            rent_house_count = 0
        try:
            service_people_count = re.search('\d+', service_people_count_content).group() if service_people_count_content else 0
        except:
            service_people_count = 0
        self.dealeritem['region'] = 'search'
        self.dealeritem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.dealeritem['detail_url'] = response.url
        self.dealeritem['dealer_code'] = dealer_id
        self.dealeritem['dealer_name'] = dealer_name
        self.dealeritem['rent_turnover'] = rent_turnover
        self.dealeritem['rent_house_count'] = rent_house_count
        self.dealeritem['service_people_count'] = service_people_count
        yield self.dealeritem