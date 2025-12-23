from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from typing import Dict, Any

from config import settings
from database.supabase_client import supabase_client
from datetime import datetime

# Создаем приложение
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="templates")

# Базовая аутентификация
security = HTTPBasic()


def format_datetime(value: Any, format: str = "%Y-%m-%d %H:%M") -> str:
    """Форматирует дату из строки или объекта datetime"""
    if not value:
        return ""

    try:
        # Если это уже datetime
        if isinstance(value, datetime):
            return value.strftime(format)

        # Если это строка (от Supabase)
        if isinstance(value, str):
            # Пробуем разные форматы
            formats_to_try = [
                "%Y-%m-%dT%H:%M:%S.%f%z",  # 2024-01-15T14:30:00.000000+00:00
                "%Y-%m-%dT%H:%M:%S%z",  # 2024-01-15T14:30:00+00:00
                "%Y-%m-%d %H:%M:%S.%f%z",  # 2024-01-15 14:30:00.000000+00:00
                "%Y-%m-%d %H:%M:%S%z",  # 2024-01-15 14:30:00+00:00
                "%Y-%m-%dT%H:%M:%S",  # 2024-01-15T14:30:00
                "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:00
                "%Y-%m-%d",  # 2024-01-15
            ]

            for fmt in formats_to_try:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue

            # Если не удалось распарсить, возвращаем как есть
            return value[:16]  # Первые 16 символов

        return str(value)
    except Exception:
        return str(value)

templates.env.filters["format_datetime"] = format_datetime

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.admin_username)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(verify_admin)):
    """Главная панель управления"""
    stats = await supabase_client.get_statistics()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": username,
            "stats": stats,
            "title": "Панель управления"
        }
    )


@app.get("/students", response_class=HTMLResponse)
async def students_view(
        request: Request,
        page: int = 1,
        username: str = Depends(verify_admin)
):
    """Страница студентов"""
    students_data = await supabase_client.get_students(page=page)

    return templates.TemplateResponse(
        "tables/students.html",
        {
            "request": request,
            "students": students_data["data"],
            "pagination": {
                "page": students_data["page"],
                "total": students_data["total"],
                "page_size": students_data["page_size"],
                "total_pages": (students_data["total"] + students_data["page_size"] - 1) // students_data["page_size"]
            },
            "title": "Студенты"
        }
    )


@app.get("/topics", response_class=HTMLResponse)
async def topics_view(
        request: Request,
        page: int = 1,
        username: str = Depends(verify_admin)
):
    """Страница тем"""
    topics_data = await supabase_client.get_topics(page=page)

    return templates.TemplateResponse(
        "tables/topics.html",
        {
            "request": request,
            "topics": topics_data["data"],
            "pagination": {
                "page": topics_data["page"],
                "total": topics_data["total"],
                "page_size": topics_data["page_size"],
                "total_pages": (topics_data["total"] + topics_data["page_size"] - 1) // topics_data["page_size"]
            },
            "title": "Темы обучения"
        }
    )


@app.get("/sessions", response_class=HTMLResponse)
async def sessions_view(
        request: Request,
        page: int = 1,
        username: str = Depends(verify_admin)
):
    """Страница сессий"""
    sessions_data = await supabase_client.get_sessions(page=page)

    return templates.TemplateResponse(
        "tables/sessions.html",
        {
            "request": request,
            "sessions": sessions_data["data"],
            "pagination": {
                "page": sessions_data["page"],
                "total": sessions_data["total"],
                "page_size": sessions_data["page_size"],
                "total_pages": (sessions_data["total"] + sessions_data["page_size"] - 1) // sessions_data["page_size"]
            },
            "title": "Сессии обучения"
        }
    )


@app.get("/progress", response_class=HTMLResponse)
async def progress_view(
        request: Request,
        username: str = Depends(verify_admin)
):
    """Страница прогресса"""
    progress_data = await supabase_client.get_student_progress()

    return templates.TemplateResponse(
        "tables/progress.html",
        {
            "request": request,
            "progress": progress_data,
            "title": "Прогресс студентов"
        }
    )


# API endpoints для AJAX запросов
@app.get("/api/students/{student_id}")
async def get_student_api(student_id: int, username: str = Depends(verify_admin)):
    """API: Получить студента"""
    student = await supabase_client.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"success": True, "data": student}


@app.put("/api/students/{student_id}")
async def update_student_api(
        student_id: int,
        data: Dict[str, Any],
        username: str = Depends(verify_admin)
):
    """API: Обновить студента"""
    updated = await supabase_client.update_student(student_id, data)
    return {"success": True, "data": updated}


@app.get("/api/statistics")
async def get_statistics_api(username: str = Depends(verify_admin)):
    """API: Получить статистику"""
    stats = await supabase_client.get_statistics()
    return {"success": True, "data": stats}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )