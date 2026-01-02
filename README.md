# 📊 Resource Scheduling & Capacity Analysis for Live Production Projects

**Assignment Submission**

**Candidate Name:** Gokulramm S
**Time Spent:** ~4 hours
**Data:** 02/01/2026
**GitHub Repo:** https://github.com/Gokulramms/Vibra-Softech-LLP.git
**My Portfolio:** https://gokulramm.vercel.app
---

## 1. Executive Summary

This document presents a **logical, structured approach** to solving a **resource scheduling and capacity analysis problem** for a media production company handling **live broadcast projects with fixed schedules**.

The primary challenge is to **assign skilled employees to projects** while:

* Avoiding double-booking
* Controlling overtime costs
* Balancing employee workload
* Understanding whether the current workforce size is sufficient

The focus of this solution is **clarity of thinking**, **reasonable assumptions**, and **trade-off analysis**, rather than optimization or complex algorithms.

---

## 2. Problem Understanding & Modeling (Task 1)

### 2.1 Key Entities

#### Employees

Each employee can be represented with:

* `employee_id`
* `skills` (one primary skill)
* `daily_hours_worked`
* `regular_hours`
* `overtime_hours`
* `assigned_projects`

#### Projects

Each project is represented with:

* `project_id`
* `start_time`
* `end_time`
* `required_skills` (5 unique skills)
* `assigned_employees`

#### Time

* Time is modeled in **days and hours**
* Each day has a maximum of **8 regular hours per employee**
* Any additional hours are counted as **overtime**

---

### 2.2 Data Representation (Conceptual)

```
Employee {
  id
  skill
  availability[day][hour]
  regular_hours
  overtime_hours
}

Project {
  id
  start_time
  end_time
  required_skills[5]
}
```

This representation keeps the model **simple, readable, and extensible**.

---

## 3. Basic Scheduling Logic (Task 2)

### 3.1 Scheduling Strategy (Non-Optimal, Clear Logic)

For each project:

1. Identify the project time window
2. For each required skill:

   * Find employees with that skill
   * Check availability (no overlap)
   * Prefer employees with:

     * Fewer total hours
     * No overtime yet
3. Assign exactly **5 unique employees**
4. Update:

   * Regular hours (up to 8/day)
   * Overtime hours (beyond 8/day)

---

### 3.2 Simplified Pseudocode

```
for project in projects:
    for skill in project.required_skills:
        candidates = employees with skill
        available = filter non-overlapping candidates
        selected = candidate with lowest total hours
        assign selected to project
        update hours
```

This logic prioritizes **fairness and simplicity**, not optimization.

---

## 4. Capacity, Utilization & Cost Analysis (Task 3)

### 4.1 Utilization Metrics

#### Employee Utilization

```
utilization = (total hours worked) / (available working hours)
```

#### Overall Team Utilization

```
team_utilization = sum(all worked hours) / sum(all available hours)
```

---

### 4.2 Identifying Workforce Issues

#### Under-utilized Employees

* Utilization < 50%
* Few or no project assignments

#### Overworked Employees

* Frequent overtime
* High utilization (>90%)
* Repeated scheduling across days

---

### 4.3 Overtime vs Hiring Trade-off

| Option          | Pros            | Cons                |
| --------------- | --------------- | ------------------- |
| Overtime (1.3×) | Immediate       | Expensive long-term |
| Hiring          | Reduces burnout | Fixed cost increase |

**Decision Logic:**

* Short-term spikes → Overtime
* Consistent overtime → Hire additional staff

This model helps management **quantify when hiring becomes cheaper than overtime**.

---

## 5. Assumptions & Trade-offs (Task 4)

### Assumption 1: One Primary Skill per Employee

**Reason:** Simplifies matching logic
**Impact if Changed:** Multi-skilled employees improve flexibility but increase complexity

---

### Assumption 2: Fixed Project Times

**Reason:** Live events cannot move
**Impact if Changed:** Flexible projects would reduce overtime needs

---

### Assumption 3: Equal Base Cost for All Employees

**Reason:** Focus on structure, not payroll differences
**Impact if Changed:** High-cost specialists would influence assignment decisions

---

### Assumption 4: Daily Reset of Regular Hours

**Reason:** Matches standard labor practices
**Impact if Changed:** Weekly caps would smooth workload

---

### Assumption 5: All Projects Require Exactly 5 People

**Reason:** Matches problem statement
**Impact if Changed:** Variable team sizes require more dynamic allocation logic

---

## 6. Use of AI as a Tool (Task 5)

### How AI Was Used

* To structure the problem logically
* To validate assumptions
* To draft pseudocode and trade-off analysis

### Questions Asked to AI

* “How to model resource scheduling clearly?”
* “What are reasonable simplifying assumptions?”
* “How to explain overtime vs hiring trade-offs?”

### AI Suggestion Accepted

* Using **utilization metrics** to justify hiring decisions

### AI Suggestion Rejected / Modified

* Rejected complex optimization algorithms
  **Reason:** Assignment explicitly asked not to over-engineer

AI was used as a **thinking assistant**, not a solution generator.

---

## 7. Follow-up Questions to Client

1. Are employees strictly single-skilled or multi-skilled?
2. Are project schedules evenly distributed or seasonal?
3. Is overtime legally capped per week?
4. Are some skills rarer or more expensive?
5. Is future demand expected to grow?

Answers to these would significantly improve accuracy.


# 🔧 Technical Design & System Architecture (Added Section)

## 9. Technical Approach (High-Level, Practical)

The solution is designed as a **logic-first backend system**, where correctness, traceability, and explainability are prioritized over performance optimization.

The system can be implemented using a **modular backend architecture** (e.g., Python + Flask), but the design is **language-agnostic**.

### Core Technical Principles

* **Deterministic scheduling logic** (no black-box optimization)
* **Clear data models** for employees, projects, and assignments
* **Separation of concerns** between scheduling, analysis, and reporting
* **Extensible structure** for future AI/optimization layers

---

## 10. System Architecture Overview

### 10.1 Logical Architecture

```
Input Layer
(Project data, Employee data)
        |
        v
Scheduling Engine
(Assignment Logic)
        |
        v
Capacity & Cost Analyzer
(Utilization, Overtime, Cost)
        |
        v
Insights & Decision Layer
(Hiring vs Overtime, Bottlenecks)
```

This layered approach ensures that **each responsibility is isolated and explainable**.

---

## 11. Component-Level Architecture

### 11.1 Data Models

#### Employee Model

```
Employee {
  id
  skill
  daily_hours[date]
  total_regular_hours
  total_overtime_hours
  assigned_projects
}
```

#### Project Model

```
Project {
  id
  start_time
  end_time
  required_skills[5]
  assigned_employees
}
```

#### Assignment Record

```
Assignment {
  employee_id
  project_id
  hours_assigned
  is_overtime
}
```

---

### 11.2 Scheduling Engine

**Responsibility:**

* Match employees to projects
* Enforce constraints:

  * Skill match
  * No time overlap
  * Daily hour limits

**Key Design Choice:**
A **greedy, rule-based approach** was chosen instead of optimization algorithms to maintain transparency.

---

### 11.3 Capacity & Cost Analyzer

This component runs **after scheduling**, not during.

**Responsibilities:**

* Calculate utilization per employee
* Identify:

  * Over-utilization
  * Under-utilization
* Aggregate:

  * Regular cost
  * Overtime cost (1.3×)

This separation allows **what-if analysis** without re-running scheduling.

---

## 12. Cost Computation Logic (Explicit & Explainable)

### Regular Cost

```
regular_cost = regular_hours × 1 unit
```

### Overtime Cost

```
overtime_cost = overtime_hours × 1.3 units
```

### Total Cost

```
total_cost = regular_cost + overtime_cost
```

This explicit breakdown helps stakeholders **see where money is being spent**.

---

## 13. Why This Architecture Was Chosen (Trade-offs)

| Choice                         | Reason                             |
| ------------------------------ | ---------------------------------- |
| Rule-based scheduling          | Easy to reason, debug, and explain |
| No optimization algorithms     | Avoids over-engineering            |
| Post-analysis cost computation | Enables clear business insights    |
| Simple data models             | Reduces cognitive load             |

This design aligns with the assignment’s emphasis on **thinking quality over algorithmic complexity**.

---

## 14. Extensibility 
The architecture allows future improvements **without redesign**:

* Replace scheduling logic with:

  * Heuristics
  * Linear programming
  * AI-assisted suggestions
* Add:

  * Weekly/monthly views
  * Skill scarcity weighting
  * Hiring simulation

These are **optional extensions**, not required for the current scope.

---

## 15. Final Alignment With Evaluation Criteria

This submission demonstrates:

* ✅ Logical problem decomposition
* ✅ Clear assumptions & constraints
* ✅ Thoughtful cost vs capacity reasoning
* ✅ Responsible AI usage
* ✅ Practical system design thinking

The solution is **intentionally simple, transparent, and business-aligned**, making it suitable for real-world decision-making.

---

### ✅ Final Note 

> *This solution prioritizes clarity, explainability, and real-world reasoning over algorithmic optimization, in line with the assignment instructions.*

---
