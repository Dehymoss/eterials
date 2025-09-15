from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
# CORRIGIENDO: Usar la Base centralizada
from modulos.backend.menu.database.base import Base

class Ingrediente(Base):
    __tablename__ = 'ingredientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=True)  # Código único alfanumérico
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    nombre = Column(String(100), nullable=False)
    cantidad = Column(String(50), nullable=True)  # Cambio a String para flexibilidad
    unidad = Column(String(20), nullable=True)  # Renombrado de unidad_medida
    costo = Column(Float, default=0.0)
    obligatorio = Column(Boolean, default=True)
    activo = Column(Boolean, default=True)
    
    # Relación con producto
    producto = relationship("Producto", back_populates="ingredientes")