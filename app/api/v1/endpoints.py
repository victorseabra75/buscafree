import io
import os

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import db_client
from app.schemas.empresa import EmpresaResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Caminho direto para os Parquets no Cloudflare R2 via protocolo S3
BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "buscafri-data")
R2_PATH = f"s3://{BUCKET_NAME}"


@router.get("/busca", response_model=EmpresaResponse)
@limiter.limit("10/minute")
async def buscar_empresas(
    request: Request,
    uf: str | None = Query(None, description="Sigla do estado (ex: BA)"),
    municipio: str | None = Query(None, description="Código do município"),
    cnae: str | None = Query(None, description="Código do CNAE"),
    ativa: bool = Query(True, description="Filtrar apenas empresas ativas"),
    com_telefone: bool = Query(
        False, description="Filtrar apenas empresas com telefone"
    ),
    com_email: bool = Query(False, description="Filtrar apenas empresas com e-mail"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
):
    offset = (page - 1) * limit

    where_clauses = []
    if uf:
        where_clauses.append(f"est.uf = '{uf.upper()}'")
    if municipio:
        where_clauses.append(f"est.municipio = '{municipio}'")
    if cnae:
        where_clauses.append(f"est.cnae_fiscal_principal = '{cnae}'")
    if ativa:
        where_clauses.append("est.situacao_cadastral = '02'")
    if com_telefone:
        where_clauses.append("(est.telefone_1 IS NOT NULL AND est.telefone_1 != '')")
    if com_email:
        where_clauses.append(
            "(est.correio_eletronico IS NOT NULL AND est.correio_eletronico != '')"
        )

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT 
            est.cnpj_basico,
            emp.razao_social,
            est.nome_fantasia,
            est.situacao_cadastral,
            est.uf,
            est.municipio,
            est.cnae_fiscal_principal,
            est.correio_eletronico,
            CONCAT('(', est.ddd_1, ') ', est.telefone_1) as telefone_1
        FROM '{R2_PATH}/estabelecimentos/*.parquet' AS est
        JOIN '{R2_PATH}/empresas/*.parquet' AS emp ON est.cnpj_basico = emp.cnpj_basico
        WHERE {where_sql}
        LIMIT {limit} OFFSET {offset}
    """

    count_sql = f"""
        SELECT COUNT(*) as total 
        FROM '{R2_PATH}/estabelecimentos/*.parquet' AS est 
        WHERE {where_sql}
    """

    try:
        results = db_client.query(sql)
        total_df = db_client.query(count_sql)
        total = total_df.iloc[0]["total"] if not total_df.empty else 0

        data = results.to_dict("records")

        return {"total_count": int(total), "page": page, "limit": limit, "data": data}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {e!s}")


@router.get("/exportar/{formato}")
@limiter.limit("2/minute")
async def exportar_dados(
    request: Request,
    formato: str,
    uf: str | None = Query(None),
    ativa: bool = True,
    com_telefone: bool = False,
    com_email: bool = False,
):
    if formato not in ["csv", "xlsx"]:
        raise HTTPException(
            status_code=400, detail="Formato inválido. Use csv ou xlsx."
        )

    where_clauses = []
    if uf:
        where_clauses.append(f"est.uf = '{uf.upper()}'")
    if ativa:
        where_clauses.append("est.situacao_cadastral = '02'")
    if com_telefone:
        where_clauses.append("(est.telefone_1 IS NOT NULL AND est.telefone_1 != '')")
    if com_email:
        where_clauses.append(
            "(est.correio_eletronico IS NOT NULL AND est.correio_eletronico != '')"
        )

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT 
            est.cnpj_basico, emp.razao_social, est.nome_fantasia, 
            est.uf, est.municipio, est.correio_eletronico, est.telefone_1
        FROM '{R2_PATH}/estabelecimentos/*.parquet' AS est
        JOIN '{R2_PATH}/empresas/*.parquet' AS emp ON est.cnpj_basico = emp.cnpj_basico
        WHERE {where_sql}
        LIMIT 10000
    """

    try:
        df = db_client.query(sql)

        if formato == "csv":
            stream = io.StringIO()
            df.to_csv(stream, index=False, sep=";", encoding="utf-8-sig")
            response = StreamingResponse(
                iter([stream.getvalue()]), media_type="text/csv"
            )
            response.headers["Content-Disposition"] = (
                "attachment; filename=buscafri_export.csv"
            )
            return response
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Empresas")
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": "attachment; filename=buscafri_export.xlsx"
                },
            )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Erro na exportação: {e!s}")
