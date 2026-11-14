# Actuarial and Financial Maths I (STAT 40920) — Group Project

## 1. Purpose of the Project

- **Group size:** 3–4 students.
- **Client:** The trustees of a **US defined benefit (DB) pension scheme**.
- **Scope:** Advise on the asset strategy for the **equity component only** of the scheme's investment portfolio.
  - You are **not** required to model the scheme's liabilities or its other investments.
  - You **should** consider how the objectives of a DB pension scheme might influence the trustees' attitude towards investment risk.

### 1.1 What the Trustees Want

- A report recommending a **short-list of three portfolios**:
  1. Low risk
  2. Medium risk
  3. High risk
- A comparison of possible investment outcomes over a **prospective five-year investment horizon**, covering:
  - Potential rewards
  - Risks of adverse outcomes
- An explanation of:
  - The **process** by which you arrived at the portfolios
  - The **assumptions** you made
  - The **limitations** of any modelling work
- If you need more information on the trustees' objectives, you may **invent some clarifying correspondence**.

### 1.2 Audience

- The trustees will later choose between the three portfolios according to how much risk they are prepared to take.
- Write for trustees who are **financially literate but not specialists in portfolio mathematics**.
- You may use mathematical models and numerical optimisation, but explain assumptions, results and recommendations in language the trustees can understand.

---

## 2. Your Report

### 2.1 Content

The report should include your recommendations and the basis for your conclusions. This might include:

- Risks and returns measured in appropriate ways
- Consideration of diversification
- Analysis of how the strategy would have performed in the past
- Prospective outlook for the chosen sectors

All of these should be considered **within the context of client objectives**.

### 2.2 Required Statements

- [ ] **Attestation statement:** briefly describe the contribution each group member made to the project.
- [ ] **AI use statement:** see [Section 3](#3-use-of-generative-artificial-intelligence).

### 2.3 Format and Length

| Item | Requirement |
|---|---|
| File format | PDF |
| Recommended length | 8–10 A4 pages, including charts and appendices |
| Hard limit | 11 pages, **including any front cover**. Pages 12 onwards (as counted by Acrobat Reader) will be disregarded |
| Submissions | One uploaded report per group is acceptable |

> Put all material you want marked within the first 11 pages.

### 2.4 Deadlines

| Deadline | Date and time |
|---|---|
| Official due date | **14:00, Friday 27 November** |
| Extension (no request needed) | **14:00, Monday 30 November**. Any group may claim it simply by submitting by that time |

---

## 3. Use of Generative Artificial Intelligence

Generative AI is permitted under **Level 3 — AI Collaboration** of UCD's AI Assessment Scale, as described in the *UCD Faculty Guidelines for the Use of AI in Teaching and Learning* (Appendix 2).

### 3.1 Permitted Uses

You may use generative AI to help with:

- Initial research
- Brainstorming
- Programming
- Mathematical calculations
- Drafting
- Feedback and refinement of your report

### 3.2 Responsibilities

- You must **critically evaluate** and, where necessary, **modify** AI-generated outputs, demonstrating your own understanding.
- Your group remains responsible for:
  - The accuracy of all calculations
  - The validity of the methods used
  - The interpretation of results
  - The recommendations made to the trustees
- You must be able to **explain and justify** your analysis.
- Under UCD's Academic Integrity Policy (Section 4.3), you must not present AI-generated content as your own work without appropriate attribution.

### 3.3 Requirements

- [ ] Include a **brief statement** identifying any AI tools used and explaining how they contributed. If you did not use generative AI, state this.
- [ ] **Keep records** of AI-generated outputs and your underlying calculations, as you may be asked to explain or demonstrate how your results were obtained.

Further guidance: UCD Library, *Citing AI*.

---

## 4. Your Choice of Investments

### 4.1 Portfolio Constraints

- Express each portfolio as a **percentage allocation across ten industry sectors**. Each group has a different list of ten sectors.
  - *Example of a feasible allocation:* 50% in one specified sector, 10% in each of five more specified sectors, and 0% in the remaining four.
- State the **rebalancing frequency** (e.g. monthly, quarterly or annually) at which the portfolio is reset to its original proportions.
- Portfolios must **not** include:
  - Cash
  - Other asset classes
  - Equity sectors outside your group's permitted ten

### 4.2 Selecting Your Ten Sectors

The ten sectors are chosen from the **49 industry portfolios** in Kenneth French's data library:

1. **Code the sectors** from 1 to 49 in the order listed in the data set:
   `1 = Agriculture`, `2 = Food Products`, … , `48 = Financial Trading`, `49 = Other`.
2. **Compute each member's personal number** (between 0 and 50):
   take the last three digits of your student number and divide by 20.
3. **Compute the distance for every sector:**
   the absolute difference between the industry code and the **closest** member's personal number.
4. **Select the ten sectors with the smallest distances.**
   If there is a tie, you may choose arbitrarily among the tied sectors.

**Data library:** <http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html>
