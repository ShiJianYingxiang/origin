path_program=$(cd `dirname $0`; pwd)
str_production='production'


ps aux | grep main_amazon | awk '{print $2}'|xargs kill -9
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &
nohup python $path_program/main_amazon_list_spider.py 2>&1 &


