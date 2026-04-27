# Comparativo Geral de Otimização de Consultas

## 1. Comparativo de Tempo de Execução

| Cenário | Tempo Pré-Otimização | Tempo Pós-Otimização | Diferença (%) |
| :------ | :------------------- | :------------------- | :------------ |
| 1       | 4,99 s               | 2,31 s               | -53,71%       |
| 2       | 89,930 ms            | 0,759 ms             | -99,16%       |
| 3       | N/A (Timeout > 15h)  | 1,85 s               | -100,00%\*    |
| 4       | 1,39 s               | 0,722 ms             | -99,95%       |
| 5       | 5,082 ms             | 1,233 ms             | -75,74%       |
| 6       | 902,407 ms           | 232,343 ms           | -74,25%       |

\* No Cenário 3, a melhoria é virtualmente de 100% dado que a consulta original não completava.

## 2. Comparativo de Custo Total Estimado

| Cenário | Custo Pré-Otimização | Custo Pós-Otimização | Diferença (%) |
| :------ | :------------------- | :------------------- | :------------ |
| 1       | 17.927.093,59        | 678.721,81           | -96,21%       |
| 2       | 4.066,40             | 1.858,73             | -54,29%       |
| 3       | N/A                  | 13.689.480,38        | -             |
| 4       | 98.726,63            | 9,90                 | -99,99%       |
| 5       | 239,20               | 133,75               | -44,09%       |
| 6       | 56.565,03            | 23.708,26            | -58,09%       |

## 3. Comparativo de Memória (Buffers)

| Cenário | Memória Pré-Otimização (Hit/Read) | Memória Pós-Otimização (Hit/Read) | Observação                              |
| :------ | :-------------------------------- | :-------------------------------- | :-------------------------------------- |
| 1       | 4 / 110.384                       | 2.479.540 / 224.689               | Aumento expressivo em Hits (cache)      |
| 2       | - / 3.536                         | 1 / 3                             | Redução drástica em leituras físicas    |
| 3       | X / X                             | 12.158 / 75.792                   | Execução viabilizada pós-otimização     |
| 4       | 76 / 84.184                       | 13 / 87                           | Redução massiva de I/O de disco         |
| 5       | - / 208                           | 204 / -                           | Transição de leitura física para cache  |
| 6       | 26.019 / 26.376                   | 188 / 26.889                      | Mudança no perfil de acesso com índices |
