from scripts.convert_to_parquet import get_table_name


def test_get_table_name_mapping():
    # Teste de mapeamento inteligente de nomes
    assert get_table_name("F.K03200$Z.D60912.CNAECSV") == "cnaes"
    assert get_table_name("K3241.K03200Y0.D60912.EMPRECSV") == "empresas"
    assert get_table_name("K3241.K03200Y0.D60912.ESTABELE") == "estabelecimentos"
    assert get_table_name("F.K03200$W.SIMPLES.CSV.D60912") == "simples"
    assert get_table_name("K3241.K03200Y0.D60912.SOCIOCSV") == "socios"


def test_get_table_name_fallback():
    # Teste para arquivos desconhecidos (deve retornar o stem)
    assert get_table_name("arquivo_aleatorio.csv") == "arquivo_aleatorio"


def test_get_table_name_case_insensitivity():
    # Teste de indiferença a maiúsculas/minúsculas
    assert get_table_name("cnaecsv_teste.csv") == "cnaes"
