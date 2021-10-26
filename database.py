import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import name_user, password, port, name_db


Base = declarative_base()


engine = sq.create_engine(f'postgresql+psycopg2://{name_user}:{password}@localhost:{port}/{name_db}')
Session = sessionmaker(bind=engine)


class Url(Base):
    __tablename__ = 'url'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False, unique=True)
    url = sq.Column(sq.String, nullable=False, unique=True)


if __name__ == '__main__':
    session = Session()
    Base.metadata.create_all(engine)