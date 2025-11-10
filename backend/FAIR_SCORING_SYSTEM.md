# Fair Lab Reservation Scoring System

## Overview

The new scoring system **eliminates biases** and **prevents gaming** by focusing on **optimal capacity utilization** rather than participant count or purpose labels alone.

## 🎯 Core Principles

1. **Capacity Match is King** (50/100 points)
   - Best score when participants ≈ 85-100% of capacity
   - NOT "more participants = higher score"
   - Penalizes wasteful use (<30% capacity)
   - Penalizes overbooking (>105% capacity)

2. **Proof Over Claims** (25/100 points)
   - Purpose labels (exam, emergency) mean NOTHING without proof
   - Requires verification for academic purposes
   - Analyzes description quality, not keywords

3. **Real Urgency Only** (15/100 points)
   - Based on event proximity, not just urgency claims
   - Checks if urgency label matches description content
   - Penalizes "urgent" claims without context

4. **Fair Usage** (10/100 points)
   - Tracks user history (cancellations, misuse)
   - Penalizes pattern of overbooking or under-utilizing

## 📊 Scoring Breakdown

### Total Score = 100 Points

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **Capacity Match** | 50 pts | How well participants match lab capacity |
| **Authenticity & Verification** | 25 pts | Proof provided, description details |
| **Timing & Urgency** | 15 pts | Real urgency based on event date |
| **Fairness & Past Usage** | 10 pts | User behavior history |

## 🔢 Capacity Scoring (50 points)

Uses **Gaussian curve** centered at optimal utilization:

```
Utilization Ratio = num_participants / lab_capacity

Scoring:
- 85-100% capacity → 50 points (OPTIMAL)
- 70-84% capacity → 40-49 points (Good)
- 50-69% capacity → 30-39 points (Acceptable)
- 30-49% capacity → 15-29 points (Poor)
- <30% capacity → <15 points (Wasteful - penalized)
- 100-105% capacity → 35-42 points (Slight overbook - penalized)
- 105-120% capacity → 10-20 points (Heavy penalty)
- >120% capacity → AUTO-REJECT
```

### Example Scenarios:

**Scenario 1: Perfect Match**
- Lab capacity: 50
- Participants: 45 (90%)
- **Capacity Score: 50/50 ✅**

**Scenario 2: Wasteful**
- Lab capacity: 100
- Participants: 15 (15%)
- **Capacity Score: ~8/50 ❌** (Choose smaller lab!)

**Scenario 3: Gaming Attempt**
- Lab capacity: 40
- Participants: 80 (200%)
- **Result: AUTO-REJECTED ❌**

## 🔐 Authenticity Scoring (25 points)

**NOT based on purpose labels!**

### Score Breakdown:

1. **User Role** (0-5 pts)
   - Faculty/Admin: 5 pts
   - PhD Student: 4 pts
   - Postgrad: 3 pts
   - Student: 2 pts

2. **Proof Verification** (0-12 pts) - **MOST IMPORTANT**
   - Faculty approval: 12 pts
   - Official letter: 10 pts
   - Department email: 9 pts
   - Event registration: 8 pts
   - Course syllabus: 7 pts
   - **NO PROOF for academic purpose: -5 pts penalty!**

3. **Description Details** (0-8 pts)
   - Specific dates mentioned: +1.5 pts
   - Faculty names (Dr./Prof.): +1.5 pts
   - Course codes: +1.5 pts
   - Venue details: +1.5 pts
   - Time mentions: +1.5 pts
   - **Generic phrases ("very important"): -2 pts**

### Anti-Gaming Examples:

**❌ Gaming Attempt:**
```
Purpose: "Exam"
Description: "Very important urgent exam"
Has proof: No
→ Authenticity Score: 2 (role) + 0 (no details) - 5 (no proof for exam) = -3 → 0/25
```

**✅ Legitimate:**
```
Purpose: "Exam"
Description: "Mid-term exam for CSE301 Data Structures on March 15, 2pm-4pm, Dr. Kumar supervising, 45 students from Section A"
Has proof: Yes (Faculty approval)
→ Authenticity Score: 2 + 12 + 7.5 = 21.5/25
```

## ⏰ Timing Scoring (15 points)

### Breakdown:

1. **Event Proximity** (0-8 pts)
   - ≤2 days: 8 pts
   - 3-7 days: 6 pts
   - 8-14 days: 4 pts
   - >14 days: 2 pts

2. **Urgency Label** (0-7 pts) - **Only if justified**
   - High: 7 pts (if description has urgency keywords)
   - Medium: 4 pts
   - Normal: 2 pts
   - **Unjustified urgency: ×0.3 penalty**

### Example:

**❌ False Urgency:**
```
Urgency: High
Description: "Regular meeting"
Event date: 20 days away
→ Timing Score: 2 (date) + 7×0.3 (unjustified) = 4.1/15
```

## ⚖️ Fairness Scoring (10 points)

Starts at 10, penalties applied:

- **Cancellation rate >30%**: -3 pts
- **Cancellation rate >15%**: -1.5 pts
- **Consistently under-utilizing** (<50%): -2 pts
- **Pattern of high-count bookings** (>70%): -2 pts

## 🚨 Fraud Detection Flags

Each flag = **-5 points penalty**:

1. **GENERIC_DESCRIPTION**: Academic purpose with <30 chars
2. **NO_PROOF_ACADEMIC**: Exam/lecture/research without proof
3. **WASTEFUL_UTILIZATION**: <25% capacity used
4. **KEYWORD_STUFFING**: ≥3 urgency keywords in <50 chars
5. **REPETITIVE_CLAIMS**: "Important" or "urgent" repeated >2 times
6. **CAPACITY_EXCEEDED**: >120% capacity (auto-reject)

## 📈 Acceptance Criteria

**Minimum Requirements:**
- Score ≥ 50/100
- Utilization ≤ 105%

**Auto-Approval:**
- Score ≥ 65 + No conflicts

**Priority Override:**
- If conflict exists, new request must score 15+ points higher

## 🎯 How to Get High Score

### ✅ DO:
1. **Match participants to capacity** (85-100% ideal)
2. **Provide proof** for academic purposes
3. **Add specific details**: dates, names, codes, venues
4. **Book appropriate size lab** for your group
5. **Be honest** about urgency

### ❌ DON'T:
1. ❌ Book 100-person lab for 10 people
2. ❌ Claim "exam" without faculty approval
3. ❌ Stuff description with "urgent important critical"
4. ❌ Use vague descriptions like "important meeting"
5. ❌ Mark high urgency for events 30 days away

## 📊 Scoring Examples

### Example 1: Perfect Booking
```
Lab: E401 (capacity: 50)
Participants: 45
Purpose: Workshop
Description: "Python programming workshop for CSE students, March 15, 2-4pm, organized by Dr. Kumar, registered with CS department"
Has proof: Yes (Department email)
Urgency: Normal
Days until: 5

Scores:
- Capacity: 50/50 (90% utilization)
- Authenticity: 2 + 9 + 7.5 = 18.5/25
- Timing: 6 + 2 = 8/15
- Fairness: 10/10
- Flags: None

TOTAL: 86.5/100 ✅ AUTO-APPROVED
```

### Example 2: Gaming Attempt - REJECTED
```
Lab: Seminar-Hall (capacity: 100)
Participants: 10
Purpose: Emergency
Description: "Very urgent important emergency meeting"
Has proof: No
Urgency: High
Days until: 15

Scores:
- Capacity: ~7/50 (10% utilization - wasteful)
- Authenticity: 2 + 0 - 2 (generic) = 0/25
- Timing: 2 + 2.1 = 4.1/15
- Fairness: 10/10
- Flags: WASTEFUL_UTILIZATION (-5), REPETITIVE_CLAIMS (-5)

TOTAL: 11.1/100 ❌ REJECTED
Recommendation: Choose smaller lab (capacity 15-20)
```

### Example 3: Legitimate Emergency
```
Lab: E301 (capacity: 40)
Participants: 38
Purpose: Emergency
Description: "Emergency faculty meeting regarding curriculum changes, Dean's office notified, all CS faculty attending tomorrow 10am"
Has proof: Yes (Admin approval)
Urgency: High
Days until: 1

Scores:
- Capacity: 50/50 (95% utilization)
- Authenticity: 5 (faculty) + 12 + 6 = 23/25
- Timing: 8 + 7 = 15/15
- Fairness: 10/10
- Flags: None

TOTAL: 98/100 ✅ HIGHEST PRIORITY
```

## 🔄 Migration from Old System

### Old System Issues:
- ❌ More participants = always higher score
- ❌ Purpose "exam" = instant high priority
- ❌ No capacity consideration
- ❌ Keyword-based (gameable)

### New System Fixes:
- ✅ Capacity match is primary factor
- ✅ Purpose labels require proof
- ✅ Optimal utilization rewarded
- ✅ Fraud detection built-in

## 🛠️ API Changes

New parameters for `/api/reserve-lab`:

```javascript
{
  // Existing
  "lab_number": "E401",
  "date": "2025-03-15",
  "start_time": "14:00",
  "end_time": "16:00",
  "num_participants": 45,
  "purpose": "workshop",
  "description": "Python workshop...",
  "urgency": "normal",
  "user_email": "user@example.com",
  "user_name": "John Doe",
  
  // New (optional)
  "has_proof": true,
  "proof_type": "faculty_approval",
  "user_role": "student"
}
```

Response includes:

```javascript
{
  "success": true,
  "reservation_id": 123,
  "status": "approved",
  "priority_score": 86.5,
  "breakdown": {
    "capacity_score": 50,
    "authenticity_score": 18.5,
    "timing_score": 8,
    "fairness_score": 10,
    "fraud_penalty": 0,
    "utilization_ratio": 0.9
  },
  "flags": [],
  "message": "Reservation approved. Score: 86.5/100"
}
```

## 📖 For Users

When making a reservation:

1. **Choose appropriate lab size** - Don't book a 100-person hall for 10 people
2. **Provide details** - Mention faculty names, course codes, specific dates
3. **Upload proof** - For exams, lectures, official events
4. **Be realistic about urgency** - High urgency for next-day events, not next month
5. **Book responsibly** - System tracks your history

## 🎓 Summary

The new system is **fair**, **transparent**, and **game-proof**:

- ✅ Rewards efficient capacity utilization
- ✅ Requires proof for high-priority purposes
- ✅ Detects and penalizes gaming attempts
- ✅ Tracks user behavior patterns
- ✅ Provides detailed explanations

**Bottom line**: Book responsibly, provide proof, match capacity → High score!

