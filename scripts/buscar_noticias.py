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

        self.termos_base = [
            "escorpião",
            "escorpiões",
            "escorpionismo",
            "acidente escorpiônico",
            "picada de escorpião",
            "criança picada escorpião",
            "morte escorpião",
            "soro antiescorpiônico",
            "escorpião amarelo",
            "Tityus serrulatus",
            "infestação de escorpiões",
            "animais peçonhentos escorpião",
            "vigilância escorpião",
            "prefeitura escorpião",
            "surto de escorpiões"
        ]

        self.estados = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }

        self.cidades_referencia = {
            "SP": ["São Paulo", "Campinas", "Ribeirão Preto", "Sorocaba", "Bauru", "Marília", "Presidente Prudente", "Araçatuba", "São José do Rio Preto", "Piracicaba", "Limeira"],
            "PR": ["Curitiba", "Londrina", "Maringá", "Cascavel", "Foz do Iguaçu", "Ponta Grossa", "Toledo", "Assis Chateaubriand"],
            "MG": ["Belo Horizonte", "Uberlândia", "Uberaba", "Montes Claros", "Juiz de Fora", "Divinópolis", "Governador Valadares"],
            "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias", "Nova Iguaçu", "Campos dos Goytacazes"],
            "BA": ["Salvador", "Feira de Santana", "Vitória da Conquista", "Juazeiro", "Ilhéus"],
            "GO": ["Goiânia", "Anápolis", "Rio Verde", "Aparecida de Goiânia"],
            "MT": ["Cuiabá", "Rondonópolis", "Sinop", "Várzea Grande"],
            "MS": ["Campo Grande", "Dourados", "Três Lagoas"],
            "SC": ["Florianópolis", "Joinville", "Blumenau", "Chapecó", "Criciúma"],
            "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Santa Maria"],
            "PE": ["Recife", "Caruaru", "Petrolina"],
            "CE": ["Fortaleza", "Juazeiro do Norte", "Sobral"],
            "PA": ["Belém", "Santarém", "Marabá"],
            "PB": ["João Pessoa", "Campina Grande"],
            "RN": ["Natal", "Mossoró"],
            "AL": ["Maceió", "Arapiraca"],
            "SE": ["Aracaju"],
            "ES": ["Vitória", "Vila Velha", "Serra", "Cariacica"],
            "DF": ["Brasília"]
        }

        self.fontes_site = [
            "site:g1.globo.com escorpião",
            "site:gov.br escorpião",
            "site:agenciabrasil.ebc.com.br escorpião",
            "site:uol.com.br escorpião",
            "site:terra.com.br escorpião",
            "site:metropoles.com escorpião",
            "site:cnnbrasil.com.br escorpião",
            "site:prefeitura escorpião",
            "site:saude escorpião",
            "site:vigilancia escorpião"
        ]

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
        texto = texto.replace("&#39;", "'")
        texto = texto.replace("&quot;", '"')
        return texto.strip()

    def gerar_id(self, titulo, link):
        base = (titulo + link).lower()
        base = re.sub(r"[^a-z0-9áéíóúãõâêôç]", "", base)
        return base[:160]

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
            "escorpionismo", "acidente escorpiônico", "acidente escorpionico",
            "picada", "soro antiescorpiônico", "soro antiescorpionico",
            "tityus serrulatus", "animal peçonhento", "animais peçonhentos"
        ]

        return any(t in texto for t in termos_validos)

    def detectar_gravidade(self, texto):
        t = texto.lower()

        graves = [
            "morte", "morre", "morreu", "óbito", "obito",
            "uti", "estado grave", "fatal", "criança morre",
            "bebê morre", "bebe morre"
        ]

        moderadas = [
            "picada", "acidente", "soro", "hospital",
            "atendimento", "infestação", "infestacao",
            "vigilância", "vigilancia", "prefeitura"
        ]

        if any(p in t for p in graves):
            return "grave"

        if any(p in t for p in moderadas):
            return "moderada"

        return "leve"

    def detectar_estado(self, texto):
        t = f" {texto.lower()} "

        for uf, nome in self.estados.items():
            nome_lower = nome.lower()

            if nome_lower in t:
                return uf

            if f" {uf.lower()} " in t or f"-{uf.lower()}" in t or f"/{uf.lower()}" in t:
                return uf

        for uf, cidades in self.cidades_referencia.items():
            for cidade in cidades:
                if cidade.lower() in t:
                    return uf

        return "Nacional"

    def detectar_cidade(self, titulo, descricao, estado):
        texto = f"{titulo} {descricao}"

        if estado in self.cidades_referencia:
            for cidade in self.cidades_referencia[estado]:
                if cidade.lower() in texto.lower():
                    return cidade

        padroes = [
            r"em ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"no município de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"na cidade de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})"
        ]

        bloqueios = [
            "Brasil", "Google", "News", "Escorpião", "Escorpiões",
            "Hospital", "Prefeitura", "Secretaria", "Estado",
            "Ministério", "Vigilância", "Saúde", "Criança",
            "Animal", "Animais", "Homem", "Mulher"
        ]

        for padrao in padroes:
            m = re.search(padrao, texto)
            if m:
                cidade = m.group(1).strip()
                if cidade not in bloqueios and len(cidade) > 2:
                    return cidade

        return "Não identificada"

    def converter_data(self, pub_date):
        try:
            dt = parsedate_to_datetime(pub_date)

            if dt.year < 2026:
                return None

            return dt.strftime("%d/%m/%Y")

        except:
            return None

    def gerar_consultas(self):
        consultas = []

        for termo in self.termos_base:
            consultas.append(termo)

        for termo in [
            "escorpião",
            "picada de escorpião",
            "acidente escorpiônico",
            "escorpionismo",
            "infestação de escorpiões"
        ]:
            for uf, nome in self.estados.items():
                consultas.append(f"{termo} {nome}")
                consultas.append(f"{termo} {uf}")

        for fonte in self.fontes_site:
            consultas.append(fonte)

        consultas_unicas = []
        vistos = set()

        for c in consultas:
            chave = c.lower().strip()
            if chave not in vistos:
                consultas_unicas.append(c)
                vistos.add(chave)

        return consultas_unicas

    def buscar_google_rss(self):
        print("🔍 Buscando Google News RSS ampliado...")

        consultas = self.gerar_consultas()

        for termo in consultas:

            try:
                url = (
                    "https://news.google.com/rss/search?"
                    f"q={quote(termo)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
                )

                response = requests.get(url, timeout=20)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                for item in root.findall(".//item")[:20]:

                    titulo = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    descricao = self.limpar_html(item.findtext("description", ""))

                    data = self.converter_data(pub_date)

                    if not data:
                        continue

                    if not titulo or not link:
                        continue

                    if not self.noticia_valida(titulo, descricao):
                        continue

                    texto = f"{titulo} {descricao}"

                    estado = self.detectar_estado(texto)
                    cidade = self.detectar_cidade(titulo, descricao, estado)

                    noticia = {
                        "id": self.gerar_id(titulo, link),
                        "titulo": titulo,
                        "descricao": descricao if descricao else titulo,
                        "link": link,
                        "data": data,
                        "tipo": "alerta",
                        "gravidade": self.detectar_gravidade(texto),
                        "fonte": "Google News",
                        "estado": estado,
                        "cidade": cidade,
                        "termo_busca": termo
                    }

                    self.noticias.append(noticia)

                    print(f"✅ {data} | {estado} | {cidade} | {titulo[:70]}")

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
        print("🦂 MONITOR DE ESCORPIÕES - BUSCA AMPLIADA")
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("=" * 70)

        self.buscar_google_rss()
        self.salvar_noticias()

        print("=" * 70)
        print("✅ FINALIZADO")
        print("=" * 70)

if __name__ == "__main__":
    BuscadorNoticias().executar()
