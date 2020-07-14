from api_schema import concept_response_schema as response_schema
from bs4 import BeautifulSoup
import pymysql
import config
import json
from flask import jsonify



concept_codes = []

def connect_db():
	connection = pymysql.connect(host=config.DbDetails.host_name, database=config.DbDetails.db_name,
								 user=config.DbDetails.username,
								 password=config.DbDetails.password, port=config.DbDetails.port,
								 ssl={'ca': config.DbDetails.certificate_path})
	return connection.cursor(cursor=pymysql.cursors.DictCursor)


def create_parent_field(name, type, learn_path, entity_code):
	url = f"/study/{learn_path}-chapter?entity_code={entity_code}"
	return {
		"name": name,
		"type": type,
		"url": url
	}


def create_siblings_data(code, Type, title, seo_name, learn_path) -> dict:
	selected = True if code == entity_code else False
	return {
		"code": code,
		"type": Type,
		"name": title,
		"is_important": "true",
		"seo_subject_name": seo_name,
		"url": f"/study/{learn_path}-concept?entity_code={code}",
		"selected": selected
	},



# run join query and get all chapter codes for the concept code
# Expected output: a list containing all the concept_codes corresponding to the chapter_code
def get_chapter_codes(cursor, concept_code):
	query = f"SELECT chapter_code, code FROM {config.DbDetails.db_name}.{config.TableNames.knowledge_vectors} AS a JOIN {config.DbDetails.db_name}.{config.TableNames.chapter_concepts} as b on a.code = b.concept_code where code = '{concept_code}' and b.status = 'active';"
	cursor.execute(query)
	records = cursor.fetchall()
	if records:
		return [record['chapter_code'] for record in records]
	return None


# hit knowledge_vectors with all chapter codes, fill the parent and parents fields
def get_chapter_details(cursor, chapter_codes):
	query = f"SELECT * FROM {config.DbDetails.db_name}.{config.TableNames.knowledge_vectors} WHERE code IN {chapter_codes} and status='active';"
	cursor.execute(query)
	records = cursor.fetchall()
	return {each['code']:each for each in records}


def fill_parent_fields(chapter_details):
	global response_schema
	response_schema['data']['parent'] = create_parent_field(chapter_details[parent_chapter_code]['title'], 
			chapter_details[parent_chapter_code]['Type'], json.loads(chapter_details[parent_chapter_code]['kv_details'])['meta']['learn_path'], parent_chapter_code)
	parents = [create_parent_field(chapter_details[code]['title'], 
			chapter_details[code]['Type'], json.loads(chapter_details[code]['kv_details'])['meta']['learn_path'], code) for code in chapter_details.keys()]
	response_schema['data']['parents'] = parents
	parent_learnpath_code = chapter_details[parent_chapter_code]['learnpath_code'].split("--")
	response_schema['data']['learning_map']['exam_code'] = parent_learnpath_code[1]
	response_schema['data']['learning_map']['goal_code'] = parent_learnpath_code[0]


# take the first chapter code and get all the concept codes from chapter_concepts
def get_siblings_concept_codes(cursor):
	global concept_codes
	query = f"SELECT concept_code FROM {config.DbDetails.db_name}.{config.TableNames.chapter_concepts} WHERE chapter_code='{parent_chapter_code}' and status='active';"
	cursor.execute(query)
	records = cursor.fetchall()
	concept_codes = [each['concept_code'] for each in records]



# Get the derived and leading_to concept_codes from concept_edges
def get_derived_lead(cursor, entity_code):
	query = f"SELECT source_concept_code, dest_concept_code FROM {config.DbDetails.db_name}.{config.TableNames.concept_edges} WHERE source_concept_code='{entity_code}' or dest_concept_code='{entity_code}';"
	cursor.execute(query)
	records = cursor.fetchall()
	global derived, lead
	for record in records:
		if record['source_concept_code'] == entity_code:
			lead = record['dest_concept_code']
		if record['dest_concept_code'] == entity_code:
			derived = record['source_concept_code']

# finally hit knowledge_vectors and get all the details of concept_codes: fill data
def concept_codes_data(entity_code):
	codes = tuple(concept_codes + [derived, lead])
	query = f"SELECT * FROM {config.DbDetails.db_name}.{config.TableNames.knowledge_vectors} WHERE code in {codes};"
	cursor.execute(query)
	records = cursor.fetchall()
	records = {each['code']:each for each in records}
	fill_data(records)


def fill_data(records):
	siblings_data = []
	global response_schema
	for code in records.keys():

		if code == entity_code:
			fill_entity_code_data(records[entity_code])
			fill_kt_data(code,records[entity_code])
		if code in [derived, lead]:
			fill_kt_data(code, records[entity_code], records[code])
			continue
		meta = json.loads(records[code]['kv_details'])['meta']
		record = records[code]
		siblings_data.append(create_siblings_data(code, record['Type'], record['title'], meta['seo_friendly_subject_name'], meta['learn_path'])[0])
		response_schema['data']['siblings_data'] = siblings_data


def fill_kt_data(code, root_record, record=None):
	global response_schema
	if code == derived:
		meta = json.loads(record['kv_details'])['meta']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['from'] = code
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['to'] = entity_code
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['source'] = record['title']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['target'] = root_record['title']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['label'] = meta['concept_type']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['type'] = record['Type']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['seo_subject_name'] = meta['seo_friendly_subject_name']
		response_schema['data']['kt_data']['relation']['derived_from_links'][0]['concept_url'] = f'study/{meta["learn_path"]}-concept?entity_code={code}'
	elif code == lead:
		meta = json.loads(record['kv_details'])['meta']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['from'] = entity_code
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['to'] = code
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['source'] = root_record['title']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['target'] = record['title']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['label'] = meta['concept_type']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['type'] = record['Type']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['seo_subject_name'] = meta['seo_friendly_subject_name']
		response_schema['data']['kt_data']['relation']['leading_to_links'][0]['concept_url'] = f'study/{meta["learn_path"]}-concept?entity_code={code}'
	elif code == entity_code:
		meta = json.loads(root_record['kv_details'])['meta']
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['from'] = entity_code
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['source'] = root_record['title']
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['label'] = meta['concept_type']
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['type'] = root_record['Type']
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['seo_subject_name'] = meta['seo_friendly_subject_name']
		response_schema['data']['kt_data']['relation']['root_kt_node'][0]['concept_url'] = f'study/{meta["learn_path"]}-concept?entity_code={code}'


def fill_entity_code_data(record):
	global response_schema
	meta = json.loads(record['kv_details'])['meta']
	videos = json.loads(record['kv_details'])['details']['VIDEOS']
	response_schema['data']['code'] = record['code']
	response_schema['data']['type'] = record['Type']
	response_schema['data']['title'] = record['title']
	response_schema['data']['clean_title'] = BeautifulSoup(record['title'], "lxml").text
	response_schema['data']['description'] = record['description']
	response_schema['data']['relevant_exams'] = get_relevant_exams(tuple(json.loads(meta['relevant_exams'].replace("'", "\""))))
	response_schema['data']['relevant_skills'] = get_relevant_skills(tuple(json.loads(meta['nature_ids'].replace("'", "\""))))
	response_schema['data']['reference_links'] = get_reference_links()
	response_schema['data']['seo_subject_name'] = meta['seo_friendly_subject_name']
	response_schema['data']['wiki_friendly_name'] = meta['wiki_friendly_name']
	response_schema['data']['video_data'] = [{"url": each['url']} for each in videos]


def get_relevant_exams(exam_list):
	query = f"SELECT title from {config.DbDetails.db_name}.{config.TableNames.knowledge_vectors} WHERE code in {exam_list} and status='active';"
	cursor.execute(query)
	records = cursor.fetchall()
	return [each['title'] for each in records]


def get_relevant_skills(nature_ids):
	query = f"SELECT name from {config.DbDetails.db_name}.{config.TableNames.natures} where id in {nature_ids}"
	cursor.execute(query)
	records = cursor.fetchall()
	return [each['name'] for each in records]


def get_reference_links():
	query = f"SELECT url from {config.DbDetails.db_name}.{config.TableNames.concept_details} where concept_code='{entity_code}' and detail_type='REFERENCE_LINKS';"
	cursor.execute(query)
	records = cursor.fetchall()
	return [each['url'] for each in records]


def concept(code):
	global entity_code, parent_chapter_code, cursor, response_schema
	entity_code = code
	cursor = connect_db()
	chapter_codes = get_chapter_codes(cursor, entity_code)
	if chapter_codes:
		parent_chapter_code = chapter_codes[0]
		chapter_details = get_chapter_details(cursor, tuple(chapter_codes))
		fill_parent_fields(chapter_details)
		get_derived_lead(cursor, entity_code)
		get_siblings_concept_codes(cursor)
		concept_codes_data(entity_code)
		return jsonify(response_schema)
	return json.dumps({
	"success": False,
	"msg" : "Record not found"
	}, indent=4)