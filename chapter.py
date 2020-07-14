from api_schema import chapter_response_schema as response_schema
import pymysql
import config
from flask import jsonify
from bs4 import BeautifulSoup
import json


def connect_db():
	connection = pymysql.connect(host=config.DbDetails.host_name, database=config.DbDetails.db_name,
								 user=config.DbDetails.username,
								 password=config.DbDetails.password, port=config.DbDetails.port,
								 ssl={'ca': config.DbDetails.certificate_path})
	return connection.cursor(cursor=pymysql.cursors.DictCursor)


def get_data_from_db(code):
	cursor = connect_db()
	query = f"SELECT * FROM {config.DbDetails.db_name}.{config.TableNames.knowledge_vectors} where code='{code}' and type='chapters';"
	cursor.execute(query)
	record = cursor.fetchone()
	if record:
			return record
	return None


def fill_learning_map(learnpath_code):
	goal_code, exam_code, subject_code, unit_code, chapter_code = learnpath_code.split("--")
	global response_schema
	response_schema['data']['learning_map']['goal_code'] = goal_code
	response_schema['data']['learning_map']['exam_code'] = exam_code
	response_schema['data']['learning_map']['subject_code'] = subject_code
	response_schema['data']['learning_map']['unit_code'] = unit_code
	response_schema['data']['learning_map']['chapter_code'] = chapter_code



def fill_response_schema(data):
	global response_schema
	meta = json.loads(data['kv_details'])['meta']
	response_schema['data']['title'] = data['title']
	response_schema['data']['clean_title'] = BeautifulSoup(data['title'], "lxml").text
	response_schema['data']['seo_subject_name'] = meta['seo_friendly_subject_name']
	response_schema['data']['wiki_friendly_name'] = meta['wiki_friendly_name']
	response_schema['data']['description'] = data['description']
	fill_learning_map(data['learnpath_code'])



def chapter(code):
	cursor = connect_db()
	global response_schema
	data = get_data_from_db(code)
	if data:
		fill_response_schema(data)
		return jsonify(response_schema)
	return json.dumps({
	"success": False,
	"msg" : "Record not found"
	}, indent=4)