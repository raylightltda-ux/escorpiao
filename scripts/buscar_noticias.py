#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import xml.etree.ElementTree as ET
import unicodedata
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote

class BuscadorNoticias:

    def __init__(self):
        self.noticias = []

        self.termos = [
            "escorpião Brasil",
            "escorpiões Brasil",
            "picada escorpião",
            "picada de escorpião",
            "acidente escorpiônico",
            "escorpionismo",
            "infestação escorpiões",
            "infestação de escorpiões",
            "escorpião amarelo",
            "soro antiescorpiônico",
            "animais peçonhentos escorpião",
            "prefeitura escorpião",
            "vigilância escorpião",
            "vigilância sanitária escorpião",
            "alerta escorpiões",
            "controle de escorpiões",
            "captura de escorpiões",
            "prevenção escorpiões",
            "criança escorpião",
            "morte escorpião",
            "escorpião prefeitura municipal",
            "escorpiões prefeitura municipal",
            "escorpião vigilância ambiental",
            "escorpiões vigilância ambiental"
        ]

        self.estados = {
            "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
            "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
            "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
            "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba",
            "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
            "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
            "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
            "TO": "Tocantins"
        }

        self.cidade_estado = self.carregar_cidades_ibge()

        self.correcoes_manuais = {
            "sao manuel": "SP",
            "jaguariuna": "SP",
            "mococa": "SP",
            "votuporanga": "SP",
            "birigui": "SP",
            "conchal": "SP",
            "cacapava": "SP",
            "sao carlos": "SP",
            "votorantim": "SP",
            "tijucas": "SC",
            "gravatal": "SC",
            "xanxere": "SC",
            "itajai": "SC",
            "biguacu": "SC",
            "braco do norte": "SC",
            "mafra": "SC",
            "esteio": "RS",
            "sapucaia do sul": "RS",
            "sao leopoldo": "RS",
            "presidente kennedy": "ES",
            "laranja da terra": "ES",
            "rio largo": "AL",
            "buzios": "RJ",
            "ibipora": "PR"
        }

        self.cidade_estado.update(self.correcoes_manuais)

    def sem_acento(self, texto):
        texto = unicodedata.normalize("NFD", texto)
        texto = texto.encode("ascii", "ignore").decode("utf-8")
        return texto.lower().strip()

    def normalizar(self, texto):
        texto = self.sem_acento(texto)
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    def carregar_cidades_ibge(self):
        cidades = {}

        try:
            url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
            response = requests.get(url, timeout=20)
            response.raise_for_status()

            dados = response.json()

            for item in dados:
                nome = item.get("nome", "")
                uf = item.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("sigla", "")

                if nome and uf:
                    chave = self.normalizar(nome)
                    cidades[chave] = uf

            print(f"✅ {len(cidades)} municípios carregados do IBGE")

        except Exception as e:
            print(f"⚠️ Não foi possível carregar municípios do IBGE: {e}")

        return cidades

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
        texto = texto.replace("&nbsp;", " ").replace("&amp;", "&")
        texto = texto.replace("&#39;", "'").replace("&quot;", '"')
        return texto.strip()

    def normalizar_titulo(self, titulo):
        titulo = self.normalizar(titulo)
        titulo = re.sub(r" - .*?$", "", titulo)
        titulo = re.sub(r" \| .*?$", "", titulo)
        return titulo.strip()

    def gerar_id(self, titulo, link):
        base = self.normalizar_titulo(titulo)
        base = re.sub(r"[^a-z0-9]", "", base)
        return base[:150]

    def converter_data(self, pub_date):
        try:
            dt = parsedate_to_datetime(pub_date)

            if dt.year < 2026:
                return None

            return dt.strftime("%d/%m/%Y")
        except:
            return None

    def noticia_valida(self, titulo, descricao):
        texto = self.normalizar(f"{titulo} {descricao}")

        bloqueios = [
            "horoscopo", "signo", "zodiaco", "astrologia",
            "taro", "previsao do dia", "escorpiao do signo",
            "signo de escorpiao", "cinema", "filme", "serie",
            "streaming", "netflix", "marvel", "dc comics",
            "personagem", "trailer", "bilheteria", "ator", "atriz",
            "musica", "show", "celebridade", "famosos", "bbb", "plantas para espantar",
            "planta para espantar", "espantar escorpiao", "espantar escorpioes", "repelente natural",
            "remedio caseiro", "remédio caseiro", "dicas caseiras", "simpatia", "feng shui", "jardinagem",
            "plantas repelentes", "lavanda", "hortela", "hortelã","alecrim"
        ]

        if any(b in texto for b in bloqueios):
            return False

        tem_escorpiao = any(t in texto for t in [
            "escorpiao", "escorpioes", "escorpionismo",
            "escorpionico", "escorpionica"
        ])

        if not tem_escorpiao:
            return False

        contexto_valido = [
            "picada", "acidente", "morte", "morreu", "obito",
            "soro", "antiescorpionico", "hospital", "atendimento",
            "crianca", "bebe", "infestacao", "aparecimento",
            "aumento", "prefeitura", "vigilancia", "saude",
            "alerta", "prevencao", "controle", "captura",
            "mutirao", "orienta", "orientacao",
            "animais peconhentos", "animal peconhento", "peconhentos",
            "residencia", "residencias",
            "casa", "casas",
            "morador", "moradores",
            "condominio", "condominios",
            "terreno", "lote",
            "bairro", "bairros",
            "verao", "chuvas", "calor",
            "limpeza", "entulho", "lixo",
            "dedetizacao", "dedetizadora",
            "controle de pragas",
            "risco", "perigo",
            "registro", "registra",
            "casos", "ocorrencias",
            "escorpiao amarelo",
            "escorpioes amarelos"
        ]

        return any(c in texto for c in contexto_valido)

    def detectar_gravidade(self, texto):
        t = self.normalizar(texto)

        if any(p in t for p in ["morte", "morre", "morreu", "obito", "uti", "estado grave", "fatal"]):
            return "grave"

        if any(p in t for p in ["picada", "acidente", "soro", "hospital", "atendimento", "infestacao"]):
            return "moderada"

        return "leve"

    def detectar_estado(self, texto):
        t = f" {self.normalizar(texto)} "

        cidades_ordenadas = sorted(self.cidade_estado.keys(), key=len, reverse=True)

        for cidade in cidades_ordenadas:
            if len(cidade) < 4:
                continue

            padrao = r"\b" + re.escape(cidade) + r"\b"

            if re.search(padrao, t):
                return self.cidade_estado[cidade]

        estados_extenso = {
            "acre": "AC",
            "alagoas": "AL",
            "amapa": "AP",
            "amazonas": "AM",
            "bahia": "BA",
            "ceara": "CE",
            "distrito federal": "DF",
            "espirito santo": "ES",
            "goias": "GO",
            "maranhao": "MA",
            "mato grosso do sul": "MS",
            "mato grosso": "MT",
            "minas gerais": "MG",
            "paraiba": "PB",
            "parana": "PR",
            "pernambuco": "PE",
            "piaui": "PI",
            "rio de janeiro": "RJ",
            "rio grande do norte": "RN",
            "rio grande do sul": "RS",
            "rondonia": "RO",
            "roraima": "RR",
            "santa catarina": "SC",
            "sao paulo": "SP",
            "sergipe": "SE",
            "tocantins": "TO"
        }

        for nome, uf in estados_extenso.items():
            if nome in t:
                return uf

        # Pará é perigoso porque "para" aparece como preposição.
        # Só classifica PA se houver contexto claro.
        if "estado do para" in t or "governo do para" in t or "belem" in t:
            return "PA"

        return "Não identificado"

    def detectar_cidade(self, titulo, descricao, estado):
        texto = f" {self.normalizar(titulo + ' ' + descricao)} "

        cidades_ordenadas = sorted(self.cidade_estado.keys(), key=len, reverse=True)

        for cidade in cidades_ordenadas:
            if len(cidade) < 4:
                continue

            uf = self.cidade_estado[cidade]

            if estado != "Não identificado" and uf != estado:
                continue

            padrao = r"\b" + re.escape(cidade) + r"\b"

            if re.search(padrao, texto):
                return self.formatar_cidade(cidade)

        return "Não identificada"

    def formatar_cidade(self, cidade):
        excecoes = {
            "sao paulo": "São Paulo",
            "sao jose do rio preto": "São José do Rio Preto",
            "ribeirao preto": "Ribeirão Preto",
            "jau": "Jaú",
            "bauru": "Bauru",
            "ibipora": "Ibiporã",
            "maringa": "Maringá",
            "londrina": "Londrina",
            "curitiba": "Curitiba",
            "tijucas": "Tijucas",
            "xanxere": "Xanxerê",
            "itajai": "Itajaí",
            "biguacu": "Biguaçu",
            "braco do norte": "Braço do Norte",
            "sao leopoldo": "São Leopoldo",
            "sapucaia do sul": "Sapucaia do Sul",
            "vitoria": "Vitória",
            "presidente kennedy": "Presidente Kennedy",
            "laranja da terra": "Laranja da Terra",
            "buzios": "Búzios",
            "rio largo": "Rio Largo",
            "brasilia": "Brasília"
        }

        if cidade in excecoes:
            return excecoes[cidade]

        return " ".join(p.capitalize() for p in cidade.split())

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

                for item in root.findall(".//item")[:50]:
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
                    print(f"✅ {data} | {estado} | {cidade} | {titulo[:80]}")

            except Exception as e:
                print(f"❌ Erro no termo '{termo}': {e}")

    def salvar_noticias(self):
        existentes = self.carregar_existentes()

        ids_existentes = set()

        for n in existentes:
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
        print("🦂 MONITOR DE ESCORPIÕES - BUSCA COM MUNICÍPIOS IBGE")
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("=" * 70)

        self.buscar_google_rss()
        self.salvar_noticias()

        print("=" * 70)
        print("✅ FINALIZADO")
        print("=" * 70)

if __name__ == "__main__":
    BuscadorNoticias().executar()
