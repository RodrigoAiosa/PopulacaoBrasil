"""
Modelos de dados usando dataclasses e Pydantic
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Regiao:
    """Modelo de Região"""
    id: int
    nome: str
    sigla: str
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Regiao":
        return cls(
            id=data["id"],
            nome=data["nome"],
            sigla=data["sigla"]
        )


@dataclass
class Estado:
    """Modelo de Estado"""
    id: int
    nome: str
    sigla: str
    regiao: Optional[Regiao] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Estado":
        regiao = Regiao.from_api(data["regiao"]) if "regiao" in data else None
        return cls(
            id=data["id"],
            nome=data["nome"],
            sigla=data["sigla"],
            regiao=regiao
        )


@dataclass
class Municipio:
    """Modelo de Município"""
    id: int
    nome: str
    microrregiao: Optional[Dict] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Municipio":
        return cls(
            id=data["id"],
            nome=data["nome"],
            microrregiao=data.get("microrregiao")
        )


@dataclass
class IndicadorDemografico:
    """Modelo de indicadores demográficos"""
    populacao: Optional[float] = None
    area: Optional[float] = None
    densidade: Optional[float] = None
    total_municipios: Optional[int] = None
    pib_per_capita: Optional[float] = None
    pib_total: Optional[float] = None
    
    @property
    def populacao_formatada(self) -> str:
        if self.populacao is None:
            return "—"
        return f"{int(round(self.populacao)):,}".replace(",", ".")
    
    @property
    def area_formatada(self) -> str:
        if self.area is None:
            return "—"
        return f"{self.area:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def densidade_formatada(self) -> str:
        if self.densidade is None:
            return "—"
        return f"{self.densidade:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def pib_per_capita_formatado(self) -> str:
        if self.pib_per_capita is None:
            return "—"
        return f"R$ {self.pib_per_capita:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def pib_total_formatado(self) -> str:
        if self.pib_total is None:
            return "—"
        
        valor = self.pib_total
        if valor >= 1_000_000_000:
            return f"R$ {valor / 1_000_000_000:.2f} bi"
        elif valor >= 1_000_000:
            return f"R$ {valor / 1_000_000:.2f} mi"
        else:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class RankingItem:
    """Item do ranking populacional com renda per capita"""
    nome: str
    populacao: float
    renda_per_capita: Optional[float] = None
    destaque: bool = False
    
    @property
    def populacao_formatada(self) -> str:
        return f"{int(round(self.populacao)):,}".replace(",", ".")
    
    @property
    def renda_per_capita_formatada(self) -> str:
        if self.renda_per_capita is None:
            return "—"
        return f"R$ {self.renda_per_capita:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class DadosMapa:
    """Dados para exibição no mapa"""
    sigla: str
    nome: str
    populacao: float
    lat: float
    lon: float
    
    @property
    def populacao_formatada(self) -> str:
        return f"{int(round(self.populacao)):,}".replace(",", ".")
