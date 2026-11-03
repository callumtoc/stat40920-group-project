# Group Sector Allocation

The ten industry sectors our group may invest in, chosen with the method set out in the project brief.

## Method

1. Number the 49 industries 1–49 as defined in [`data/raw/Siccodes49.txt`](data/raw/Siccodes49.txt), downloaded unaltered from the Kenneth French data library.
2. Each member's **personal number** is the last three digits of their student number ÷ 20.
3. For each sector, the **distance** is |industry code − closest member's personal number|.
4. Our ten sectors are the ten with the smallest distances.

## Personal numbers

| Member | Last 3 digits | Personal number |
|---|---:|---:|
| C | 443 | 22.15 |
| N | 232 | 11.60 |
| J | 804 | 40.20 |

## Our ten sectors

| Rank | Code | Short name | Industry | Closest member | Distance |
|---:|---:|---|---|---|---:|
| 1 | 22 | ElcEq | Electrical Equipment | C | 0.15 |
| 2 | 40 | Boxes | Shipping Containers | J | 0.20 |
| 3 | 12 | MedEq | Medical Equipment | N | 0.40 |
| 4 | 11 | Hlth | Healthcare | N | 0.60 |
| 5 | 41 | Trans | Transportation | J | 0.80 |
| 6 | 23 | Autos | Automobiles and Trucks | C | 0.85 |
| 7 | 21 | Mach | Machinery | C | 1.15 |
| 8 | 39 | Paper | Business Supplies | J | 1.20 |
| 9 | 13 | Drugs | Pharmaceutical Products | N | 1.40 |
| 10 | 10 | Clths | Apparel | N | 1.60 |

The next closest were 42 Wholesale (1.80) and 24 Aircraft (1.85). Nothing ties at the cut-off, so no arbitrary choice was needed.

## Sectors by member

| Member | Sectors |
|---|---|
| C | 21 Machinery, 22 Electrical Equipment, 23 Automobiles and Trucks |
| N | 10 Apparel, 11 Healthcare, 12 Medical Equipment, 13 Pharmaceutical Products |
| J | 39 Business Supplies, 40 Shipping Containers, 41 Transportation |

## What each sector contains

Summarised from the SIC code definitions in [`data/raw/Siccodes49.txt`](data/raw/Siccodes49.txt).

| Code | Sector | Main activities included |
|---:|---|---|
| 10 | Apparel | Clothing, footwear, leather tanning, buttons and fasteners |
| 11 | Healthcare | Health services: hospitals, clinics, care providers (SIC 8000–8099) |
| 12 | Medical Equipment | Surgical, medical and dental instruments; X-ray and electromedical apparatus; ophthalmic goods |
| 13 | Pharmaceutical Products | Drugs, pharmaceutical preparations, biological products, diagnostic substances |
| 21 | Machinery | Engines and turbines; farm, construction and mining machinery; industrial machinery; air conditioning and refrigeration |
| 22 | Electrical Equipment | Power transmission equipment, electrical industrial apparatus, lighting and wiring, batteries |
| 23 | Automobiles and Trucks | Motor vehicles and parts, tyres, truck and bus bodies, trailers, motor homes |
| 39 | Business Supplies | Paper and allied products, office furniture, business forms, pens and pencils |
| 40 | Shipping Containers | Paperboard boxes, glass containers, metal cans, wood containers |
| 41 | Transportation | Railroads, trucking, airlines, shipping, pipelines, freight forwarding, buses |

## Data column names

Short names to select from the 49 Industry Portfolios file:

```
Clths, Hlth, MedEq, Drugs, Mach, ElcEq, Autos, Paper, Boxes, Trans
```
