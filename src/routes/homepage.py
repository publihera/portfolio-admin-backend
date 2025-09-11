from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.project import db
from src.models.homepage import HomePage

homepage_bp = Blueprint("homepage", __name__)

@homepage_bp.route("/homepage", methods=["GET"])
def get_homepage_content():
    homepage_data = HomePage.query.first()
    if not homepage_data:
        return jsonify({"message": "No homepage content found"}), 404

    return jsonify({
        "logo_url": homepage_data.logo_url,
        "nav_links_json": homepage_data.nav_links_json,
        "main_title": homepage_data.main_title,
        "slogan": homepage_data.slogan,
        "rotating_keywords_json": homepage_data.rotating_keywords_json,
        "nascido_em_sp_title": homepage_data.nascido_em_sp_title,
        "nascido_em_sp_quote": homepage_data.nascido_em_sp_quote,
        "best_practices_title": homepage_data.best_practices_title,
        "emotion_driven_title": homepage_data.emotion_driven_title,
        "services_json": homepage_data.services_json,
        "good_at_title": homepage_data.good_at_title,
        "good_at_intro": homepage_data.good_at_intro,
        "clients_json": homepage_data.clients_json,
        "partners_title": homepage_data.partners_title,
        "partners_json": homepage_data.partners_json,
        "cta_title": homepage_data.cta_title,
        "cta_subtitle": homepage_data.cta_subtitle,
        "cta_button_text": homepage_data.cta_button_text,
        "header_bg_color": homepage_data.header_bg_color,
        "section_1_bg_image_url": homepage_data.section_1_bg_image_url,
    })

@homepage_bp.route("/homepage", methods=["PUT"])
@jwt_required()
def update_homepage_content():
    data = request.get_json()
    homepage_data = HomePage.query.first()

    if not homepage_data:
        homepage_data = HomePage()
        db.session.add(homepage_data)

    homepage_data.logo_url = data.get("logo_url", homepage_data.logo_url)
    homepage_data.nav_links_json = data.get("nav_links_json", homepage_data.nav_links_json)
    homepage_data.main_title = data.get("main_title", homepage_data.main_title)
    homepage_data.slogan = data.get("slogan", homepage_data.slogan)
    homepage_data.rotating_keywords_json = data.get("rotating_keywords_json", homepage_data.rotating_keywords_json)
    homepage_data.nascido_em_sp_title = data.get("nascido_em_sp_title", homepage_data.nascido_em_sp_title)
    homepage_data.nascido_em_sp_quote = data.get("nascido_em_sp_quote", homepage_data.nascido_em_sp_quote)
    homepage_data.best_practices_title = data.get("best_practices_title", homepage_data.best_practices_title)
    homepage_data.emotion_driven_title = data.get("emotion_driven_title", homepage_data.emotion_driven_title)
    homepage_data.services_json = data.get("services_json", homepage_data.services_json)
    homepage_data.good_at_title = data.get("good_at_title", homepage_data.good_at_title)
    homepage_data.good_at_intro = data.get("good_at_intro", homepage_data.good_at_intro)
    homepage_data.clients_json = data.get("clients_json", homepage_data.clients_json)
    homepage_data.partners_title = data.get("partners_title", homepage_data.partners_title)
    homepage_data.partners_json = data.get("partners_json", homepage_data.partners_json)
    homepage_data.cta_title = data.get("cta_title", homepage_data.cta_title)
    homepage_data.cta_subtitle = data.get("cta_subtitle", homepage_data.cta_subtitle)
    homepage_data.cta_button_text = data.get("cta_button_text", homepage_data.cta_button_text)
    homepage_data.header_bg_color = data.get("header_bg_color", homepage_data.header_bg_color)
    homepage_data.section_1_bg_image_url = data.get("section_1_bg_image_url", homepage_data.section_1_bg_image_url)

    db.session.commit()
    return jsonify({"message": "Homepage content updated successfully"}))

