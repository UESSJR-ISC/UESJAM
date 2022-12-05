from sqlalchemy import Date
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from database import Database

class Usuarios(Database):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(60))
    correo = Column(String(60))
    password = Column(String(256))
    ues_id = Column(Integer)
    descripcion = Column(String(240))
    picture = Column(String(36))
    admin = Column(Integer)
    
    
class Jams(Database):
    __tablename__ = "jams"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(60))
    descripcion = Column(String(60))
    cover = Column(String(256))
    fecha_inicio = Column(Date)
    fecha_final = Column(Date)
    tags = Column(String(240))
    opened = Column(Integer)
    visible = Column(Integer)


class Juegos(Database):
    __tablename__ = "juegos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(60))
    descripcion_corta = Column(String(120))
    descripcion_larga = Column(String(450))
    cover = Column(String(256))
    folder_capturas = Column(String(256))
    folder_ficheros = Column(String(256))
    votos = Column(Integer)

    jam_id = Column(Integer, ForeignKey('jams.id'))
    jam = relationship("Jams")


class Comentarios(Database):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True)
    contenido = Column(String(250))

    juego_id = Column(Integer, ForeignKey('juegos.id'))
    juego = relationship("Juegos")