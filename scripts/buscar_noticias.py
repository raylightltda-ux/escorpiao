#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote

class BuscadorNoticias:

    def __init__(self):
        self.noticias = []

        self.termos = [
            "escorpião Brasil",
            "escorpiões Brasil",
            "picada de escorpião",
            "acidente escorpiônico",
            "infestação de escorpiões",
            "soro antiescorpiônico",
            "criança picada escorpião",
            "morte escorpião",
            "escorpião prefeitura",
            "escorpião vigilância sanitária"
        ]

        self.estados = {
            "AC": ["acre", " ac "],
            "AL": ["alagoas", " al "],
            "AP": ["amapá", "amapa", " ap "],
            "AM": ["amazonas", " am "],
            "BA": ["bahia", " ba "],
            "CE": ["ceará", "ceara", " ce "],
            "DF": ["distrito federal", " df ", "brasília", "brasilia"],
            "ES": ["espírito santo", "espirito santo", " es "],
            "GO": ["goiás", "goias", " go "],
            "MA": ["maranhão", "maranhao", " ma "],
            "MT": ["mato grosso", " mt "],
            "MS": ["mato grosso do sul", " ms "],
            "MG": ["minas gerais", " mg "],
            "PA": ["pará", "para", " pa "],
            "PB": ["paraíba", "paraiba", " pb "],
            "PR": ["paraná", "parana", " pr "],
            "PE": ["pernambuco", " pe "],
            "PI": ["piauí", "piaui", " pi "],
            "RJ": ["rio de janeiro", " rj "],
            "RN": ["rio grande do norte", " rn "],
            "RS": ["rio grande do sul", " rs "],
            "RO": ["rondônia", "rondonia", " ro "],
            "RR": ["roraima", " rr "],
            "SC": ["santa catarina", " sc "],
            "SP": ["são paulo", "sao paulo", " sp "],
            "SE": ["sergipe", " se "],
            "TO": ["tocantins", " to "]
        }

    def carregar_existentes(self):
        if os.path.exists("noticias.json"):
            try:
                with open("noticias.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def limpar_html(self, texto):
        if not texto:
            return ""
        texto = re.sub(r"<.*?>", "", texto)
        texto = texto.replace("&nbsp;", " ")
        texto = texto.replace("&amp;", "&")
        return texto.strip()

    def normalizar(self, texto):
        return f" {texto.lower()} "

    def gerar_id(self, titulo, link):
        base = (titulo + link).lower()
        base = re.sub(r"[^a-z0-9áéíóúãõâêôç]", "", base)
        return base[:120]

    def detectar_gravidade(self, texto):
        t = texto.lower()

        graves = [
            "morte", "morre", "morreu", "óbito", "obito",
            "uti", "internado", "estado grave", "fatal"
        ]

        moderadas = [
            "picada", "acidente", "soro", "hospital",
            "atendimento", "infestação", "infestacao"
        ]

        if any(p in t for p in graves):
            return "grave"

        if any(p in t for p in moderadas):
            return "moderada"

        return "leve"

    def detectar_estado(self, texto):
        t = self.normalizar(texto)

        for uf, termos in self.estados.items():
            for termo in termos:
                if termo in t:
                    return uf

        return "Nacional"

    def detectar_cidade(self, titulo, descricao):
        texto = f"{titulo} {descricao}"

        padroes = [
            r"em ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"no município de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"na cidade de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})"
        ]

        bloqueios = [
            "Brasil", "Google", "News", "Escorpião", "Escorpiões",
            "Hospital", "Prefeitura", "Secretaria", "Estado",
            "Ministério", "Vigilância", "Saúde"
        ]

        for padrao in padroes:
            m = re.search(padrao, texto)
            if m:
                cidade = m.group(1).strip()
                if cidade not in bloqueios and len(cidade) > 2:
                    return cidade

        return "Não identificada"

    def converter_data(self, pub_date):
        if not pub_date:
            return datetime.now().strftime("%d/%m/%Y")

        try:
            dt = parsedate_to_datetime(pub_date)
            return dt.strftime("%d/%m/%Y")
        except:
            return datetime.now().strftime("%d/%m/%Y")

    def noticia_valida(self, titulo, descricao):
        texto = f"{titulo} {descricao}".lower()

        bloqueios = [
            "horóscopo", "horoscopo", "signo", "zodíaco", "zodiaco",
            "astrologia", "previsão do dia", "previsao do dia",
            "escorpião do signo", "signo de escorpião"
        ]

        if any(b in texto for b in bloqueios):
            return False

        termos_validos = [
            "escorpião", "escorpiões", "escorpiao", "escorpioes",
            "picada", "acidente escorpiônico", "soro antiescorpiônico"
        ]

        return any(t in texto for t in termos_validos)

    def buscar_google_rss(self):
        print("🔍 Buscando Google News RSS...")

        for termo in self.termos:
            try:
                url = (
                    "https://news.google.com/rss/search?"
                    f"q={quote(termo)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
                )

                response = requests.get(url, timeout=20)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                for item in root.findall(".//item")[:25]:

                    titulo = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    descricao = self.limpar_html(item.findtext("description", ""))

                    try:
                        dt_publicacao = parsedate_to_datetime(pub_date)

                        if dt_publicacao.year < 2026:
                            continue

                    except:
                        continue

                    if not titulo or not link:
                        continue

                    if not self.noticia_valida(titulo, descricao):
                        continue

                    texto = f"{titulo} {descricao}"

                    noticia = {
                        "id": self.gerar_id(titulo, link),
                        "titulo": titulo,
                        "descricao": descricao if descricao else titulo,
                        "link": link,
                        "data": self.converter_data(pub_date),
                        "tipo": "alerta",
                        "gravidade": self.detectar_gravidade(texto),
                        "fonte": "Google News",
                        "estado": self.detectar_estado(texto),
                        "cidade": self.detectar_cidade(titulo, descricao)
                    }

                    self.noticias.append(noticia)
                    print(f"✅ {noticia['data']} | {noticia['estado']} | {titulo[:80]}")

            except Exception as e:
                print(f"❌ Erro no termo '{termo}': {e}")

    def salvar_noticias(self):
        existentes = self.carregar_existentes()

        ids_existentes = set()

        for n in existentes:
            if "id" not in n:
                n["id"] = self.gerar_id(n.get("titulo", ""), n.get("link", ""))
            ids_existentes.add(n["id"])

        novas = 0

        for noticia in self.noticias:
            if noticia["id"] not in ids_existentes:
                existentes.append(noticia)
                ids_existentes.add(noticia["id"])
                novas += 1

        def chave_data(n):
            try:
                return datetime.strptime(n.get("data", "01/01/1900"), "%d/%m/%Y")
            except:
                return datetime(1900, 1, 1)

        existentes.sort(key=chave_data, reverse=True)

        with open("noticias.json", "w", encoding="utf-8") as f:
            json.dump(existentes, f, ensure_ascii=False, indent=2)

        print(f"\n📰 Total salvo: {len(existentes)}")
        print(f"🆕 Novas notícias: {novas}")

    def executar(self):
        print("=" * 70)
        print("🦂 MONITOR DE ESCORPIÕES")
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("=" * 70)

        self.buscar_google_rss()
        self.salvar_noticias()

        print("=" * 70)
        print("✅ FINALIZADO")
        print("=" * 70)

if __name__ == "__main__":
    BuscadorNoticias().executar()
