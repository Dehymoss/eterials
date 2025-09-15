from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from modulos.backend.menu.database.base import Base

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=True)  # Código único alfanumérico
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    subcategoria_id = Column(Integer, ForeignKey('subcategorias.id'))
    imagen_url = Column(String(500))
    tiempo_preparacion = Column(String(50))
    instrucciones_preparacion = Column(Text)  # Nuevo campo
    notas_cocina = Column(Text)  # Nuevo campo
    disponible = Column(Boolean, default=True)
    activo = Column(Boolean, default=True)
    tipo_producto = Column(String(20), default='simple')  # 'simple' o 'preparado'
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    subcategoria = relationship("Subcategoria", back_populates="productos")
    ingredientes = relationship("Ingrediente", back_populates="producto")