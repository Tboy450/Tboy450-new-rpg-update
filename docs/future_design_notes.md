# Future Design Notes

Small design ideas that are not active gameplay yet.

## Inn Mini-Game

The Warm Hearth Inn is a good future home for a short optional mini-game.

Beginner implementation idea:

- Keep the normal rest service simple: OK/SPACE restores HP/MP and gives the
  once-per-level rest bonus.
- Add the mini-game as a separate Inn action later so resting never blocks basic
  healing.
- Good first versions would be a simple timing game, tavern dice/cards, or a
  memory/order game tied to serving guests.
- Rewards should stay modest: bonus EXP, one potion, temporary town reputation,
  or a cosmetic/trophy item.
- Code should live near `systems/town_services.py` or in a new
  `systems/inn_minigame.py` module, not directly inside the largest parts of
  `main.py`.
