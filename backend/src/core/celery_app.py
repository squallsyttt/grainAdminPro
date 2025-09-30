"""
Celery 异步任务配置
用于处理后台任务,如发送通知、生成报表等
"""
from celery import Celery

from src.core.config import settings

# 创建 Celery 应用实例
celery_app = Celery(
    "grainadmin",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery 配置
celery_app.conf.update(
    # 任务配置
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 任务结果配置
    result_expires=3600,  # 结果过期时间(秒)
    # 任务路由配置
    task_routes={
        "src.tasks.notifications.*": {"queue": "notifications"},
        "src.tasks.reports.*": {"queue": "reports"},
    },
    # Worker 配置
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# 自动发现任务
# celery_app.autodiscover_tasks(['src.tasks'])


@celery_app.task(bind=True)
def debug_task(self) -> str:
    """调试任务"""
    return f"Request: {self.request!r}"