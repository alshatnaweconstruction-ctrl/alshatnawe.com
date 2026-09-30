# Pool Service Images Setup

## Folder Structure

All images go into `/images/` at the project root:

```
alshatnawe.com/
└── images/
    ├── maintenance/
    │   ├── weekly_1.jpg  weekly_2.jpg  weekly_3.jpg  weekly_4.jpg  weekly_5.jpg
    │   ├── comp_1.jpg    comp_2.jpg    comp_3.jpg    comp_4.jpg    comp_5.jpg
    │   └── daily_1.jpg   daily_2.jpg   daily_3.jpg   daily_4.jpg   daily_5.jpg
    ├── construction/
    │   ├── small_1.jpg  ... small_5.jpg
    │   ├── medium_1.jpg ... medium_5.jpg
    │   └── large_1.jpg  ... large_5.jpg
    ├── pool_types/
    │   ├── overflow_1.jpg ... overflow_5.jpg
    │   ├── skimmer_1.jpg  ... skimmer_5.jpg
    │   └── infinity_1.jpg ... infinity_5.jpg
    ├── linings/
    │   ├── liner_1.jpg   ... liner_5.jpg
    │   ├── mosaic_1.jpg  ... mosaic_5.jpg
    │   └── ceramic_1.jpg ... ceramic_5.jpg
    ├── commercial/
    │   ├── pool_1.jpg    ... pool_5.jpg
    │   ├── spa_1.jpg     ... spa_5.jpg
    │   ├── fountain_1.jpg... fountain_5.jpg
    │   └── hotel_1.jpg   ... hotel_5.jpg
    ├── specialty/
    │   ├── swim_spa_1.jpg ... swim_spa_5.jpg
    │   ├── waterpark_1.jpg... waterpark_5.jpg
    │   ├── heating_1.jpg  ... heating_5.jpg
    │   ├── rock_1.jpg     ... rock_5.jpg
    │   └── bar_1.jpg      ... bar_5.jpg
    └── renovation/
        ├── basic_1.jpg    ... basic_5.jpg
        └── complete_1.jpg ... complete_5.jpg
```

## How to Download Images

### Option 1: Run `download_images.py` from your machine

```bash
pip install requests
python3 BazarakiSystem/download_images.py
```

The script downloads 5 matching images per service from Unsplash (free, no restrictions).

### Option 2: Pinterest Manual Download

Search Pinterest for each category and save 5 images per folder:

| Folder | Pinterest Search |
|--------|-----------------|
| maintenance/weekly | "pool cleaning service technician" |
| maintenance/comp | "pool equipment pump filter service" |
| maintenance/daily | "hotel resort pool daily service" |
| construction/small | "small backyard pool construction" |
| construction/medium | "swimming pool construction site" |
| construction/large | "large luxury villa pool" |
| pool_types/overflow | "overflow wet edge pool" |
| pool_types/skimmer | "residential skimmer pool blue" |
| pool_types/infinity | "infinity edge pool sea view" |
| linings/liner | "vinyl liner pool installation" |
| linings/mosaic | "glass mosaic pool tile" |
| linings/ceramic | "ceramic tile pool finish" |
| commercial/pool | "commercial resort hotel pool" |
| commercial/spa | "commercial spa jacuzzi jets" |
| commercial/fountain | "decorative water fountain feature" |
| commercial/hotel | "hotel pool service maintenance" |
| specialty/swim_spa | "swim spa backyard hydrotherapy" |
| specialty/waterpark | "waterpark slides aqua park" |
| specialty/heating | "pool heat pump heating system" |
| specialty/rock | "natural rock pool waterfall feature" |
| specialty/bar | "swim up pool bar stools" |
| renovation/basic | "pool renovation repair resurfacing" |
| renovation/complete | "complete pool renovation makeover" |

## Rules

- ❌ Do NOT use photos from other Bazaraki ads
- ✅ Use Pinterest, Unsplash, Pexels, or your own photos
- ✅ Each photo must match the service it represents
- ✅ Minimum 5 photos per service type
- ✅ JPG format, at least 800×600 pixels
