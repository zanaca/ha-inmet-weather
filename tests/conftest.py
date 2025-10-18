"""Simple fixtures for INMET Weather integration tests (no HA dependency)."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Constants (matching Home Assistant)
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_NAME = "name"


@pytest.fixture
def mock_aiohttp_client():
    """Mock aiohttp client session."""
    with patch("aiohttp.ClientSession") as mock_session:
        yield mock_session


@pytest.fixture
def mock_current_weather_response():
    """Mock current weather API response."""
    return {
        "estacao": {
            "UF": "RJ",
            "CODIGO": "A636",
            "LONGITUDE": "-43.40277777",
            "REGIAO": "SE",
            "DISTANCIA_EM_KM": "6",
            "NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
            "LATITUDE": "-22.93999999",
            "GEOCODE": "3304557",
        },
        "dados": {
            "DC_NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
            "PRE_INS": "1008.3",
            "TEM_SEN": "29.6",
            "VL_LATITUDE": "-22.93999999",
            "PRE_MAX": "1009.5",
            "UF": "RJ",
            "RAD_GLO": "3371.2",
            "PTO_INS": "20.6",
            "TEM_MIN": "27.3",
            "VL_LONGITUDE": "-43.40277777",
            "UMD_MIN": "61",
            "PTO_MAX": "21.6",
            "VEN_DIR": "153",
            "DT_MEDICAO": "2025-10-17",
            "CHUVA": "0",
            "PRE_MIN": "1008.3",
            "UMD_MAX": "68",
            "VEN_VEL": "1.7",
            "PTO_MIN": "20.1",
            "TEM_MAX": "29.1",
            "TEN_BAT": "13.3",
            "VEN_RAJ": "5.2",
            "TEM_CPU": "31",
            "TEM_INS": "29",
            "UMD_INS": "61",
            "CD_ESTACAO": "A636",
            "HR_MEDICAO": "1600",
        },
    }


@pytest.fixture
def mock_forecast_response():
    """Mock forecast API response."""
    return {
        "3304557": {
            "17/10/2025": {
                "manha": {
                    "uf": "RJ",
                    "entidade": "Rio de Janeiro",
                    "resumo": "Muitas nuvens",
                    "tempo": "",
                    "temp_max": 32,
                    "temp_min": 20,
                    "dir_vento": "N-NE",
                    "int_vento": "Fracos",
                    "cod_icone": "34",
                    "dia_semana": "Sexta-Feira",
                    "umidade_max": 90,
                    "umidade_min": 45,
                    "temp_max_tende": "Ligeira Elevação",
                    "temp_min_tende": "Estável",
                    "estacao": "Primavera",
                    "hora": "14",
                    "nascer": "05h21",
                    "ocaso": "17h59",
                    "fonte": "prevmet",
                },
                "tarde": {
                    "uf": "RJ",
                    "entidade": "Rio de Janeiro",
                    "resumo": "Muitas nuvens",
                    "tempo": "",
                    "temp_max": 32,
                    "temp_min": 20,
                    "dir_vento": "S-SW",
                    "int_vento": "Fraco/Moderado",
                    "cod_icone": "34",
                    "dia_semana": "Sexta-Feira",
                    "umidade_max": 90,
                    "umidade_min": 45,
                },
                "noite": {
                    "uf": "RJ",
                    "entidade": "Rio de Janeiro",
                    "resumo": "Poucas nuvens",
                    "tempo": "",
                    "temp_max": 30,
                    "temp_min": 18,
                    "dir_vento": "S",
                    "int_vento": "Fracos",
                    "cod_icone": "2",
                    "dia_semana": "Sexta-Feira",
                    "umidade_max": 85,
                    "umidade_min": 50,
                },
            },
            "18/10/2025": {
                "manha": {
                    "uf": "RJ",
                    "entidade": "Rio de Janeiro",
                    "resumo": "Limpo",
                    "tempo": "",
                    "temp_max": 28,
                    "temp_min": 18,
                    "dir_vento": "S-SE",
                    "int_vento": "Fracos",
                    "cod_icone": "1",
                    "dia_semana": "Sábado",
                    "umidade_max": 80,
                    "umidade_min": 45,
                },
            },
        }
    }


@pytest.fixture
def mock_config_entry():
    """Mock config entry data."""
    return {
        CONF_NAME: "INMET Weather Test",
        CONF_LATITUDE: -22.9068,
        CONF_LONGITUDE: -43.1729,
        "geocode": "3304557",
    }
