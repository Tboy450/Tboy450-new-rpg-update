# Active Town Shop Scenery

These PNGs are active copies of selected future assets. They are used only by
the Mooncap Market shop test.

Beginner note:

- The source ideas still live in `assets/processed/future_assets/scenery/`.
- These copies live here because active code should point at active folders, not
  the future shelf.
- If this test works well, more buildings can get their own folders beside
  `town_shop/`.

## Files

- `shop_front.png`: outdoor shop facade drawn over the Python-drawn shop area.
- `potion_shelf.png`: indoor potion shelf for the shop's left-side shelving.
- `shop_counter.png`: indoor shop counter used for the service counter.
- `scroll_desk.png`: small indoor desk used as a shop order desk/detail prop.

## Active Data References

- Outdoor reference: `TOWN_BUILDINGS` shop record in `game_data/town.py`.
- Indoor references: `TOWN_INTERIORS["shop"]["props"]` in
  `game_data/interiors.py`.
