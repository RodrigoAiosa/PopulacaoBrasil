"""
Funções de formatação para display
"""
from typing import Optional, Any


def fmt_int(value: Optional[float]) -> str:
    """Formata número inteiro com separador de milhar"""
    if value is None:
        return "—"
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_dec(value: Optional[float], casas: int = 1) -> str:
    """Formata número decimal com separador"""
    if value is None:
        return "—"
    # Substitui ponto por vírgula e vice-versa
    return f"{value:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_porcentagem(value: Optional[float], casas: int = 1) -> str:
    """Formata porcentagem"""
    if value is None:
        return "—"
    return f"{fmt_dec(value, casas)}%"


def fmt_habitantes(value: Optional[float]) -> str:
    """Formata número de habitantes"""
    if value is None:
        return "—"
    
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} mi"
    elif value >= 1_000:
        return f"{value / 1_000:.1f} mil"
    return fmt_int(value)


def fmt_posicao(posicao: Optional[int], total: Optional[int] = None) -> str:
    """Formata posição em ranking"""
    if posicao is None:
        return "—"
    
    # Adiciona sufixo ordinal
    sufixos = {1: "º", 2: "º", 3: "º"}
    sufixo = sufixos.get(posicao % 10, "º")
    
    resultado = f"{posicao}{sufixo}"
    if total:
        resultado += f" de {total}"
    
    return resultado


def formatar_texto_plural(numero: int, singular: str, plural: str = None) -> str:
    """Retorna texto no singular ou plural conforme o número"""
    if numero == 1:
        return singular
    return plural if plural else f"{singular}s"
