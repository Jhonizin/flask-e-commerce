from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Ad(db.Model):
    __tablename__ = 'ads'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Chave estrangeira para o usuário que criou o anúncio
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Chave estrangeira para a categoria do anúncio
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relacionamentos
    user = db.relationship('User', back_populates='ads')
    category = db.relationship('Category', back_populates='ads')
    questions = db.relationship('Question', back_populates='ad', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Ad {self.title} - ${self.price}>'
