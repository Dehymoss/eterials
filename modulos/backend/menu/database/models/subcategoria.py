from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from modulos.backend.menu.database.base import Base

class Subcategoria(Base):
    __tablename__ = 'subcategorias'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Cambio a Integer
    codigo = Column(String(20), unique=True, nullable=True)  # Código único alfanumérico
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)  # Cambio a Integer
    tipo = Column(String)  # Ejemplo: 'con licor', 'sin licor', etc.
    icono = Column(String(10), default='🏷️')  # Campo para icono emoji
    orden = Column(Integer, default=0)  # Campo para ordenamiento
    activa = Column(Boolean, default=True)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="subcategorias")
    productos = relationship("Producto", back_populates="subcategoria")
