from src.models.project import db

class HomePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Logo
    logo_url = db.Column(db.String(255), nullable=True)

    # Links de Navegação (armazenados como JSON ou string serializada)
    # Para simplificar, vamos armazenar como string JSON. No frontend, você fará o parse.
    nav_links_json = db.Column(db.Text, nullable=True) # Ex: '[{"text": "Home", "url": "/"}, {"text": "Portfólio", "url": "/portfolio"}]'

    # Título Principal
    main_title = db.Column(db.String(255), nullable=True)

    # Subtítulo/Slogan
    slogan = db.Column(db.Text, nullable=True)

    # Palavras-chave Rotativas (armazenadas como string JSON)
    rotating_keywords_json = db.Column(db.Text, nullable=True) # Ex: '["EXPERIÊNCIA", "INOVAÇÃO"]'

    # Seção "Nascido em São Paulo"
    nascido_em_sp_title = db.Column(db.Text, nullable=True)
    nascido_em_sp_quote = db.Column(db.Text, nullable=True)

    # Seção "Não seguimos as melhores práticas."
    best_practices_title = db.Column(db.Text, nullable=True)

    # Seção "Movido pela emoção."
    emotion_driven_title = db.Column(db.Text, nullable=True)

    # Serviços/Áreas de Atuação (armazenados como string JSON)
    services_json = db.Column(db.Text, nullable=True) # Ex: '[{"title": "Live Marketing", "description": "..."}]'

    # Seção "No que somos realmente bons"
    good_at_title = db.Column(db.String(255), nullable=True)
    good_at_intro = db.Column(db.Text, nullable=True)
    clients_json = db.Column(db.Text, nullable=True) # Ex: '["Pepsico", "Viveo"]'

    # Seção "Agências Parceiras"
    partners_title = db.Column(db.String(255), nullable=True)
    partners_json = db.Column(db.Text, nullable=True) # Ex: '["MKT House", "Geek Group BR"]'

    # Seção "Conversa é barata. Resultados custam caro."
    cta_title = db.Column(db.String(255), nullable=True)
    cta_subtitle = db.Column(db.Text, nullable=True)
    cta_button_text = db.Column(db.String(255), nullable=True)

    # Campos para cores e fundos (exemplo - pode ser expandido)
    # Armazenados como strings hexadecimais ou URLs de imagem
    header_bg_color = db.Column(db.String(7), nullable=True) # Ex: '#FFFFFF'
    section_1_bg_image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<HomePage {self.id}>'


