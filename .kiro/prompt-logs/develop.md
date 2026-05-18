# Prompt Logs: develop

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Kiro, temos que fazer estas etapas, verifica o que...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 16:23:45 (Brasília)

### Prompt original
```
Kiro, temos que fazer estas etapas, verifica o que foi feito e o que ainda falta fazer: 1. Corrigir testes quebrados — `test_scoring.py` e `test_endpoints.py`
2. Criar novos testes** — scoring por tipo, asset_classifier, data_validator
3. Análise do banco — verificar distribuição de scores e anomalias
4. Coleção Postman — para testes de integração com o frontend
```

---

## Prompt: vamos trazer os dados de todas as ações e Fiis par...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 16:29:58 (Brasília)

### Prompt original
```
vamos trazer os dados de todas as ações e Fiis para testar. Eu preciso olhar o banco de dados e fazer uma validação visual. Também quero analisar o resultado dos calculos, principalemtne de score. Então traga todos os dados para o banco e faça os calculos, por gentileza.
```

---

## Prompt: FII são fundos imobiliários, tudo que não é isso, ...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 17:28:38 (Brasília)

### Prompt original
```
FII são fundos imobiliários, tudo que não é isso, não é classificado como FII e deve ser removido do escopo do projeto. Voê ja rodou o scrip dos calculos para tentar povoar o banco e calcular os indicadores ?
```

---

## Prompt: Kiro, não é 11, É ii, letra I
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 17:38:18 (Brasília)

### Prompt original
```
Kiro, não é 11, É ii, letra I
```

---

## Prompt: VOCÊ ESTA BUSCANDO TIKERS QUE TERMINAN COM NUMERO ...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 17:38:57 (Brasília)

### Prompt original
```
VOCÊ ESTA BUSCANDO TIKERS QUE TERMINAN COM NUMERO 11 MAS A NOMENCLATURA CORRETA É FIIS com i
```

---

## Prompt: ok, continua
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 17:39:32 (Brasília)

### Prompt original
```
ok, continua
```

---

## Prompt: O quoteType é EQUITY para todos — yfinance não dis...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 17:42:19 (Brasília)

### Prompt original
```
O quoteType é EQUITY para todos — yfinance não distingue. Mas o sector é o discriminador: FIIs reais têm sector=Real Estate. Consultar o quoteType do yfinance — FIIs reais retornam "ETF" ou têm dados específicos de fundo.
```

---

## Prompt: kiro, atualiza a documentação oficial do projeto d...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 18:31:25 (Brasília)

### Prompt original
```
kiro, atualiza a documentação oficial do projeto dentro de steering e backend, com esses ajustes, vamos deixar o codigo bem clean somente com o que é necessário para trazer os dados da maneira correta e fazer os calculos para tentar preencher os valores financeiros e indicadores faltantes.
```

---

## Prompt: Kiro, você atualizou o banco de dados ?/ preciso v...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 18:41:52 (Brasília)

### Prompt original
```
Kiro, você atualizou o banco de dados, preciso ver como ficou ?
```

---

## Prompt: relatorio.md
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 18:45:12 (Brasília)

### Prompt original
```
eu quero que estes dados que você esta me mostrando no terminal virem um relatorio .md. Princilamente o relatorio  de cobertura de indicadores de ações e fiis.
```

---

## Prompt: ok Kiro, agora faça uma segunda conferência sobre ...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 18:54:28 (Brasília)

### Prompt original
```
ok Kiro, agora faça uma segunda conferência sobre os testes com o pytest e o postmam para conseguirmos fazer o frontend posteriormente. Aí a gente encerra por hoje.
```

---

## Prompt: vams continuar
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 19:15:33 (Brasília)

### Prompt original
```
vamos continuar
```

---

## Prompt: não, agora precisamos atualizar a documentção de c...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 19:17:22 (Brasília)

### Prompt original
```
não, agora precisamos atualizar a documentção de compliance deixando evidente que para os tikers com indicadores e valores financeiros nuls, estamos colocando um valor suposto para fazer o calculo do score, este metodo precisa ficar explicito na documentação, em steering.
```

---

## Prompt: Vamos fazer um commit na develop com todos os ajus...
- Responsável: Michele Oliveira
- Branch: develop
- Data/hora: 2026-05-17 19:20:27 (Brasília)

### Prompt original
```
Vamos fazer um commit na develop com todos os ajustes realizados e abrir um PR conforme convenções do projeto. Leia atentamente a instruções dentro de steering e .github para criar o commit e PR da maneira correta, por gentileza.
```

---

