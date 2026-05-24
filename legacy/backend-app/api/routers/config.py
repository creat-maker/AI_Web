from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SystemConfig
from app.schemas import ChatHistoryOut, ConfigCreate, ConfigOut, ConfigUpdate, ResponseModel

router = APIRouter(prefix="/config", tags=["系统配置"])


@router.get("/", response_model=ResponseModel[list[ConfigOut]])
def list_configs(db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).order_by(SystemConfig.created_at.desc()).all()
    return ResponseModel(data=[ConfigOut.model_validate(c) for c in configs])


@router.post("/", response_model=ResponseModel[ConfigOut])
def create_config(payload: ConfigCreate, db: Session = Depends(get_db)):
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == payload.config_key).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"配置项 {payload.config_key} 已存在")

    config = SystemConfig(**payload.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return ResponseModel(data=ConfigOut.model_validate(config))


@router.put("/{config_key}", response_model=ResponseModel[ConfigOut])
def update_config(config_key: str, payload: ConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置项 {config_key} 不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return ResponseModel(data=ConfigOut.model_validate(config))


@router.get("/{config_key}", response_model=ResponseModel[ConfigOut])
def get_config(config_key: str, db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置项 {config_key} 不存在")
    return ResponseModel(data=ConfigOut.model_validate(config))


@router.delete("/{config_key}", response_model=ResponseModel[dict])
def delete_config(config_key: str, db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置项 {config_key} 不存在")
    db.delete(config)
    db.commit()
    return ResponseModel(data={"deleted": config_key})
