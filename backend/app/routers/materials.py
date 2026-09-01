# -*- coding: utf-8 -*-
"""课业材料路由：按学生类别分级返回"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

# 类别访问级别：C 类可看 C 及以下；A 类全看
LEVEL_ORDER = {"C": 0, "B": 1, "A": 2}

router = APIRouter(prefix="/api/materials", tags=["课业材料"])


def _accessible(material: models.Material, category: str) -> bool:
    return LEVEL_ORDER.get(category, -1) >= LEVEL_ORDER.get(material.level_required, 0)


@router.get("", response_model=list[schemas.MaterialOut])
def list_materials(
    category: str = Query(default="C"),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """按当前查看的学生类别返回可访问材料；category 不合法时返回全部"""
    all_materials = db.query(models.Material).order_by(models.Material.level_required.desc(), models.Material.id).all()
    if category not in LEVEL_ORDER:
        return all_materials
    return [m for m in all_materials if _accessible(m, category)]


@router.post("", response_model=schemas.MaterialOut)
def create_material(data: schemas.MaterialOut, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    material = models.Material(
        title=data.title, type=data.type, level_required=data.level_required,
        url=data.url, description=data.description,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="材料不存在")
    db.delete(material)
    db.commit()
    return {"message": "删除成功"}
