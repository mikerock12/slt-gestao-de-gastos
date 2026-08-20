# -*- coding: utf-8 -*-
"""Janela do SLT — Gestão de Gastos.

Uma tela só: escolher a pasta com as planilhas, apertar o botão, esperar.
O trabalho roda numa thread para a janela não travar.
"""
from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

from .pipeline import executar

APP = "SLT — Gestão de Gastos"

COR = {
    "fundo": "#0e100e", "painel": "#171a17", "campo": "#1e221e",
    "linha": "#272c27", "texto": "#e8ece7", "texto2": "#a2ada6",
    "texto3": "#78837c", "mate": "#35a87a", "erro": "#e0725a",
}


def _pasta_padrao_saida(entrada: str) -> str:
    return os.path.join(entrada, "Gestao de Gastos")


class Janela(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.configure(bg=COR["fundo"])
        self.minsize(720, 560)
        self.geometry("820x640")
        self._centraliza()

        self.entrada = tk.StringVar()
        self.saida = tk.StringVar()
        self.fila = queue.Queue()
        self.rodando = False
        self.cancelar = threading.Event()
        self.resultado = None

        self._estilo()
        self._monta()
        self.after(120, self._drena)
        self.protocol("WM_DELETE_WINDOW", self._fechar)

    # ------------------------------------------------------------- visual
    def _centraliza(self):
        self.update_idletasks()
        w, h = 820, 640
        x = (self.winfo_screenwidth() - w) // 2
        y = max(0, (self.winfo_screenheight() - h) // 2 - 30)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _estilo(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TProgressbar", troughcolor=COR["campo"], background=COR["mate"],
                    bordercolor=COR["linha"], lightcolor=COR["mate"],
                    darkcolor=COR["mate"], thickness=8)

    def _rotulo(self, pai, texto, **kw):
        cfg = dict(bg=COR["fundo"], fg=COR["texto2"], font=("Segoe UI", 10),
                   anchor="w", justify="left")
        cfg.update(kw)
        return tk.Label(pai, text=texto, **cfg)

    def _botao(self, pai, texto, comando, principal=False):
        return tk.Button(
            pai, text=texto, command=comando, relief="flat", cursor="hand2",
            font=("Segoe UI", 10, "bold" if principal else "normal"),
            bg=COR["mate"] if principal else COR["campo"],
            fg=COR["fundo"] if principal else COR["texto"],
            activebackground="#2c8f68" if principal else COR["linha"],
            activeforeground=COR["fundo"] if principal else COR["texto"],
            bd=0, padx=18, pady=9, disabledforeground=COR["texto3"],
        )

    def _monta(self):
        pad = dict(padx=28)

        tk.Label(self, text="SLT", bg=COR["fundo"], fg=COR["mate"],
                 font=("Segoe UI", 22, "bold"), anchor="w").pack(fill="x", pady=(26, 0), **pad)
        tk.Label(self, text="Gestão de Gastos", bg=COR["fundo"], fg=COR["texto"],
                 font=("Segoe UI", 15), anchor="w").pack(fill="x", **pad)
        self._rotulo(
            self,
            "Coloque numa pasta as planilhas que você baixa do site do Nota Fiscal "
            "Gaúcha — uma por pessoa. O programa consulta cada nota na SEFAZ-RS, "
            "salva tudo em disco e monta o relatório.",
            wraplength=740, fg=COR["texto3"],
        ).pack(fill="x", pady=(10, 0), **pad)

        # ---------------- pasta de entrada
        caixa = tk.Frame(self, bg=COR["fundo"])
        caixa.pack(fill="x", pady=(22, 0), **pad)
        self._rotulo(caixa, "Pasta com as planilhas (.xlsx)").pack(fill="x")
        linha = tk.Frame(caixa, bg=COR["fundo"])
        linha.pack(fill="x", pady=(6, 0))
        self.campo_entrada = tk.Entry(
            linha, textvariable=self.entrada, bg=COR["campo"], fg=COR["texto"],
            insertbackground=COR["texto"], relief="flat", font=("Consolas", 10),
            highlightthickness=1, highlightbackground=COR["linha"],
            highlightcolor=COR["mate"])
        self.campo_entrada.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self._botao(linha, "Escolher…", self._escolher_entrada).pack(side="left")

        # ---------------- pasta de saída
        caixa2 = tk.Frame(self, bg=COR["fundo"])
        caixa2.pack(fill="x", pady=(16, 0), **pad)
        self._rotulo(caixa2, "Onde salvar o resultado").pack(fill="x")
        linha2 = tk.Frame(caixa2, bg=COR["fundo"])
        linha2.pack(fill="x", pady=(6, 0))
        self.campo_saida = tk.Entry(
            linha2, textvariable=self.saida, bg=COR["campo"], fg=COR["texto"],
            insertbackground=COR["texto"], relief="flat", font=("Consolas", 10),
            highlightthickness=1, highlightbackground=COR["linha"],
            highlightcolor=COR["mate"])
        self.campo_saida.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self._botao(linha2, "Escolher…", self._escolher_saida).pack(side="left")

        # ---------------- ação
        acao = tk.Frame(self, bg=COR["fundo"])
        acao.pack(fill="x", pady=(22, 0), **pad)
        self.btn_ir = self._botao(acao, "Analisar", self._comecar, principal=True)
        self.btn_ir.pack(side="left")
        self.btn_parar = self._botao(acao, "Cancelar", self._pedir_cancelar)
        self.btn_parar.pack(side="left", padx=(10, 0))
        self.btn_parar.configure(state="disabled")
        self.btn_abrir = self._botao(acao, "Abrir relatório", self._abrir_relatorio)
        self.btn_abrir.pack(side="right")
        self.btn_abrir.configure(state="disabled")
        self.btn_pasta = self._botao(acao, "Abrir pasta", self._abrir_pasta)
        self.btn_pasta.pack(side="right", padx=(0, 10))
        self.btn_pasta.configure(state="disabled")

        # ---------------- progresso
        self.barra = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.barra.pack(fill="x", pady=(20, 6), **pad)
        self.status = self._rotulo(self, "Pronto para começar.", fg=COR["texto"])
        self.status.pack(fill="x", **pad)

        # ---------------- registro
        moldura = tk.Frame(self, bg=COR["linha"])
        moldura.pack(fill="both", expand=True, pady=(16, 24), **pad)
        self.log = tk.Text(
            moldura, bg=COR["painel"], fg=COR["texto2"], relief="flat",
            font=("Consolas", 9), wrap="word", padx=14, pady=12, state="disabled",
            height=8, insertbackground=COR["texto"])
        self.log.pack(fill="both", expand=True, padx=1, pady=1)
        self.log.tag_configure("ok", foreground=COR["mate"])
        self.log.tag_configure("erro", foreground=COR["erro"])
        self.log.tag_configure("fraco", foreground=COR["texto3"])

    # ------------------------------------------------------------ eventos
    def _escolher_entrada(self):
        p = filedialog.askdirectory(title="Pasta com as planilhas do Nota Fiscal Gaúcha")
        if not p:
            return
        self.entrada.set(os.path.normpath(p))
        if not self.saida.get():
            self.saida.set(_pasta_padrao_saida(os.path.normpath(p)))

    def _escolher_saida(self):
        p = filedialog.askdirectory(title="Onde salvar o resultado")
        if p:
            self.saida.set(os.path.normpath(p))

    def _diz(self, texto, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _comecar(self):
        entrada = self.entrada.get().strip()
        if not entrada or not os.path.isdir(entrada):
            messagebox.showwarning(APP, "Escolha a pasta onde estão as planilhas.")
            return
        saida = self.saida.get().strip() or _pasta_padrao_saida(entrada)
        self.saida.set(saida)

        self.rodando = True
        self.cancelar.clear()
        self.resultado = None
        self.btn_ir.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        self.btn_abrir.configure(state="disabled")
        self.btn_pasta.configure(state="disabled")
        self.barra.configure(value=0)
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._diz("Iniciando…", "fraco")

        def trabalho():
            r = executar(
                entrada, saida,
                aviso=lambda t: self.fila.put(("msg", t)),
                cancelado=self.cancelar.is_set,
                passo=lambda f, feito, total: self.fila.put(("passo", (f, feito, total))),
            )
            self.fila.put(("fim", r))

        threading.Thread(target=trabalho, daemon=True).start()

    def _pedir_cancelar(self):
        self.cancelar.set()
        self.status.configure(text="Cancelando…")

    def _drena(self):
        try:
            while True:
                tipo, carga = self.fila.get_nowait()
                if tipo == "msg":
                    self._diz(carga)
                    self.status.configure(text=carga)
                elif tipo == "passo":
                    fase, feito, total = carga
                    pct = 100 * feito / total if total else 0
                    self.barra.configure(value=pct)
                    if fase == "baixando":
                        self.status.configure(
                            text=f"Consultando a SEFAZ-RS — nota {feito} de {total}")
                    elif fase == "gravando":
                        self.status.configure(text=f"Gravando — {feito} de {total}")
                elif tipo == "fim":
                    self._terminou(carga)
        except queue.Empty:
            pass
        self.after(120, self._drena)

    def _terminou(self, r):
        self.rodando = False
        self.btn_ir.configure(state="normal")
        self.btn_parar.configure(state="disabled")
        self.resultado = r

        if not r.ok:
            self.barra.configure(value=0)
            self.status.configure(text="Não deu certo.")
            self._diz("\n" + r.erro, "erro")
            if r.pasta_saida and os.path.isdir(r.pasta_saida):
                self.btn_pasta.configure(state="normal")
            messagebox.showerror(APP, r.erro.split("\n\n")[0])
            return

        self.barra.configure(value=100)
        quem = " e ".join(r.pessoas)
        self.status.configure(text="Pronto — relatório gerado.")
        self._diz("")
        self._diz(f"{'Família' if r.familia else 'Pessoa'}: {quem}", "ok")
        self._diz(f"{r.baixadas} notas detalhadas · {r.itens} itens", "ok")
        if r.m55:
            self._diz(f"{r.m55} NF-e modelo 55 sem consulta pública (entram pelo valor "
                      "da planilha, sem itens)", "fraco")
        if r.falhas:
            self._diz(f"{r.falhas} chave(s) não baixaram — veja chaves_com_falha.csv", "erro")
        for a in r.avisos[:8]:
            self._diz("aviso: " + a, "fraco")
        self._diz("")
        self._diz("Relatório: " + r.relatorio, "ok")
        self._diz("Notas:     " + r.pasta_notas, "ok")

        self.btn_abrir.configure(state="normal")
        self.btn_pasta.configure(state="normal")
        if messagebox.askyesno(APP, "Análise concluída.\n\nAbrir o relatório agora?"):
            self._abrir_relatorio()

    def _abrir_relatorio(self):
        if self.resultado and self.resultado.relatorio:
            webbrowser.open("file:///" + self.resultado.relatorio.replace("\\", "/"))

    def _abrir_pasta(self):
        alvo = (self.resultado.pasta_saida if self.resultado else self.saida.get())
        if alvo and os.path.isdir(alvo):
            if sys.platform == "win32":
                os.startfile(alvo)  # noqa: S606
            else:
                subprocess.Popen(["xdg-open", alvo])

    def _fechar(self):
        if self.rodando and not messagebox.askyesno(
                APP, "A análise ainda está rodando. Fechar mesmo assim?"):
            return
        self.cancelar.set()
        self.destroy()


def main():
    Janela().mainloop()
