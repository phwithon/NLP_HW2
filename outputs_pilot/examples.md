# Randomly sampled examples

Model `Qwen/Qwen2.5-3B-Instruct`, prompt `instructed`, seed 2026. 4 rows drawn uniformly at random from the 35 errors and 4 from the 185 correct predictions (no manual selection).

## item 1 / metric_far -> correct

```
Financial note on Tordris Systems:
Tordris Systems had 13,344 employees in fiscal year 2021. Tordris Systems reported revenue of $416 million in fiscal year 2021. Tordris Systems reported cash and cash equivalents of $622 million in fiscal year 2021. Tordris Systems reported long-term debt of $5,264 million in fiscal year 2021.

Q: According to the note, what was the net income of Tordris Systems in fiscal year 2021?
A. $461 million
B. $416 million
C. The value cannot be determined from the note
D. $375 million
```

gold C, predicted C (unk); p = {"A": 0.0, "B": 0.0, "C": 1.0, "D": 0.0}

## item 5 / scope_far -> WRONG

```
Financial note on Ossmont Group:
Ossmont Group reported long-term debt of $1,179 million in fiscal year 2024. Ossmont Group's Consumer Products segment reported net income of $405 million in fiscal year 2024. Ossmont Group reported capital expenditure of $220 million in fiscal year 2024. Ossmont Group reported total assets of $5,478 million in fiscal year 2024.

Q: How much net income did Ossmont Group report for fiscal year 2024?
A. The value cannot be determined from the note
B. $405 million
C. $465 million
D. $355 million
```

gold A, predicted B (v); p = {"A": 0.0, "B": 1.0, "C": 0.0, "D": 0.0}

## item 6 / scope_near -> WRONG

```
Financial note on Toreth Industries:
- Toreth Industries: number of employees, fiscal year 2024: 38,152
- Toreth Industries: total assets, fiscal year 2024: $9,428 million
- Toreth Industries: fourth-quarter net income, fiscal year 2024: $699 million
- Toreth Industries: capital expenditure, fiscal year 2024: $447 million

Q: According to the note, what was the net income of Toreth Industries in fiscal year 2024?
A. $749 million
B. $699 million
C. $637 million
D. The value cannot be determined from the note
```

gold D, predicted B (v); p = {"A": 0.0, "B": 1.0, "C": 0.0, "D": 0.0}

## item 7 / IRR -> correct

```
Financial note on Istdris Group:
Istdris Group had 3,171 employees in fiscal year 2024. Istdris Group reported total assets of $4,152 million in fiscal year 2024. Istdris Group reported capital expenditure of $252 million in fiscal year 2024. Istdris Group had 173 million shares outstanding in fiscal year 2024.

Q: According to the note, what was the net income of Istdris Group in fiscal year 2024?
A. $192 million
B. $161 million
C. $173 million
D. The value cannot be determined from the note
```

gold D, predicted D (unk); p = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 1.0}

## item 8 / scope_near -> WRONG

```
Financial note on Halack Holdings:
- Halack Holdings: fourth-quarter net income, fiscal year 2020: $267 million
- Halack Holdings: cash and cash equivalents, fiscal year 2020: $861 million
- Halack Holdings: long-term debt, fiscal year 2020: $4,729 million
- Halack Holdings: number of employees, fiscal year 2020: 3,013

Q: According to the note, what was the net income of Halack Holdings in fiscal year 2020?
A. $267 million
B. The value cannot be determined from the note
C. $291 million
D. $249 million
```

gold B, predicted A (v); p = {"A": 1.0, "B": 0.0, "C": 0.0, "D": 0.0}

## item 13 / metric_near -> correct

```
Financial note on Pelholt Systems:
Pelholt Systems had 10,069 employees in fiscal year 2025. Pelholt Systems reported operating income of $482 million in fiscal year 2025. Pelholt Systems reported long-term debt of $4,856 million in fiscal year 2025. Pelholt Systems reported cash and cash equivalents of $821 million in fiscal year 2025.

Q: What was Pelholt Systems's net income in fiscal year 2025?
A. $540 million
B. The value cannot be determined from the note
C. $414 million
D. $482 million
```

gold B, predicted B (unk); p = {"A": 0.0, "B": 1.0, "C": 0.0, "D": 0.0}

## item 14 / scope_far -> correct

```
Financial note on Braeth Group:
- Braeth Group: total assets, fiscal year 2022: $6,134 million
- Braeth Group: number of employees, fiscal year 2022: 19,648
- Braeth Group's Consumer Products segment: net income, fiscal year 2022: $818 million
- Braeth Group: long-term debt, fiscal year 2022: $1,300 million

Q: How much net income did Braeth Group report for fiscal year 2022?
A. $731 million
B. $818 million
C. $908 million
D. The value cannot be determined from the note
```

gold D, predicted D (unk); p = {"A": 0.0, "B": 0.182, "C": 0.0, "D": 0.818}

## item 17 / scope_far -> WRONG

```
Financial note on Morven Industries:
Morven Industries had 5,713 employees in fiscal year 2023. Morven Industries' Digital Services segment reported net income of $840 million in fiscal year 2023. Morven Industries reported cash and cash equivalents of $544 million in fiscal year 2023. Morven Industries reported long-term debt of $2,675 million in fiscal year 2023.

Q: What was Morven Industries's net income in fiscal year 2023?
A. $788 million
B. The value cannot be determined from the note
C. $840 million
D. $915 million
```

gold B, predicted C (v); p = {"A": 0.0, "B": 0.0, "C": 1.0, "D": 0.0}
