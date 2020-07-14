concept_response_schema = {
    "success": True,
    "data": {
        "status_code": "success",
        "code": "",
        "type": "",
        "title": "",
        "clean_title": "",
        "description": "",
        "relevant_exams": [],
        "relevant_skills": [],
        "reference_links": [],
        "parent": {},
        "parents": [],
        "learning_map": {
            "exam_code": "",
            "goal_code": ""
        },
        "siblings_data": [],
        "questions_rankers_got_wrong": {},
        "top_prev_year_question": {},
        "challenging_questions": {},
        "seo_subject_name": "",
        "wiki_friendly_name": "",
        "video_data": [],
        "kt_data": {
            "relation": {
                "derived_from_links": [
                    {
                        "source": "",
                        "target": "",
                        "from": "",
                        "to": "",
                        "label": "",
                        "type": "",
                        "seo_subject_name": "",
                        "concept_url": ""
                    }
                ],
                "leading_to_links": [
                    {
                        "source": "",
                        "target": "",
                        "from": "",
                        "to": "",
                        "label": "",
                        "type": "",
                        "seo_subject_name": "",
                        "concept_url": ""
                    }
                ],
                "root_kt_node": [
                    {
                        "source": "",
                        "target": "",
                        "from": "",
                        "to": "",
                        "label": "",
                        "seo_subject_name": "",
                        "type": "",
                    }
                ]
            }
        }
    }
}


chapter_response_schema = {
    "success": True,
    "data": {
        "title": "",
        "clean_title": "",
        "description": "",
        "type":"chapters",
        "seo_subject_name": "",
        "wiki_friendly_name": "",
        "learning_map": {
            "goal_code": "",
            "exam_code": "",
            "subject_code": "",
            "unit_code": "",
            "chapter_code": ""
        }
    }
}

unit_response_schema = {
    "success": True,
    "data": {
        "title": "",
        "clean_title": "",
        "type":"units",
        "description": "",
        "seo_subject_name": "",
        "wiki_friendly_name": "",
        "learning_map": {
            "goal_code": "",
            "exam_code": "",
            "subject_code": "",
            "unit_code": ""
        }
    }
}

subject_response_schema = {
    "success": True,
    "data": {
        "title": "",
        "clean_title": "",
        "type":"subjects",
        "description": "",
        "seo_subject_name": "",
        "wiki_friendly_name": "",
        "learning_map": {
            "goal_code": "",
            "exam_code": "",
            "subject_code": ""
        }
    }
}