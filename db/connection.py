from datetime import datetime
from sqlalchemy import create_engine, Integer, DateTime
from sqlalchemy.orm import Session, DeclarativeBase, mapped_column
from typing import List
from routes.helpers import sendError
from dotenv import load_dotenv
import os

load_dotenv()



DATABASE_URL = "sqlite:///main.sqlite"
# POSTGRES_URL = "postgresql://postgres:Hyxt1ZY0elg7aS07Ykl4@containers-us-west-118.railway.app:5778/railway"
# POSTGRES_URL = "postgresql://localhost:5432/skill_sage?user=postgres&password=admin"

POSTGRES_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")

# POSTGRES_URL = "postgresql://postgres:administrator@skill-sage-db.c9xcjxxsg3qg.eu-north-1.rds.amazonaws.com:5432/skillsage_db"

engine = create_engine(POSTGRES_URL, echo=True)

session = Session(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    created = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated = mapped_column(DateTime, onupdate=datetime.utcnow)


def initDB():
    Base.metadata.create_all(bind=engine)


# RECOMMENDATION


class node:
    factor = 0
    rep = 0

    def __init__(self):
        pass

    def add(self, ft):
        self.rep += 1
        self.factor += ft

    def average(self):
        return self.factor // self.rep

    def __repr__(self):
        return str(self.average())


def recommend(skills: List[str], take: int = 20):
    try:
        cur = engine.raw_connection().cursor()

        fq = f"""
        SELECT skill, factor from skill_factors WHERE skill IN %s LIMIT 1;
        """
        cur.execute(fq, (tuple(skills),))
        factor_records = cur.fetchall()
        factors: dict[str, dict[str, int]] = dict()
        for item in factor_records:
            if item is not None:
                factors[item[0]] = item[1]

        pairs = dict()
        for skill in skills:
            if skill not in factors:
                continue
            for k, v in factors[skill].items():
                # key = skill, value = factor
                if k not in pairs:
                    pairs[k] = node()
                    pairs[k].add(v)
                else:
                    pairs[k].add(v)

        pair_list = list()
        for k, v in pairs.items():
            pair_list.append({"skill": k, "average": v.average()})

        result = list(
            map(
                lambda x: x["skill"],
                sorted(pair_list, key=lambda x: x["average"], reverse=True),
            )
        )

        clean = list(filter(lambda x: x not in skills, result))[:take]
        pq = f"""
            SELECT name FROM skills WHERE lower IN %s;
        """
        cur.execute(pq, (tuple(clean),))
        pair_records = cur.fetchall()
        return list(map(lambda x: x[0], pair_records))

    except Exception as err:
        print(err)
        session.rollback()
        sendError("failed")
    finally:
        session.close()
