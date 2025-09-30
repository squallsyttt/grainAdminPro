"""
文件 API 端点
处理文件上传和下载
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user
from src.core.file_storage import file_storage
from src.models.enums import QualificationFileType
from src.schemas.file import FileUploadResponse, FileInfo
from src.services.file_service import FileService


router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传文件",
    description="上传资质文件或合同文件",
)
async def upload_file(
    file: UploadFile = File(..., description="文件对象"),
    file_type: str = Form(..., description="文件类型（business_license/id_card_front/id_card_back/contract/other）"),
    application_id: str = Form(None, description="申请ID（上传资质文件时必填）"),
    merchant_id: str = Form(None, description="商家编号（上传合同文件时必填）"),
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> FileUploadResponse:
    """
    上传文件

    **文件类型**:
    - business_license: 营业执照
    - id_card_front: 身份证正面
    - id_card_back: 身份证背面
    - contract: 合同文件
    - other: 其他资质文件

    **参数**:
    - file: 文件对象（支持 JPEG/PNG/PDF，最大10MB）
    - file_type: 文件类型
    - application_id: 申请ID（上传资质文件时必填）
    - merchant_id: 商家编号（上传合同文件时必填）

    **返回**:
    文件上传结果（包含文件ID、路径、大小等）
    """
    service = FileService(db)

    try:
        # 验证参数
        if file_type in ["business_license", "id_card_front", "id_card_back", "other"]:
            # 上传资质文件
            if not application_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="上传资质文件时必须提供 application_id",
                )

            # 转换文件类型枚举
            file_type_enum = QualificationFileType(file_type)

            uploaded_file = await service.upload_qualification_file(
                file,
                UUID(application_id),
                file_type_enum,
            )

            return FileUploadResponse(
                file_id=uploaded_file.id,
                file_path=uploaded_file.file_path,
                file_size=uploaded_file.file_size,
                uploaded_at=uploaded_file.uploaded_at,
            )

        elif file_type == "contract":
            # 上传合同文件
            if not merchant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="上传合同文件时必须提供 merchant_id",
                )

            upload_by = current_user.get("name", current_user["user_id"])

            uploaded_file = await service.upload_contract_file(
                file,
                merchant_id,
                upload_by,
            )

            return FileUploadResponse(
                file_id=uploaded_file.id,
                file_path=uploaded_file.file_path,
                file_size=uploaded_file.file_size,
                uploaded_at=uploaded_file.uploaded_at,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file_type}",
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}",
        )


@router.get(
    "/{file_id}",
    response_class=FileResponse,
    summary="下载文件",
    description="根据文件ID下载文件",
)
async def download_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    下载文件

    **权限**:
    - 管理员: 可下载所有文件
    - 商家: 仅可下载自己的文件（TODO: 实现权限验证）

    **参数**:
    - file_id: 文件ID

    **返回**:
    文件内容（直接下载）
    """
    service = FileService(db)

    try:
        # 生成签名URL（简化实现，直接返回文件路径）
        file_path = await service.generate_signed_url(
            file_id,
            user_id=UUID(current_user["user_id"]),
        )

        # 获取完整文件路径
        full_path = file_storage.get_file_path(file_path)

        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在",
            )

        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}",
        )