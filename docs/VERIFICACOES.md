# Catálogo de verificações

## Estudos preliminares

| Arquivo | Disciplina declarada | Código | Perguntas declaradas |
|---|---|---:|---:|
| `estudo_geologico.py` | Estudo Geológico | EGEO | 3 |
| `estudo_geotecnico.py` | Estudo Geotécnico | EGTC | 5 |
| `estudo_hidrologico.py` | Estudo Hidrológico | EHID | 7 |
| `estudo_tracado.py` | Estudo de Traçado | ETRC | 6 |
| `estudo_trafego.py` | Estudo de Tráfego | ETRF | 4 |

O catálogo possui cinco verificações de estudos. A avaliação de ART não aparece como módulo selecionável porque é acrescentada automaticamente a toda disciplina.

## Projetos básico e executivo

| Arquivo | Disciplina | Código | Perguntas declaradas |
|---|---|---:|---:|
| `projeto_contencao.py` | Contenção | PCTC | 6 |
| `projeto_geometrico.py` | Geometria | PGMT | 4 |
| `projeto_obras_complementares.py` | Obras Complementares | POBC | 3 |
| `projeto_pavimentacao.py` | Pavimentação | PPAV | 4 |
| `projeto_sinalizacao.py` | Sinalização | PSIN | 4 |
| `projeto_terraplanagem.py` | Terraplanagem | PTER | 6 |

As duas fases usam exatamente os mesmos arquivos e perguntas; a fase é apenas registrada como metadado.

## Pergunta adicional de ART

Depois das perguntas declaradas, o executor acrescenta:

```text
O documento apresenta Anotação de Responsabilidade Técnica (ART)?
```

Páginas candidatas são obtidas pelo mesmo recuperador do documento. Cada página candidata é renderizada e classificada por um modelo visual. O item participa do percentual geral do RAC.

## Códigos e compatibilidade

O código faz parte do nome do arquivo e da descoberta da próxima versão. Alterar um código inicia outra sequência de versionamento. Códigos devem ser unicos por disciplina e estaveis ao longo das versões.

## Descoberta pela interface

A interface lista todo arquivo `*.py` na pasta da fase, em ordem alfabética. Não existe manifesto, validação prévia ou filtro para arquivos auxiliares. Todo arquivo listado deve expor `principal()` e ser seguro para importacao dinâmica.
