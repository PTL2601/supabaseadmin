from supabase import create_client, Client
from config import settings
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )

    # Студенты
    async def get_students(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Получить список студентов с пагинацией"""
        try:
            start = (page - 1) * page_size
            end = start + page_size - 1

            response = self.client.table("stdlist") \
                .select("id, fullname, tgid, isactive, createdat, \"Group\"") \
                .range(start, end) \
                .order("createdat", desc=True) \
                .execute()

            count = self.client.table("stdlist") \
                .select("*", count="exact") \
                .execute()

            # Форматируем данные для шаблона
            formatted_students = []
            for student in response.data:
                # Парсим имя из fullname
                fullname = student.get("fullname", "").strip()
                first_name = ""
                last_name = ""

                if fullname:
                    parts = fullname.split()
                    if len(parts) >= 2:
                        first_name = parts[0]
                        last_name = " ".join(parts[1:])
                    else:
                        first_name = fullname

                # Получаем количество тем (из tasklist и testlist)
                student_id = student.get("id")
                tasks_count = 0
                tests_count = 0

                try:
                    tasks_response = self.client.table("tasklist") \
                        .select("*", count="exact") \
                        .eq("studentid", student_id) \
                        .execute()
                    tasks_count = tasks_response.count or 0
                except:
                    pass

                try:
                    tests_response = self.client.table("testlist") \
                        .select("*", count="exact") \
                        .eq("studentid", student_id) \
                        .execute()
                    tests_count = tests_response.count or 0
                except:
                    pass

                formatted_students.append({
                    "id": student_id,
                    "tgid": student.get("tgid", ""),
                    "username": "",  # Нет поля username в таблице
                    "first_name": first_name,
                    "last_name": last_name,
                    "level": student.get("Group", ""),  # Используем "Group" как уровень
                    "topics_count": tasks_count + tests_count,
                    "is_active": bool(student.get("isactive", True)),
                    "created_at": student.get("createdat"),
                    "fullname": fullname,
                    "group": student.get("Group", "")
                })

            return {
                "data": formatted_students,
                "total": count.count if hasattr(count, 'count') else len(response.data),
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            print(f"Error in get_students: {e}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}

    async def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Получить студента по ID"""
        try:
            response = self.client.table("stdlist") \
                .select("id, fullname, tgid, isactive, createdat, \"Group\"") \
                .eq("id", student_id) \
                .single() \
                .execute()

            student = response.data
            if student:
                # Парсим имя
                fullname = student.get("fullname", "").strip()
                first_name = ""
                last_name = ""

                if fullname:
                    parts = fullname.split()
                    if len(parts) >= 2:
                        first_name = parts[0]
                        last_name = " ".join(parts[1:])
                    else:
                        first_name = fullname

                return {
                    "id": student.get("id"),
                    "tgid": student.get("tgid"),
                    "fullname": fullname,
                    "first_name": first_name,
                    "last_name": last_name,
                    "group": student.get("Group"),
                    "is_active": bool(student.get("isactive", True)),
                    "created_at": student.get("createdat")
                }
            return None
        except Exception as e:
            print(f"Error in get_student_by_id: {e}")
            return None

    # Темы
    async def get_topics(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Получить список тем с пагинацией"""
        try:
            start = (page - 1) * page_size
            end = start + page_size - 1

            response = self.client.table("topiclist") \
                .select("id, topicname, topicdesc, isactive, subjectid, date_of_completion") \
                .range(start, end) \
                .order("id", desc=True) \
                .execute()

            count = self.client.table("topiclist") \
                .select("*", count="exact") \
                .execute()

            # Форматируем данные для шаблона
            formatted_data = []
            for topic in response.data:
                # Получаем название предмета
                subject_name = ""
                subject_id = topic.get("subjectid")
                if subject_id:
                    try:
                        subject_response = self.client.table("subjectlist") \
                            .select("subjectname") \
                            .eq("id", subject_id) \
                            .single() \
                            .execute()
                        subject_name = subject_response.data.get("subjectname", "")
                    except:
                        pass

                # Считаем количество выполненных заданий
                topic_id = topic.get("id")
                completed_count = 0

                try:
                    tasks_response = self.client.table("tasklist") \
                        .select("*", count="exact") \
                        .eq("topicid", topic_id) \
                        .execute()
                    completed_count += tasks_response.count or 0
                except:
                    pass

                try:
                    tests_response = self.client.table("testlist") \
                        .select("*", count="exact") \
                        .eq("topicid", topic_id) \
                        .execute()
                    completed_count += tests_response.count or 0
                except:
                    pass

                formatted_data.append({
                    "id": topic_id,
                    "title": topic.get("topicname", "Без названия"),
                    "description": topic.get("topicdesc", ""),
                    "level": "beginner",  # По умолчанию
                    "topic_type": "learning",
                    "language": "ru",
                    "subject": subject_name,
                    "questions_count": 10,  # По умолчанию
                    "completed_count": completed_count,
                    "is_active": bool(topic.get("isactive", True)),
                    "created_at": topic.get("date_of_completion"),  # Используем date_of_completion
                    "raglink": topic.get("raglink", "")
                })

            return {
                "data": formatted_data,
                "total": count.count if hasattr(count, 'count') else len(response.data),
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            print(f"Error in get_topics: {e}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}

    # Сессии
    async def get_sessions(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Получить список сессий"""
        try:
            start = (page - 1) * page_size
            end = start + page_size - 1

            response = self.client.table("sessionlist") \
                .select("id, tgid, mode, topicid, total, current_index, created_at, questions, answers") \
                .range(start, end) \
                .order("created_at", desc=True) \
                .execute()

            count = self.client.table("sessionlist") \
                .select("*", count="exact") \
                .execute()

            # Форматируем данные для шаблона
            formatted_data = []
            for session in response.data:
                # Получаем тему
                topic_name = ""
                topic_id = session.get("topicid")
                if topic_id:
                    try:
                        topic_response = self.client.table("topiclist") \
                            .select("topicname") \
                            .eq("id", topic_id) \
                            .single() \
                            .execute()
                        topic_name = topic_response.data.get("topicname", "")
                    except:
                        topic_name = f"Тема {topic_id}"

                # Получаем текущий вопрос и ответ
                questions = session.get("questions", [])
                answers = session.get("answers", [])
                current_index = session.get("current_index", 0)

                current_question = ""
                current_answer = ""

                if isinstance(questions, list) and current_index < len(questions):
                    current_question = str(questions[current_index])

                if isinstance(answers, list) and current_index < len(answers):
                    current_answer = str(answers[current_index])

                formatted_data.append({
                    "id": session.get("id", ""),
                    "tgid": session.get("tgid", ""),
                    "mode": session.get("mode", "learning"),
                    "topicid": topic_id,
                    "topic_name": topic_name,
                    "current_question": current_question,
                    "current_answer": current_answer,
                    "score": None,  # В sessionlist нет поля score
                    "current_index": current_index,
                    "total": session.get("total", 10),
                    "created_at": session.get("created_at"),
                    "is_active": True  # Все сессии активны (нет поля is_active)
                })

            return {
                "data": formatted_data,
                "total": count.count if hasattr(count, 'count') else len(response.data),
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            print(f"Error in get_sessions: {e}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}

    # Прогресс студентов
    async def get_student_progress(self) -> Dict[str, Any]:
        """Получить прогресс студентов из view student_progress"""
        try:
            # Используем готовый view
            response = self.client.table("student_progress") \
                .select("*") \
                .execute()

            progress_data = response.data

            # Группируем по студентам
            students_dict = {}
            for row in progress_data:
                student_id = row.get("studentid")
                if student_id not in students_dict:
                    # Получаем доп. информацию о студенте
                    student_info = {}
                    try:
                        student_response = self.client.table("stdlist") \
                            .select("fullname, tgid, isactive, createdat, \"Group\"") \
                            .eq("id", student_id) \
                            .single() \
                            .execute()
                        student_info = student_response.data
                    except:
                        pass

                    # Парсим имя
                    fullname = student_info.get("fullname", "").strip()
                    first_name = ""
                    last_name = ""

                    if fullname:
                        parts = fullname.split()
                        if len(parts) >= 2:
                            first_name = parts[0]
                            last_name = " ".join(parts[1:])
                        else:
                            first_name = fullname

                    students_dict[student_id] = {
                        "id": student_id,
                        "tgid": student_info.get("tgid", ""),
                        "fullname": fullname,
                        "first_name": first_name,
                        "last_name": last_name,
                        "group": student_info.get("Group", ""),
                        "is_active": bool(student_info.get("isactive", True)),
                        "topics": [],
                        "completed_count": 0,
                        "practice_score_avg": 0,
                        "test_score_avg": 0
                    }

                # Добавляем тему
                students_dict[student_id]["topics"].append({
                    "topicid": row.get("topicid"),
                    "topicname": row.get("topicname"),
                    "practice_done": row.get("practice_done", False),
                    "practice_score": row.get("practice_score"),
                    "test_done": row.get("test_done", False),
                    "test_score": row.get("test_score")
                })

            # Считаем статистику для каждого студента
            students_progress = []
            practice_scores = []
            test_scores = []
            completed_counts = []
            active_count = 0

            for student in students_dict.values():
                topics = student["topics"]

                # Считаем выполненные практики и тесты
                practice_done = [t for t in topics if t["practice_done"]]
                test_done = [t for t in topics if t["test_done"]]

                completed_topics = len([t for t in topics if t["practice_done"] or t["test_done"]])
                student["completed_count"] = completed_topics
                completed_counts.append(completed_topics)

                # Считаем средние баллы
                practice_scores_student = [t["practice_score"] for t in practice_done if
                                           t["practice_score"] is not None]
                test_scores_student = [t["test_score"] for t in test_done if t["test_score"] is not None]

                practice_avg = sum(practice_scores_student) / len(
                    practice_scores_student) if practice_scores_student else 0
                test_avg = sum(test_scores_student) / len(test_scores_student) if test_scores_student else 0

                student["practice_score_avg"] = practice_avg
                student["test_score_avg"] = test_avg

                # Общие средние
                practice_scores.extend(practice_scores_student)
                test_scores.extend(test_scores_student)

                # Активен ли студент
                if student["is_active"]:
                    active_count += 1

                # Формируем для шаблона
                students_progress.append({
                    "id": student["id"],
                    "tgid": student["tgid"],
                    "username": "",
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "completed_topics": completed_topics,
                    "total_topics": len(topics),
                    "average_score": round((practice_avg + test_avg) / 2, 1) if practice_avg > 0 or test_avg > 0 else 0,
                    "last_activity": None,  # Нет поля последней активности
                    "is_active": student["is_active"],
                    "group": student["group"]
                })

            # Считаем общую статистику
            avg_progress = sum(completed_counts) / (len(completed_counts) * len(
                students_dict[list(students_dict.keys())[0]]["topics"])) * 100 if students_dict else 0

            # Новые студенты (за последние 7 дней)
            week_ago = datetime.now() - timedelta(days=7)
            new_students = 0

            for student_id in students_dict.keys():
                try:
                    student_response = self.client.table("stdlist") \
                        .select("createdat") \
                        .eq("id", student_id) \
                        .single() \
                        .execute()

                    created_at = student_response.data.get("createdat")
                    if created_at:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if dt > week_ago:
                            new_students += 1
                except:
                    pass

            return {
                "average_progress": round(avg_progress, 1),
                "active_students": active_count,
                "completed_students": len([s for s in students_progress if s["completed_topics"] >= 3]),
                # Завершили хотя бы 3 темы
                "new_students": new_students,
                "students": students_progress[:100],  # Ограничиваем для производительности
                "total_students": len(students_progress)
            }

        except Exception as e:
            print(f"Error in get_student_progress: {e}")
            return {
                "average_progress": 0,
                "active_students": 0,
                "completed_students": 0,
                "new_students": 0,
                "students": [],
                "total_students": 0
            }

    # Статистика
    async def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику по системе"""
        try:
            # Количество студентов
            students_response = self.client.table("stdlist") \
                .select("*", count="exact") \
                .execute()

            total_students = students_response.count if hasattr(students_response, 'count') else 0

            # Активные студенты
            active_students_response = self.client.table("stdlist") \
                .select("*", count="exact") \
                .eq("isactive", True) \
                .execute()

            active_students = active_students_response.count if hasattr(active_students_response, 'count') else 0

            # Количество тем
            topics_response = self.client.table("topiclist") \
                .select("*", count="exact") \
                .eq("isactive", True) \
                .execute()

            total_topics = topics_response.count if hasattr(topics_response, 'count') else 0

            # Активные сессии (последние 24 часа)
            day_ago = datetime.now() - timedelta(dours=24)
            active_sessions_response = self.client.table("sessionlist") \
                .select("*", count="exact") \
                .gte("created_at", day_ago.isoformat()) \
                .execute()

            active_sessions = active_sessions_response.count if hasattr(active_sessions_response, 'count') else 0

            # Последние сессии (доработанные данные)
            recent_sessions_response = self.client.table("sessionlist") \
                .select("id, tgid, mode, topicid, current_index, total, created_at") \
                .order("created_at", desc=True) \
                .limit(10) \
                .execute()

            recent_sessions = []
            for session in recent_sessions_response.data:
                # Получаем название темы
                topic_name = ""
                topic_id = session.get("topicid")
                if topic_id:
                    try:
                        topic_response = self.client.table("topiclist") \
                            .select("topicname") \
                            .eq("id", topic_id) \
                            .single() \
                            .execute()
                        topic_name = topic_response.data.get("topicname", "")
                    except:
                        topic_name = f"Тема {topic_id}"

                recent_sessions.append({
                    "id": session.get("id"),
                    "tgid": session.get("tgid"),
                    "mode": session.get("mode", "learning"),
                    "topicid": topic_id,
                    "topic_name": topic_name,
                    "current_index": session.get("current_index", 0),
                    "total": session.get("total", 10),
                    "created_at": session.get("created_at")
                })

            return {
                "total_students": total_students,
                "active_students": active_students,
                "total_topics": total_topics,
                "active_sessions": active_sessions,
                "recent_sessions": recent_sessions
            }

        except Exception as e:
            print(f"Error in get_statistics: {e}")
            return {
                "total_students": 0,
                "active_students": 0,
                "total_topics": 0,
                "active_sessions": 0,
                "recent_sessions": []
            }


# Создаем глобальный экземпляр клиента
supabase_client = SupabaseClient()