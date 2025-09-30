"""
Celery 任务模块
定义异步任务
"""
from src.core.celery_app import celery_app


@celery_app.task(name="tasks.test_task")
def test_task() -> str:
    """测试任务 - 返回简单字符串"""
    return "success"


@celery_app.task(name="tasks.add")
def add(x: int, y: int) -> int:
    """测试任务 - 简单加法"""
    return x + y