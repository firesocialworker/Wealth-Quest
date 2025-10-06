from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from math import floor
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_URL = "sqlite:///focus.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Focus RPG")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.globals.update(datetime=datetime, timedelta=timedelta)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    note: Optional[str] = ""
    est_minutes: int = 10
    context: str = "work"
    due_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"
    impact: int = 1
    priority_score: int = 0


class FocusSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    start: datetime
    end: Optional[datetime] = None
    duration_min: int = 0
    completed_bool: bool = False
    distract_count: int = 0


class Reward(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cost_points: int
    cooldown_min: int = 0
    last_redeemed_at: Optional[datetime] = None


class PointLedger(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    delta: int
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TriggerLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trigger_type: str
    note: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(BaseModel):
    title: str
    note: Optional[str] = None
    est_minutes: int = 10
    context: str = "work"
    due_date: Optional[str] = None
    impact: int = 1


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    note: Optional[str] = None
    est_minutes: Optional[int] = None
    context: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    impact: Optional[int] = None


class StormPayload(BaseModel):
    trigger: Optional[str] = None
    note: Optional[str] = None


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(User)).first():
            session.add(User(name="Solo Player"))
        existing_rewards = session.exec(select(Reward)).all()
        if not existing_rewards:
            session.add_all(
                [
                    Reward(name="Espresso or fancy tea", cost_points=8, cooldown_min=60),
                    Reward(name="One meme scroll pass", cost_points=6, cooldown_min=90),
                    Reward(name="10 pushups + music break", cost_points=5, cooldown_min=45),
                    Reward(name="5 minutes of game time", cost_points=7, cooldown_min=120),
                    Reward(name="10 minutes outside", cost_points=9, cooldown_min=180),
                ]
            )
        session.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def parse_due_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def compute_priority(task: Task) -> int:
    today = datetime.utcnow().date()
    due = parse_due_date(task.due_date)
    is_due_today = 1 if due == today else 0
    is_overdue = 1 if (due and due < today) else 0
    freshness = 1 if (datetime.utcnow() - task.created_at).days <= 3 else 0
    return (is_due_today * 3) + (is_overdue * 5) + task.impact + freshness


def compute_points_balance(session: Session) -> int:
    return sum(entry.delta for entry in session.exec(select(PointLedger)).all())


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: SessionDep) -> HTMLResponse:
    tasks = (
        session.exec(
            select(Task)
            .where(Task.status == "open")
            .order_by(Task.priority_score.desc(), Task.created_at)
            .limit(5)
        ).all()
    )
    balance = compute_points_balance(session)
    rewards = session.exec(select(Reward)).all()
    stats = get_daily_stats(session)
    return templates.TemplateResponse(
        "today.html",
        {
            "request": request,
            "tasks": tasks,
            "balance": balance,
            "rewards": rewards,
            "stats": stats,
        },
    )


@app.get("/tasks", response_model=list[Task])
def list_tasks(session: SessionDep, status: str = "open") -> list[Task]:
    statement = select(Task).where(Task.status == status).order_by(
        Task.priority_score.desc(), Task.created_at
    )
    return session.exec(statement).all()


def insert_task(session: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    task.priority_score = compute_priority(task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate, session: SessionDep) -> Task:
    return insert_task(session, payload)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate, session: SessionDep) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.priority_score = compute_priority(task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep) -> dict[str, str]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"status": "deleted"}


@app.post("/tasks/{task_id}/complete", response_class=HTMLResponse)
def complete_task(task_id: int, request: Request, session: SessionDep) -> HTMLResponse:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "done"
    session.add(task)
    session.commit()
    tasks = (
        session.exec(
            select(Task)
            .where(Task.status == "open")
            .order_by(Task.priority_score.desc(), Task.created_at)
            .limit(5)
        ).all()
    )
    response = templates.TemplateResponse(
        "partials/task_list.html", {"request": request, "tasks": tasks}
    )
    response.headers["HX-Trigger"] = json.dumps({"stats:refresh": {}})
    return response


@app.post("/tasks/form", response_class=HTMLResponse)
def create_task_form(
    request: Request,
    session: SessionDep,
    title: Annotated[str, Form(...)],
    note: Annotated[Optional[str], Form()] = None,
    est_minutes: Annotated[int, Form()] = 10,
    context: Annotated[str, Form()] = "work",
    due_date: Annotated[Optional[str], Form()] = None,
    impact: Annotated[int, Form()] = 1,
) -> HTMLResponse:
    payload = TaskCreate(
        title=title,
        note=note,
        est_minutes=est_minutes,
        context=context,
        due_date=due_date,
        impact=impact,
    )
    insert_task(session, payload)
    tasks = (
        session.exec(
            select(Task)
            .where(Task.status == "open")
            .order_by(Task.priority_score.desc(), Task.created_at)
            .limit(5)
        ).all()
    )
    return templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks},
    )


class SessionStartPayload(BaseModel):
    task_id: int


class SessionStopPayload(BaseModel):
    session_id: int
    completed: bool = False
    distracts: int = 0
    est_minutes: int = 25


@app.post("/sessions/start")
def start_session(payload: SessionStartPayload, session: SessionDep) -> dict[str, int | str]:
    task = session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "doing"
    focus_session = FocusSession(task_id=payload.task_id, start=datetime.utcnow())
    session.add(focus_session)
    session.add(task)
    session.commit()
    session.refresh(focus_session)
    return {"session_id": focus_session.id, "task": task.title}


@app.post("/sessions/stop")
def stop_session(payload: SessionStopPayload, session: SessionDep) -> dict[str, int]:
    focus_session = session.get(FocusSession, payload.session_id)
    if not focus_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if focus_session.end:
        return {"earned_points": 0, "duration_min": focus_session.duration_min}

    focus_session.end = datetime.utcnow()
    focus_session.duration_min = max(
        1, int((focus_session.end - focus_session.start).total_seconds() // 60)
    )
    focus_session.completed_bool = payload.completed
    focus_session.distract_count = payload.distracts

    task = session.get(Task, focus_session.task_id)
    points = 0
    if task:
        if payload.completed:
            task.status = "done"
            points = 5 + floor(payload.est_minutes / 10)
            due = parse_due_date(task.due_date)
            if due and focus_session.end.date() <= due:
                points += 3
        else:
            task.status = "open"
        session.add(task)

    session.add(focus_session)

    if points:
        ledger_entry = PointLedger(delta=points, reason="completed_focus_session")
        session.add(ledger_entry)

    session.commit()
    session.refresh(focus_session)
    return {"earned_points": points, "duration_min": focus_session.duration_min}


@app.post("/sessions/{session_id}/distract")
def increment_distraction(session_id: int, session: SessionDep) -> dict[str, int]:
    focus_session = session.get(FocusSession, session_id)
    if not focus_session:
        raise HTTPException(status_code=404, detail="Session not found")
    focus_session.distract_count += 1
    session.add(focus_session)
    session.commit()
    session.refresh(focus_session)
    return {"distract_count": focus_session.distract_count}


class RewardCreate(BaseModel):
    name: str
    cost_points: int
    cooldown_min: int = 0


@app.get("/rewards", response_model=list[Reward])
def list_rewards(session: SessionDep) -> list[Reward]:
    return session.exec(select(Reward)).all()


@app.post("/rewards", response_model=Reward)
def create_reward(payload: RewardCreate, session: SessionDep) -> Reward:
    reward = Reward(**payload.model_dump())
    session.add(reward)
    session.commit()
    session.refresh(reward)
    return reward


class RedeemPayload(BaseModel):
    reward_id: int


@app.post("/rewards/redeem")
def redeem_reward(
    payload: RedeemPayload, request: Request, session: SessionDep
) -> HTMLResponse | dict[str, str | int]:
    reward = session.get(Reward, payload.reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    balance = compute_points_balance(session)
    if balance < reward.cost_points:
        raise HTTPException(status_code=400, detail="Not enough points")
    if reward.last_redeemed_at:
        cooldown = reward.last_redeemed_at + timedelta(minutes=reward.cooldown_min)
        if datetime.utcnow() < cooldown:
            raise HTTPException(status_code=400, detail="Reward on cooldown")
    ledger_entry = PointLedger(delta=-reward.cost_points, reason=f"redeem:{reward.name}")
    reward.last_redeemed_at = datetime.utcnow()
    session.add_all([ledger_entry, reward])
    session.commit()
    new_balance = compute_points_balance(session)

    if request.headers.get("HX-Request"):
        rewards = session.exec(select(Reward)).all()
        response = templates.TemplateResponse(
            "partials/reward_list.html",
            {"request": request, "rewards": rewards, "balance": new_balance},
        )
        response.headers["HX-Trigger"] = json.dumps(
            {
                "points:update": {"balance": new_balance},
                "stats:refresh": {},
            }
        )
        return response

    return {"status": "ok", "balance": new_balance}


@app.get("/stats/daily")
def daily_stats(session: SessionDep) -> dict[str, int | float]:
    stats = get_daily_stats(session)
    return stats


def get_daily_stats(session: Session) -> dict[str, int | float]:
    today = datetime.utcnow().date()
    all_points = session.exec(select(PointLedger)).all()
    total_points = sum(entry.delta for entry in all_points)
    tasks_done = session.exec(select(Task).where(Task.status == "done")).all()
    total_sessions = session.exec(select(FocusSession)).all()
    streak = compute_completion_streak(session)
    distractions_today = sum(
        sess.distract_count
        for sess in total_sessions
        if sess.end and sess.end.date() == today
    )
    return {
        "total_points": total_points,
        "tasks_done": len(tasks_done),
        "sessions_logged": len(total_sessions),
        "streak_days": streak,
        "distractions_today": distractions_today,
    }


def compute_completion_streak(session: Session) -> int:
    completed_sessions = session.exec(
        select(FocusSession).where(
            FocusSession.completed_bool == True,  # noqa: E712
            FocusSession.end.is_not(None),
        )
    ).all()
    completed_dates = {
        sess.end.date()
        for sess in completed_sessions
        if sess.end and sess.completed_bool
    }
    if not completed_dates:
        return 0
    streak = 0
    current_day = datetime.utcnow().date()
    while current_day in completed_dates:
        streak += 1
        current_day = current_day - timedelta(days=1)
    return streak


@app.post("/storm")
def storm(
    payload: StormPayload, request: Request, session: SessionDep
) -> HTMLResponse | dict[str, list[str]]:
    session.add(
        TriggerLog(
            trigger_type=payload.trigger or "storm",
            note=payload.note,
        )
    )
    session.commit()
    checklist = [
        "Write a 3-item rescue list on paper.",
        "Spend 5 minutes on the first item.",
        "Ping a buddy or schedule a body-double session.",
        "If still stuck: 10 jumping jacks, cold water, then back for 5 minutes.",
    ]
    if request.headers.get("HX-Request"):
        items = "".join(f"<li>{step}</li>" for step in checklist)
        response = HTMLResponse(items)
        response.headers["HX-Trigger"] = json.dumps({"stats:refresh": {}})
        return response
    return {"protocol": checklist}


@app.get("/storm/logs")
def storm_logs(session: SessionDep) -> list[TriggerLog]:
    return session.exec(select(TriggerLog).order_by(TriggerLog.timestamp.desc())).all()


@app.get("/partials/task-list", response_class=HTMLResponse)
def task_list_partial(request: Request, session: SessionDep) -> HTMLResponse:
    tasks = (
        session.exec(
            select(Task)
            .where(Task.status == "open")
            .order_by(Task.priority_score.desc(), Task.created_at)
            .limit(5)
        ).all()
    )
    return templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks},
    )


@app.get("/partials/rewards", response_class=HTMLResponse)
def rewards_partial(request: Request, session: SessionDep) -> HTMLResponse:
    rewards = session.exec(select(Reward)).all()
    balance = compute_points_balance(session)
    return templates.TemplateResponse(
        "partials/reward_list.html",
        {"request": request, "rewards": rewards, "balance": balance},
    )


@app.get("/partials/stats", response_class=HTMLResponse)
def stats_partial(request: Request, session: SessionDep) -> HTMLResponse:
    stats = get_daily_stats(session)
    return templates.TemplateResponse(
        "partials/stats.html",
        {"request": request, "stats": stats},
    )
