from data import db_session


db_session.global_init(f"db/Quizi.db")
db_sess = db_session.create_session()
