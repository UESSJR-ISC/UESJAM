from sqlalchemy import Date
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import relationship, deferred


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

    votos = relationship("Votos", back_populates="usuario")
    juegos = relationship("Juegos", back_populates="usuario")
    
    
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

    juegos = relationship("Juegos", back_populates="jam", order_by="desc(Juegos.votos_count)")


class Votos(Database):
    __tablename__ = "votos"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship("Usuarios", back_populates="votos")

    juego_id = Column(Integer, ForeignKey('juegos.id'))
    juego = relationship("Juegos", back_populates="votos")

    jam_id = Column(Integer, ForeignKey('jams.id'))
    jam = relationship("Jams")


class Juegos(Database):
    __tablename__ = "juegos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(60))
    descripcion_corta = Column(String(120))
    descripcion_larga = Column(String(450))
    cover = Column(String(256))
    files = Column(String(256))
    path = Column(String(256))

    jam_id = Column(Integer, ForeignKey('jams.id'))
    jam = relationship("Jams", back_populates="juegos")

    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship("Usuarios", back_populates="juegos")

    comentarios = relationship("Comentarios", back_populates="juego")
    archivos = relationship("Archivos", back_populates="juego")
    votos = relationship("Votos", back_populates="juego")

    votos_count = deferred(select([Votos.id]).where(Votos.juego_id == id))


class Comentarios(Database):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True)
    contenido = Column(String(250))

    juego_id = Column(Integer, ForeignKey('juegos.id'))
    juego = relationship("Juegos", back_populates="comentarios")


class Archivos(Database):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(90))

    juego_id = Column(Integer, ForeignKey('juegos.id'))
    juego = relationship("Juegos", back_populates="archivos")