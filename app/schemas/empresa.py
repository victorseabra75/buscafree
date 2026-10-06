from pydantic import BaseModel


class EmpresaBase(BaseModel):
    cnpj_basico: str
    razao_social: str
    nome_fantasia: str | None = None
    situacao_cadastral: str
    uf: str
    municipio: str
    cnae_fiscal_principal: str
    correio_eletronico: str | None = None
    telefone_1: str | None = None


class EmpresaResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    data: list[EmpresaBase]
