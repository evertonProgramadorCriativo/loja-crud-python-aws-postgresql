from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Product, User
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def _get_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
    return product


# Listar e ver um produto: público (qualquer visitante pode ver a vitrine)
@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None, description="Busca pelo nome"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Product).order_by(Product.id)
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, product_id)


# Criar, editar e apagar: exige login
@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    product = _get_or_404(db, product_id)
    # exclude_unset: só os campos que vieram no JSON
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field in ("name", "price", "stock"):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, f"'{field}' não pode ser nulo"
            )
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    product = _get_or_404(db, product_id)
    try:
        db.delete(product)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Produto está em algum carrinho e não pode ser apagado",
        )
