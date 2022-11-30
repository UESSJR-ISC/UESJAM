from database import Database
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer


class Usuarios(Database):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key = True)
    nombre = Column(String(60))
    correo = Column(String(60))
    password = Column(String(256))
    ues_id = Column(Integer)
    descripcion = Column(String(240))
    picture = Column(String(36))
    admin = Column(Integer)
    
    
class Jams(Database):
    __tablename__ = "jams"
    id = Column(Integer, primary_key = True)
    titulo = Column(String(60))
    descripcion = Column(String(60))
    cover= Column(String(256))
  

