from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# ---- DBの準備 ----
DATABASE_URL = "sqlite:///./goals.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---- テーブルの設計図 ----
class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    achieved = Column(Boolean, default=False)

# テーブルを実際に作る
Base.metadata.create_all(bind=engine)

# ---- FastAPI本体 ----
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, やりたいことリスト!"}

@app.post("/goals")
def add_goal(title: str):
    db = SessionLocal()
    new_goal = Goal(title=title)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    db.close()
    return {"message": f"「{title}」を追加しました", "id": new_goal.id}

@app.get("/goals")
def get_goals():
    db = SessionLocal()
    goals = db.query(Goal).all()
    db.close()
    return goals