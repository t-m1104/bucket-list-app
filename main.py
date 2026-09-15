from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from passlib.context import CryptContext

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
    
    

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# テーブルを実際に作る
Base.metadata.create_all(bind=engine)

# ---- FastAPI本体 ----
app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/app")
def serve_frontend():
    return FileResponse("static/index.html")

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

@app.patch("/goals/{goal_id}/achieve")
def achieve_goal(goal_id: int):
    db = SessionLocal()
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if goal:
        goal.achieved = True
        db.commit()
    db.close()
    return {"message": "達成しました!"}

@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    db = SessionLocal()
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if goal:
        db.delete(goal)
        db.commit()
    db.close()
    return {"message": "削除しました"}

@app.post("/register")
def register(username: str, password: str):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        db.close()
        return {"error": "そのユーザー名はすでに使われています"}

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.close()
    return {"message": f"{username}を登録しました"}

@app.post("/login")
def login(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user:
        return {"error": "ユーザーが見つかりません"}

    if not pwd_context.verify(password, user.hashed_password):
        return {"error": "パスワードが違います"}

    return {"message": f"{username}さん、ログイン成功です!"}