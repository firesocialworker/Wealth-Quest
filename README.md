# Focus RPG: ADHD Game Plan Toolkit

This repo packages a no-frills ADHD action plan and a shippable FastAPI + HTMX app you can drop into Replit (or run locally) to track deep work reps, earn rewards, and deploy the "storm" rescue protocol when things get noisy.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) to see the Today dashboard.

## What you get

- **Today dashboard** – capture micro-steps, see the top-five priorities, fire up a focus timer, and log distraction counts.
- **Points + dopamine menu** – complete a focus block to bank points, then redeem them for tight dopamine hits with cooldowns so you don’t derail the day.
- **ADHD storm protocol** – one click drops the four-step rescue checklist into view and logs the trigger so you can review patterns later.
- **Stats snapshot** – total points, sessions logged, streak days, and distraction counts refresh automatically as you work.

Everything runs on SQLite via SQLModel, so the data lives in `focus.db`. You can safely copy or back up that file whenever you need to reset.

## API sketch

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/tasks` | Create a task (5–10 minute micro-step recommended). |
| `GET` | `/tasks?status=open` | List tasks filtered by status. |
| `PATCH` | `/tasks/{id}` | Update any task fields. |
| `POST` | `/tasks/{id}/complete` | Mark a task done (used by the UI). |
| `POST` | `/sessions/start` | Start a focus session for a task. |
| `POST` | `/sessions/stop` | Stop a session, award points, log distractions. |
| `POST` | `/sessions/{id}/distract` | Increment the distraction counter during a session. |
| `GET` | `/stats/daily` | Pull totals for points, sessions, streak, and distractions. |
| `POST` | `/rewards/redeem` | Spend points on a reward. |
| `POST` | `/storm` | Log a trigger and get the storm protocol steps. |

Default rewards are seeded on startup (espresso, meme scroll, etc.), and a placeholder user keeps things simple until you’re ready for multi-user auth.

## ADHD game plan

Pair the app with these daily/weekly anchors:

- Sleep gate: 7–8h, consistent bed/wake.
- Meds/therapy/coach: treat them like oxygen.
- Move 20 minutes: walk, lift, stretch—anything.
- Two deep work blocks (25–40 minutes, DND on).
- 15-minute admin sweep to close loops.
- Weekly: 30-minute planning, budget reset, body-double session.
- Task rules: start tiny, timebox everything, split anything >40 minutes.
- Storm protocol: 3-item rescue list → 5-minute start → body-double → reset with movement/cold water.
- Dopamine menu: espresso, meme pass, pushups + music, 5-minute game, or 10 minutes outside.

Track your streaks, watch the distraction count trend down, and iterate after 14 days.
