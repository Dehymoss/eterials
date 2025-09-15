from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from modulos.backend.menu.database.base import Base

class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Cambio a Integer para consistencia
    codigo = Column(String(20), unique=True, nullable=True)  # Código único alfanumérico
    titulo = Column(String, nullable=False)  # Campo real en la base de datos
    descripcion = Column(Text)
    icono = Column(String)
    orden = Column(Integer)
    activa = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria")
    subcategorias = relationship("Subcategoria", back_populates="categoria")
    
    # Propiedad para compatibilidad
    @property
    def nombre(self):
        return self.titulo
