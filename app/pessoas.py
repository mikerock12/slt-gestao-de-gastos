# -*- coding: utf-8 -*-
"""Quem é quem.

Cada planilha entra como uma pessoa. O CPF e o nome saem das próprias notas
baixadas (a NFC-e traz "CPF: 000.000.000-00 - FULANO DE TAL"), com o nome do
arquivo como reserva.

Se duas planilhas trouxerem o mesmo CPF, viram uma pessoa só. Sobrando uma
pessoa, o painel fala no singular e usa o nome dela; sobrando duas ou mais,
fala em família e trata cada uma como um membro.
"""
from __future__ import annotations

import collections
import re
from dataclasses import dataclass, field


@dataclass
class Pessoa:
    nome: str
    cpf: str = ""
    planilhas: list[str] = field(default_factory=list)
    notas: int = 0

    @property
    def cpf_mascarado(self) -> str:
        """Mostra só o miolo do CPF, como fazem os comprovantes."""
        d = re.sub(r"\D", "", self.cpf)
        if len(d) != 11:
            return self.cpf
        return f"***.{d[3:6]}.{d[6:9]}-**"


def _primeiro_nome(nome: str) -> str:
    partes = [p for p in re.split(r"\s+", nome.strip()) if len(p) > 2]
    return partes[0].title() if partes else nome.title()


def _titulo(nome: str) -> str:
    """'MARIA DOS SANTOS' -> 'Maria dos Santos'."""
    miudas = {"de", "da", "do", "das", "dos", "e"}
    partes = nome.lower().split()
    return " ".join(p if p in miudas else p.capitalize() for p in partes)


def identificar(por_planilha: dict[str, list]) -> tuple[list[Pessoa], bool]:
    """`por_planilha`: {rótulo da planilha: [NotaCompleta, ...]}.

    Devolve (pessoas, é_família).
    """
    brutas: list[Pessoa] = []
    for rotulo, notas in por_planilha.items():
        cpfs = collections.Counter(n.cpf for n in notas if n.cpf)
        nomes = collections.Counter(n.consumidor for n in notas if n.consumidor)
        cpf = cpfs.most_common(1)[0][0] if cpfs else ""
        nome = _titulo(nomes.most_common(1)[0][0]) if nomes else rotulo
        brutas.append(Pessoa(nome=nome, cpf=cpf, planilhas=[rotulo], notas=len(notas)))

    # junta planilhas que são da mesma pessoa
    por_cpf: dict[str, Pessoa] = {}
    sem_cpf: list[Pessoa] = []
    for p in brutas:
        if not p.cpf:
            sem_cpf.append(p)
            continue
        if p.cpf in por_cpf:
            alvo = por_cpf[p.cpf]
            alvo.planilhas.extend(p.planilhas)
            alvo.notas += p.notas
        else:
            por_cpf[p.cpf] = p

    pessoas = list(por_cpf.values()) + sem_cpf
    pessoas.sort(key=lambda p: -p.notas)

    # nomes curtos, desde que não fiquem repetidos
    curtos = [_primeiro_nome(p.nome) for p in pessoas]
    if len(set(curtos)) == len(curtos):
        for p, c in zip(pessoas, curtos):
            p.nome = c

    return pessoas, len(pessoas) > 1


def titulo_do_conjunto(pessoas: list[Pessoa]) -> str:
    if len(pessoas) == 1:
        return pessoas[0].nome
    if len(pessoas) == 2:
        return f"{pessoas[0].nome} e {pessoas[1].nome}"
    return ", ".join(p.nome for p in pessoas[:-1]) + f" e {pessoas[-1].nome}"
