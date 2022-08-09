import re
from datetime import datetime, timedelta


# 􏰥􏰦 Nginx 􏰧􏰨􏰩􏰪􏰫􏰬􏰞􏰭􏰮1000􏰯􏰰􏰄􏰱􏰲􏰣􏰰􏰀􏰳􏰴 服务器日志文件大约1000w行，其中一行如下
# 47.29.201.179 - - [28/Feb/2019:13:17:10 +0000] "GET /?p=1 HTTP/2.0" 200 5316 "https://domain1.com/?p=1" "Mozilla/5.0 (Window s NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36" "2.75"

# 统计指标
# 计算HTTPS请求多少个是以domain1.com 为域名
# 给定日期 Date，根据HTTP状态码 计算当日 UTC0 所有请求中成功的比例

class NginxLogExtract:

	def __init__(self, log_path=None, query_date=None):
		self.query_date = query_date
		self.log_path = log_path

	def log_load(self):
		with open(self.log_path, 'r') as file:
			lines = file.readlines()
		return lines

	def log_extract(self, line: str):
		pattern = '''(?P<remote_addr>[\d\.]{7,}) - - (?:\[(?P<datetime>[^\[\]]+)\]) "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<referer>.*?)" "(?P<user_agent>[^"]+)"'''
		comp = re.compile(pattern)
		matcher = comp.match(line)
		log_factors = matcher.groupdict()
		return log_factors

	def cnt_domain(self, lines: list):
		cnt = 0
		for line in lines:
			log_factors = self.log_extract(line)
			if log_factors.get("referer", "").startswith("https://domain1.com"):
				cnt += 1
		return cnt

	def cnt_success(self, lines: list):
		date_req_sum = 0
		date_req_success_sum = 0
		query_datetime = datetime.strptime(self.query_date, '%Y-%m-%d')

		for line in lines:
			log_factors = self.log_extract(line)
			log_date_str = log_factors.get("datetime", "").split('+')[0].strip()
			log_datetime = datetime.strptime(log_date_str, '%d/%b/%Y:%H:%M:%S')
			if (log_datetime - query_datetime).days == 0:
				date_req_sum += 1
				if log_factors.get("status", "0") == "200":
					date_req_success_sum += 1
		return (date_req_sum, date_req_success_sum)

	def task_run(self):
		if self.log_path:
			lines = self.log_load()
			domain_cnt = self.cnt_domain(lines)
			print("有 " + str(domain_cnt) + " 个是以 domain.com 为域名的")

			if self.query_date:
				res_tuple = self.cnt_success(lines)
				if res_tuple[0]:
					success_rate = res_tuple[1] * 1.0 / res_tuple[0]
					print(f"{self.query_date} 中，所有请求数为{res_tuple[0]}个，成功{res_tuple[1]}个, 成功比例为{success_rate}")
				else:
					print(f"{self.query_date} 中，所有请求数为0 ")


app = NginxLogExtract(log_path='./log.txt', query_date='2019-02-28')
app.task_run()
