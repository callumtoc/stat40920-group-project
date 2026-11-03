# STAT40920 Group Project: Equity Portfolio Advice for a DB Pension Scheme

Group project for **STAT40920 Actuarial and Financial Maths I** (UCD), worth 20% of the module grade.

## The project

Our group has been hired to advise the trustees of a **US defined benefit (DB) pension scheme** on the **equity part** of their investment portfolio. We do not model the scheme's liabilities or its other investments, but we do consider how a DB scheme's objectives affect the trustees' attitude to investment risk.

We must recommend **three portfolios**:

| Portfolio | Purpose |
|---|---|
| Low risk | For trustees who put stability first |
| Medium risk | A balance between risk and return |
| High risk | For trustees seeking higher expected return |

Each portfolio:

- is a percentage allocation across **our ten permitted industry sectors** only (no cash, other asset classes or other sectors)
- comes with a recommended **rebalancing frequency** (monthly, quarterly or annually)
- is compared over a **five-year investment horizon**, covering both potential rewards and the risk of adverse outcomes

## The report

- Written for trustees who are **financially literate but not specialists** in portfolio mathematics.
- Explains our process, assumptions, results and the limitations of our modelling.
- May cover risk and return measures, diversification, historical (backtest) performance and the outlook for our sectors.
- **8–10 A4 pages** recommended. Pages after 11, including the cover, are not marked.
- Must include an **attestation statement** (each member's contribution) and an **AI-use statement**.
- Submitted as a **PDF**.

**Deadline:** 14:00, Friday 27 November 2026. An extension to 14:00, Monday 30 November 2026 is available by submitting by then.

## Our ten sectors

Chosen from Kenneth French's 49 industries using the method in the brief. See [`sector-allocation.md`](sector-allocation.md) for the full working.

| Code | Short name | Industry |
|---:|---|---|
| 10 | Clths | Apparel |
| 11 | Hlth | Healthcare |
| 12 | MedEq | Medical Equipment |
| 13 | Drugs | Pharmaceutical Products |
| 21 | Mach | Machinery |
| 22 | ElcEq | Electrical Equipment |
| 23 | Autos | Automobiles and Trucks |
| 39 | Paper | Business Supplies |
| 40 | Boxes | Shipping Containers |
| 41 | Trans | Transportation |

## Data source

All data comes from the [Kenneth R. French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).

| File | Description |
|---|---|
| [`data/raw/Siccodes49.txt`](data/raw/Siccodes49.txt) | Definitions of the 49 industries (SIC codes in each) |

## Repository structure

```
stat40920-group-project/
├── README.md               # this file
├── sector-allocation.md    # how our ten sectors were chosen
└── data/
    └── raw/                # downloaded source files, unaltered
        └── Siccodes49.txt
```

More folders (e.g. `code/`, `report/`) will be added as the project develops.

## Conventions

- **Downloaded files** stay in their original format and keep their original names, unaltered, in `data/raw/`.
- **Files we create** use markdown (`.md`) for documentation, and **dash-case** file names (e.g. `sector-allocation.md`).

## Group

| Member | Role |
|---|---|
| C | |
| N | |
| J | |

## Use of generative AI

AI use is permitted under **Level 3 (AI Collaboration)** of UCD's AI Assessment Scale. We keep records of AI-assisted work so that our methods and results can be explained and reproduced. The report will include a statement of the AI tools used and how they contributed.
