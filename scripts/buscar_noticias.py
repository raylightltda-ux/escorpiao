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
            "morte escorpião"
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

        self.cidade_estado = {
            # SÃO PAULO
            "são paulo": "SP", "sao paulo": "SP",
            "campinas": "SP",
            "ribeirão preto": "SP", "ribeirao preto": "SP",
            "sorocaba": "SP",
            "bauru": "SP",
            "marília": "SP", "marilia": "SP",
            "presidente prudente": "SP",
            "araçatuba": "SP", "aracatuba": "SP",
            "são josé do rio preto": "SP", "sao jose do rio preto": "SP",
            "piracicaba": "SP",
            "limeira": "SP",
            "jundiaí": "SP", "jundiai": "SP",
            "franca": "SP",
            "araraquara": "SP",
            "barretos": "SP",
            "botucatu": "SP",
            "assis": "SP",
            "ourinhos": "SP",
            "itapetininga": "SP",
            "americana": "SP",
            "sumaré": "SP", "sumare": "SP",
            "hortolândia": "SP", "hortolandia": "SP",
            "mogi das cruzes": "SP",
            "osasco": "SP",
            "santos": "SP",
            "guarulhos": "SP",
            "são bernardo do campo": "SP", "sao bernardo do campo": "SP",
            "santo andré": "SP", "santo andre": "SP",
            "diadema": "SP",
            "taubaté": "SP", "taubate": "SP",
            "jacareí": "SP", "jacarei": "SP",
            "caraguatatuba": "SP",
            "ubatuba": "SP",
            "itanhaém": "SP", "itanhaem": "SP",

            # PARANÁ
            "curitiba": "PR",
            "londrina": "PR",
            "maringá": "PR", "maringa": "PR",
            "cascavel": "PR",
            "foz do iguaçu": "PR", "foz do iguacu": "PR",
            "ponta grossa": "PR",
            "toledo": "PR",
            "assis chateaubriand": "PR",
            "umuarama": "PR",
            "guarapuava": "PR",
            "paranavaí": "PR", "paranavai": "PR",
            "campo mourão": "PR", "campo mourao": "PR",
            "ibiporã": "PR", "ibipora": "PR",
            "cambé": "PR", "cambe": "PR",
            "arapongas": "PR",
            "rolândia": "PR", "rolandia": "PR",
            "apucarana": "PR",
            "cornélio procópio": "PR", "cornelio procopio": "PR",
            "jacarezinho": "PR",
            "bandeirantes": "PR",
            "ivaiporã": "PR", "ivaipora": "PR",
            "medianeira": "PR",
            "marechal cândido rondon": "PR", "marechal candido rondon": "PR",
            "palotina": "PR",
            "guaíra": "PR", "guaira": "PR",
            "francisco beltrão": "PR", "francisco beltrao": "PR",
            "pato branco": "PR",
            "cianorte": "PR",
            "paranaguá": "PR", "paranagua": "PR",

            # MINAS GERAIS
            "belo horizonte": "MG",
            "uberlândia": "MG", "uberlandia": "MG",
            "uberaba": "MG",
            "montes claros": "MG",
            "juiz de fora": "MG",
            "divinópolis": "MG", "divinopolis": "MG",
            "governador valadares": "MG",
            "pouso alegre": "MG",
            "patos de minas": "MG",
            "teófilo otoni": "MG", "teofilo otoni": "MG",
            "contagem": "MG",
            "betim": "MG",
            "ipatinga": "MG",
            "sete lagoas": "MG",
            "varginha": "MG",
            "poços de caldas": "MG", "pocos de caldas": "MG",

            # GOIÁS
            "goiânia": "GO", "goiania": "GO",
            "anápolis": "GO", "anapolis": "GO",
            "rio verde": "GO",
            "aparecida de goiânia": "GO", "aparecida de goiania": "GO",
            "luziânia": "GO", "luziania": "GO",
            "jataí": "GO", "jatai": "GO",

            # MATO GROSSO
            "cuiabá": "MT", "cuiaba": "MT",
            "rondonópolis": "MT", "rondonopolis": "MT",
            "sinop": "MT",
            "várzea grande": "MT", "varzea grande": "MT",
            "sorriso": "MT",

            # MATO GROSSO DO SUL
            "campo grande": "MS",
            "dourados": "MS",
            "três lagoas": "MS", "tres lagoas": "MS",
            "corumbá": "MS", "corumba": "MS",

            # BAHIA
            "salvador": "BA",
            "feira de santana": "BA",
            "vitória da conquista": "BA", "vitoria da conquista": "BA",
            "juazeiro": "BA",
            "ilhéus": "BA", "ilheus": "BA",
            "itabuna": "BA",
            "barreiras": "BA",
            "jequié": "BA", "jequie": "BA",

            # PERNAMBUCO
            "recife": "PE",
            "caruaru": "PE",
            "petrolina": "PE",
            "jaboatão dos guararapes": "PE", "jaboatao dos guararapes": "PE",
            "olinda": "PE",

            # CEARÁ
            "fortaleza": "CE",
            "juazeiro do norte": "CE",
            "sobral": "CE",
            "crato": "CE",

            # RIO DE JANEIRO
            "rio de janeiro": "RJ",
            "niterói": "RJ", "niteroi": "RJ",
            "duque de caxias": "RJ",
            "nova iguaçu": "RJ", "nova iguacu": "RJ",
            "campos dos goytacazes": "RJ",
            "volta redonda": "RJ",
            "petrópolis": "RJ", "petropolis": "RJ",

            # SANTA CATARINA
            "florianópolis": "SC", "florianopolis": "SC",
            "joinville": "SC",
            "blumenau": "SC",
            "chapecó": "SC", "chapeco": "SC",
            "criciúma": "SC", "criciuma": "SC",

            # RIO GRANDE DO SUL
            "porto alegre": "RS",
            "caxias do sul": "RS",
            "pelotas": "RS",
            "santa maria": "RS",
            "passo fundo": "RS",

            # PARÁ
            "belém": "PA", "belem": "PA",
            "santarém": "PA", "santarem": "PA",
            "marabá": "PA", "maraba": "PA",

            # PARAÍBA
            "joão pessoa": "PB", "joao pessoa": "PB",
            "campina grande": "PB",

            # RIO GRANDE DO NORTE
            "natal": "RN",
            "mossoró": "RN", "mossoro": "RN",

            # ALAGOAS
            "maceió": "AL", "maceio": "AL",
            "arapiraca": "AL",

            # SERGIPE
            "aracaju": "SE",

            # ESPÍRITO SANTO
            "vitória": "ES", "vitoria": "ES",
            "vila velha": "ES",
            "serra": "ES",
            "cariacica": "ES",

            # DISTRITO FEDERAL
            "brasília": "DF", "brasilia": "DF"
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
        texto = texto.replace("&nbsp;", " ").replace("&amp;", "&")
        texto = texto.replace("&#39;", "'").replace("&quot;", '"')
        return texto.strip()

    def normalizar(self, texto):
        texto = texto.lower()
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    def normalizar_titulo(self, titulo):
        titulo = self.normalizar(titulo)
        titulo = re.sub(r" - .*?$", "", titulo)
        titulo = re.sub(r" \| .*?$", "", titulo)
        return titulo.strip()

    def gerar_id(self, titulo, link):
        base = self.normalizar_titulo(titulo)
        base = re.sub(r"[^a-z0-9áéíóúãõâêôç]", "", base)
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
            "horóscopo", "horoscopo", "signo", "zodíaco", "zodiaco", "astrologia",
            "tarô", "taro", "previsão do dia", "previsao do dia",
            "escorpião do signo", "signo de escorpião",
            "cinema", "filme", "série", "serie", "streaming", "netflix", "marvel",
            "dc comics", "personagem", "trailer", "bilheteria", "ator", "atriz",
            "música", "musica", "show", "celebridade", "famosos", "bbb"
        ]

        if any(b in texto for b in bloqueios):
            return False

        tem_escorpiao = any(t in texto for t in [
            "escorpião", "escorpiões", "escorpiao", "escorpioes",
            "escorpionismo", "escorpiônico", "escorpionico"
        ])

        if not tem_escorpiao:
            return False

        contexto_valido = [
            "picada", "acidente", "morte", "morreu", "óbito", "obito",
            "soro", "antiescorpiônico", "antiescorpionico",
            "hospital", "atendimento", "criança", "crianca", "bebê", "bebe",
            "infestação", "infestacao", "aparecimento", "aumento",
            "prefeitura", "vigilância", "vigilancia", "saúde", "saude",
            "alerta", "prevenção", "prevencao", "controle", "captura",
            "mutirão", "mutirao", "orienta", "orientação", "orientacao",
            "animais peçonhentos", "animal peçonhento", "peçonhentos", "peconhentos"
        ]

        return any(c in texto for c in contexto_valido)

    def detectar_gravidade(self, texto):
        t = self.normalizar(texto)

        if any(p in t for p in ["morte", "morre", "morreu", "óbito", "obito", "uti", "estado grave", "fatal"]):
            return "grave"

        if any(p in t for p in ["picada", "acidente", "soro", "hospital", "atendimento", "infestação", "infestacao"]):
            return "moderada"

        return "leve"

    def detectar_estado(self, texto):
        t = self.normalizar(texto)

        # 1. Detectar cidades primeiro
        for cidade, uf in self.cidade_estado.items():
            if cidade in t:
                return uf

        # 2. Detectar estados por nome
        estados_extenso = {
            "acre": "AC",
            "alagoas": "AL",
            "amapá": "AP",
            "amapa": "AP",
            "amazonas": "AM",
            "bahia": "BA",
            "ceará": "CE",
            "ceara": "CE",
            "distrito federal": "DF",
            "espírito santo": "ES",
            "espirito santo": "ES",
            "goiás": "GO",
            "goias": "GO",
            "maranhão": "MA",
            "maranhao": "MA",
            "mato grosso": "MT",
            "mato grosso do sul": "MS",
            "minas gerais": "MG",
            "pará": "PA",
            "para": "PA",
            "paraíba": "PB",
            "paraiba": "PB",
            "paraná": "PR",
            "parana": "PR",
            "pernambuco": "PE",
            "piauí": "PI",
            "piaui": "PI",
            "rio de janeiro": "RJ",
            "rio grande do norte": "RN",
            "rio grande do sul": "RS",
            "rondônia": "RO",
            "rondonia": "RO",
            "roraima": "RR",
            "santa catarina": "SC",
            "são paulo": "SP",
            "sao paulo": "SP",
            "sergipe": "SE",
            "tocantins": "TO"
        }

        for nome, uf in estados_extenso.items():
            if nome in t:
                return uf

        # 3. Detectar UF solta
        for uf in self.estados.keys():
            uf_lower = uf.lower()

            padroes = [
                f" {uf_lower} ",
                f"/{uf_lower}",
                f"-{uf_lower}",
                f"({uf_lower})",
                f",{uf_lower}"
            ]

            for p in padroes:
                if p in t:
                    return uf

        # 4. Detectar portais regionais
        fontes_regionais = {
            "folha de londrina": "PR",
            "cbn londrina": "PR",
            "tarobá": "PR",
            "taroba": "PR",
            "gmc online": "PR",

            "thmais": "SP",
            "acidade on": "SP",
            "sampi": "SP",

            "estado de minas": "MG",
            "o tempo": "MG",

            "bahia noticias": "BA",
            "correio da bahia": "BA",

            "diario do nordeste": "CE",

            "midiamax": "MS",
            "campo grande news": "MS",

            "folha vitoria": "ES"
        }

        for portal, uf in fontes_regionais.items():
            if portal in t:
                return uf

        return "Não identificado"

    def detectar_cidade(self, titulo, descricao, estado):
        texto = self.normalizar(f"{titulo} {descricao}")

        for cidade, uf in self.cidade_estado.items():
            if estado != "Nacional" and uf != estado:
                continue

            if f" {cidade} " in f" {texto} " or cidade in texto:
                return self.formatar_cidade(cidade)

        padroes = [
            r"em ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"no município de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})",
            r"na cidade de ([A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+(?: [A-ZÁÉÍÓÚÃÕÂÊÔÇ][a-záéíóúãõâêôç]+){0,3})"
        ]

        bruto = f"{titulo} {descricao}"

        bloqueios = [
            "Brasil", "Google", "News", "Escorpião", "Escorpiões",
            "Hospital", "Prefeitura", "Secretaria", "Estado",
            "Ministério", "Vigilância", "Saúde", "Criança",
            "Animal", "Animais", "Homem", "Mulher"
        ]

        for padrao in padroes:
            m = re.search(padrao, bruto)
            if m:
                cidade = m.group(1).strip()
                if cidade not in bloqueios and len(cidade) > 2:
                    return cidade

        return "Não identificada"

    def formatar_cidade(self, cidade):
        excecoes = {
            "sao paulo": "São Paulo",
            "sao jose do rio preto": "São José do Rio Preto",
            "ribeirao preto": "Ribeirão Preto",
            "marilia": "Marília",
            "aracatuba": "Araçatuba",
            "maringa": "Maringá",
            "foz do iguacu": "Foz do Iguaçu",
            "paranavai": "Paranavaí",
            "campo mourao": "Campo Mourão",
            "uberlandia": "Uberlândia",
            "divinopolis": "Divinópolis",
            "niteroi": "Niterói",
            "nova iguacu": "Nova Iguaçu",
            "vitoria da conquista": "Vitória da Conquista",
            "goiania": "Goiânia",
            "anapolis": "Anápolis",
            "cuiaba": "Cuiabá",
            "rondonopolis": "Rondonópolis",
            "varzea grande": "Várzea Grande",
            "tres lagoas": "Três Lagoas",
            "florianopolis": "Florianópolis",
            "chapeco": "Chapecó",
            "criciuma": "Criciúma",
            "belem": "Belém",
            "maraba": "Marabá",
            "joao pessoa": "João Pessoa",
            "mossoro": "Mossoró",
            "maceio": "Maceió",
            "sao luis": "São Luís",
            "macapa": "Macapá",
            "brasilia": "Brasília",
            "vitoria": "Vitória"
        }

        if cidade in excecoes:
            return excecoes[cidade]

        return " ".join(p.capitalize() for p in cidade.split())

    def buscar_google_rss(self):
        print("🔍 Buscando Google News RSS - modelo intermediário...")

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
        print("🦂 MONITOR DE ESCORPIÕES - BUSCA INTERMEDIÁRIA")
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("=" * 70)

        self.buscar_google_rss()
        self.salvar_noticias()

        print("=" * 70)
        print("✅ FINALIZADO")
        print("=" * 70)

if __name__ == "__main__":
    BuscadorNoticias().executar()
