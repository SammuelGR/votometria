# Google Trends — Metodologia

Este documento descreve a fonte de dados **Google Trends** usada no projeto, suas
limitações metodológicas e as decisões técnicas adotadas na coleta em lotes com
**termo-âncora** para comparar eleições de **2018**, **2022** e a **eleição atual**.

## O que é o Google Trends

O Google Trends é um serviço público do Google que mede o **interesse de busca**
relativo por um termo ao longo do tempo e por região geográfica. Ele não expõe
volumes absolutos de pesquisa: os dados são amostrados e normalizados antes de
serem disponibilizados.

A coleta é feita pela biblioteca [`pytrends`](https://github.com/GeneralMills/pytrends),
um cliente não-oficial que consome os mesmos endpoints internos do Google Trends.

## O índice de 0 a 100

Os valores retornados são um **índice normalizado de 0 a 100**, e não contagens de
buscas:

- **100** representa o ponto de **maior interesse** dentro da janela e do conjunto
  de termos consultados.
- **0** indica interesse insuficiente para registro.
- Os demais pontos são proporcionais ao pico.

### Por que não é volume absoluto de buscas

O Google divide o número de buscas de cada termo pelo total de buscas da região e
do período, e reescala o maior valor para 100. O índice é, portanto, **relativo** —
não uma quantidade. Não é possível somar ou comparar índices entre coletas feitas em
janelas ou conjuntos de termos diferentes como se fossem volumes.

## Comparações só são válidas dentro da mesma consulta

A normalização (o "100") é calculada **dentro de uma única requisição**. Dois termos
só são diretamente comparáveis quando coletados **na mesma chamada** `build_payload`.
Se cada candidato fosse coletado isoladamente, cada série teria seu próprio pico em
100 e os números **não seriam comparáveis** entre candidatos.

## Mais de 5 candidatos: coleta em lotes com termo-âncora

O Google Trends aceita no máximo **~5 termos por consulta**. Como agora acompanhamos
**mais de 5 candidatos por ano**, **não** podemos simplesmente dividir os candidatos
em grupos independentes e comparar os valores diretamente — cada grupo seria
normalizado em uma escala própria de 0 a 100.

A solução é a **coleta em lotes com termo-âncora**:

1. Para cada ano eleitoral definimos uma lista de candidatos e um **termo-âncora**.
2. Os candidatos são divididos em lotes de **1 âncora + até 4 candidatos** (≤5 termos).
3. O **termo-âncora aparece em todos os lotes** daquele ano.

Exemplo (2022, âncora "Lula"):

```
Lote 1: Lula, Jair Bolsonaro, Simone Tebet, Ciro Gomes, Felipe d'Avila
Lote 2: Lula, Soraya Thronicke, Padre Kelmon, Léo Péricles, Sofia Manzano
Lote 3: Lula, Vera Lúcia, Eymael
```

## Reescala por termo-âncora (interest_scaled)

Como cada lote é normalizado separadamente, o transformer gera **dois** valores:

- **`interest_raw`** — valor original do Google Trends **dentro daquele lote**.
- **`interest_scaled`** — valor **reescalado** usando o termo-âncora.

Para cada data:

```
fator_de_escala = valor_do_ancora_no_lote_base / valor_do_ancora_no_lote_atual
interest_scaled = interest_raw * fator_de_escala
```

Regras adotadas:

- O **primeiro lote** de cada ano (`batch_01`) é o **lote base**; suas linhas mantêm
  `interest_scaled = interest_raw` (fator 1).
- Os demais lotes são ajustados pelo termo-âncora à escala do lote base.
- **Divisão por zero**: se o valor do âncora for **0 ou ausente** em uma data no lote
  atual, o ponto **não pode ser reescalado** e `interest_scaled` fica **nulo (vazio)**.
  Essa é uma decisão intencional para não inventar valores; o `interest_raw` é sempre
  preservado para auditoria.
- O termo-âncora é mantido **apenas a partir do lote base** no arquivo consolidado,
  evitando repetição excessiva.

> ⚠️ A reescala é uma **aproximação metodológica**. Ela melhora a comparabilidade
> entre candidatos do mesmo ano, mas depende da estabilidade do termo-âncora e da
> amostragem do Google. Use `interest_scaled` com cautela.

## Por que a coleta não é incremental

Não fazemos extração incremental. Como o índice é renormalizado em função da janela
consultada, concatenar coletas de janelas diferentes produziria séries
inconsistentes. Por isso **cada execução refaz a janela completa** de cada ano
(`timeframe` por grupo eleitoral). O arquivo canônico é sobrescrito e uma cópia
timestampada é guardada para rastreabilidade.

## Recomendações de uso (dashboard e análise)

- Use **`interest_raw`** para análises **dentro do mesmo lote**.
- Use **`interest_scaled`** para comparação **aproximada** entre todos os candidatos
  **do mesmo ano**.
- **Nunca** compare `interest_raw` diretamente entre lotes diferentes.
- **Não** compare `interest_scaled` de **anos diferentes** sem deixar explícito que
  são janelas temporais independentes (escalas não equivalentes entre anos).
- Para análises mais rigorosas, prefira comparações dentro do mesmo ano e da mesma
  janela temporal.

## Riscos e limitações

- **Rate limit**: o Google pode limitar requisições frequentes (HTTP 429). O extrator
  faz *retry* com *backoff*.
- **Instabilidade do `pytrends`**: cliente não-oficial; pode quebrar quando o Google
  altera endpoints internos. Com muitos lotes, o risco de rate limit aumenta.
- **Mudanças do Google**: amostragem e normalização podem mudar sem aviso.
- **Aproximação da reescala**: ver seção acima.

> Os números coletados são **estimativas de interesse relativo**, adequados para
> análise de tendência e comparação entre candidatos na mesma janela — não para
> afirmar volumes de busca ou intenção de voto.
