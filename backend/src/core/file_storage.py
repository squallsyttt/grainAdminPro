"""
文件存储抽象层
提供统一的文件存储接口,支持本地文件系统和未来的S3兼容存储
"""
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import UUID

from src.core.config import settings


class FileStorage:
    """文件存储管理器"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化文件存储

        Args:
            base_dir: 基础存储目录（默认使用配置中的 UPLOAD_DIR）
        """
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """确保基础目录存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        file_obj: BinaryIO,
        file_path: str,
    ) -> str:
        """
        保存文件

        Args:
            file_obj: 文件对象
            file_path: 相对路径（如 "applications/uuid/file.jpg"）

        Returns:
            str: 保存后的完整路径
        """
        full_path = self.base_dir / file_path

        # 确保目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)

        return str(full_path)

    def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 相对路径

        Returns:
            bool: 是否删除成功
        """
        full_path = self.base_dir / file_path

        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            return True

        return False

    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 相对路径

        Returns:
            bool: 文件是否存在
        """
        full_path = self.base_dir / file_path
        return full_path.exists() and full_path.is_file()

    def get_file_path(self, file_path: str) -> Path:
        """
        获取文件的完整路径

        Args:
            file_path: 相对路径

        Returns:
            Path: 完整路径对象
        """
        return self.base_dir / file_path

    def generate_file_path(
        self,
        category: str,
        identifier: str,
        filename: str,
    ) -> str:
        """
        生成文件存储路径

        Args:
            category: 文件分类（如 "applications", "contracts"）
            identifier: 标识符（如申请ID、商家ID）
            filename: 文件名

        Returns:
            str: 相对路径（如 "applications/uuid/file.jpg"）
        """
        return f"{category}/{identifier}/{filename}"


# 全局文件存储实例
file_storage = FileStorage()