# Tetris Mondrian

Jogo didático de blocos descendentes, inspirado nas composições geométricas de Piet Mondrian: cores primárias, planos claros e linhas pretas. Todos os elementos visuais são desenhados pelo código.

## Executar

Requer Python 3.10 ou superior e Pygame. No terminal, dentro desta pasta:

```sh
python -m pip install -r requirements.txt
python tetris_mondrian.py
```

No Windows, também é possível substituir `python` por `py`.

## Controles

| Tecla | Ação |
|---|---|
| Esquerda / direita | Mover |
| Cima ou X | Girar no sentido horário |
| Z | Girar no sentido anti-horário |
| Baixo | Acelerar a queda |
| Espaço | Soltar imediatamente |
| P | Pausar ou continuar |
| R | Reiniciar |
| Esc | Sair |

O jogo pausa ao perder o foco da janela. Pressione P para retomar.

## Regras e recursos

- Tabuleiro de 10 × 20 células e sete formatos de peças.
- Sorteio por sacos de sete: cada formato aparece uma vez por saco.
- Prévia das três próximas peças e contorno da posição de aterrissagem.
- Linhas completas desaparecem; as superiores descem.
- Uma, duas, três ou quatro linhas rendem 100, 300, 500 ou 800 pontos, multiplicados pelo nível anterior à eliminação.
- Queda acelerada rende um ponto por célula; queda imediata rende dois.
- A cada dez linhas o nível aumenta e a queda acelera.
- Há 0,45 segundo para ajustar uma peça apoiada. Até quinze movimentos ou rotações no chão podem renovar esse prazo.
- O jogo termina quando uma nova peça não cabe ou quando uma peça se fixa acima do tabuleiro.
- Rotação com ajustes simplificados nas bordas; não implementa integralmente o sistema SRS, T-spins, combos ou reserva de peça.

A lógica de regras independe do Pygame, facilitando sua explicação e seus testes. Não há recursos gráficos externos, áudio, rede ou arquivos de recorde.

Documentação técnica consultada: https://www.pygame.org/docs/
