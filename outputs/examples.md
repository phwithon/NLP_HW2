# Randomly sampled examples

Model `Qwen/Qwen2.5-3B-Instruct`, prompt `instructed`, seed 2026. 4 rows drawn uniformly at random from the 197 errors and 4 from the 1123 correct predictions (no manual selection).

## item 6 / entity_near -> correct

```
Financial note on Galuna Systems:
- Galuna Systems: total assets, fiscal year 2021: $5,623 million
- Galuna Systems: long-term debt, fiscal year 2021: $1,608 million
- Ossoria Retail (a wholly owned subsidiary of Galuna Systems): net income, fiscal year 2021: $732 million
- Galuna Systems: cash and cash equivalents, fiscal year 2021: $2,279 million

Q: What was Galuna Systems's net income in fiscal year 2021?
A. $809 million
B. $732 million
C. $630 million
D. The value cannot be determined from the note
```

gold D, predicted D (unk); p = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 1.0}

## item 8 / scope_far -> WRONG

```
Financial note on Galtine Systems:
- Galtine Systems' Industrial Solutions segment: net income, fiscal year 2025: $297 million
- Galtine Systems: total assets, fiscal year 2025: $6,088 million
- Galtine Systems: long-term debt, fiscal year 2025: $4,463 million
- Galtine Systems: cash and cash equivalents, fiscal year 2025: $728 million

Q: According to the note, what was the net income of Galtine Systems in fiscal year 2025?
A. The value cannot be determined from the note
B. $297 million
C. $329 million
D. $278 million
```

gold A, predicted B (v); p = {"A": 0.0, "B": 1.0, "C": 0.0, "D": 0.0}

## item 18 / period_far -> correct

```
Financial note on Istora Systems:
- Istora Systems: long-term debt, fiscal year 2022: $5,659 million
- Istora Systems: capital expenditure, fiscal year 2022: $49 million
- Istora Systems: net income, fiscal year 2017: $422 million
- Istora Systems: cash and cash equivalents, fiscal year 2022: $2,166 million

Q: According to the note, what was the net income of Istora Systems in fiscal year 2022?
A. $461 million
B. $422 million
C. $376 million
D. The value cannot be determined from the note
```

gold D, predicted D (unk); p = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 1.0}

## item 30 / IRR -> correct

```
Financial note on Kelack Holdings:
- Kelack Holdings: total assets, fiscal year 2020: $10,096 million
- Kelack Holdings: long-term debt, fiscal year 2020: $2,133 million
- Kelack Holdings: shares outstanding, fiscal year 2020: 287 million
- Kelack Holdings: cash and cash equivalents, fiscal year 2020: $899 million

Q: How much net income did Kelack Holdings report for fiscal year 2020?
A. $327 million
B. The value cannot be determined from the note
C. $287 million
D. $257 million
```

gold B, predicted B (unk); p = {"A": 0.0, "B": 1.0, "C": 0.0, "D": 0.0}

## item 36 / scope_far -> WRONG

```
Financial note on Torven Group:
- Torven Group's Digital Services segment: net income, fiscal year 2020: $940 million
- Torven Group: long-term debt, fiscal year 2020: $2,110 million
- Torven Group: total assets, fiscal year 2020: $3,837 million
- Torven Group: number of employees, fiscal year 2020: 18,714

Q: What was Torven Group's net income in fiscal year 2020?
A. $940 million
B. The value cannot be determined from the note
C. $1,080 million
D. $875 million
```

gold B, predicted A (v); p = {"A": 1.0, "B": 0.0, "C": 0.0, "D": 0.0}

## item 56 / scope_near -> WRONG

```
Financial note on Torack Industries:
- Torack Industries: fourth-quarter net income, fiscal year 2021: $856 million
- Torack Industries: total assets, fiscal year 2021: $7,394 million
- Torack Industries: cash and cash equivalents, fiscal year 2021: $2,060 million
- Torack Industries: number of employees, fiscal year 2021: 27,229

Q: How much net income did Torack Industries report for fiscal year 2021?
A. $956 million
B. $783 million
C. The value cannot be determined from the note
D. $856 million
```

gold C, predicted D (v); p = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 1.0}

## item 61 / scope_near -> WRONG

```
Financial note on Verana Partners:
Verana Partners reported long-term debt of $3,075 million in fiscal year 2023. Verana Partners reported fourth-quarter net income of $464 million in fiscal year 2023. Verana Partners had 28,954 employees in fiscal year 2023. Verana Partners reported cash and cash equivalents of $690 million in fiscal year 2023.

Q: What was Verana Partners's net income in fiscal year 2023?
A. $407 million
B. The value cannot be determined from the note
C. $464 million
D. $495 million
```

gold B, predicted C (v); p = {"A": 0.0, "B": 0.0, "C": 1.0, "D": 0.0}

## item 95 / period_near -> correct

```
Financial note on Kelery Systems:
Kelery Systems reported long-term debt of $2,411 million in fiscal year 2023. Kelery Systems reported cash and cash equivalents of $1,549 million in fiscal year 2023. Kelery Systems reported capital expenditure of $358 million in fiscal year 2023. Kelery Systems reported net income of $237 million in fiscal year 2022.

Q: How much net income did Kelery Systems report for fiscal year 2023?
A. $237 million
B. $254 million
C. The value cannot be determined from the note
D. $203 million
```

gold C, predicted C (unk); p = {"A": 0.0, "B": 0.0, "C": 1.0, "D": 0.0}
