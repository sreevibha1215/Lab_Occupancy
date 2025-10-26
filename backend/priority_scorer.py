import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from datetime import datetime, timedelta
import logging
import re
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriorityScorer:
    def __init__(self):
        """Initialize NLP model for authenticity detection"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.model = AutoModel.from_pretrained("distilbert-base-uncased")
            self.model.eval()
            logger.info("DistilBERT model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load DistilBERT: {e}. Using rule-based scoring only.")
            self.tokenizer = None
            self.model = None
        
        # Capacity utilization thresholds
        self.OPTIMAL_UTILIZATION_MIN = 0.85  # 85% capacity
        self.OPTIMAL_UTILIZATION_MAX = 1.00  # 100% capacity
        self.ACCEPTABLE_UTILIZATION_MIN = 0.50  # 50% capacity
        self.ACCEPTABLE_UTILIZATION_MAX = 1.05  # 105% capacity (slight overbook)
        self.MAX_UTILIZATION = 1.20  # 120% = auto-reject
        
        # User behavior tracking (in production, use database)
        self.user_history = {}  # user_email -> {bookings: [], cancellations: []}
    
    def calculate_priority(self, purpose, description, num_participants, lab_capacity, 
                          urgency='normal', user_email=None, booking_date=None, 
                          has_proof=False, proof_type=None, user_role='student'):
        """
        Fair priority scoring system focused on capacity utilization.
        
        Args:
            purpose: Purpose category
            description: Detailed description
            num_participants: Number of participants
            lab_capacity: Lab capacity
            urgency: Urgency level
            user_email: User identifier for history tracking
            booking_date: Date of booking (for timing scoring)
            has_proof: Whether user provided verification proof
            proof_type: Type of proof (faculty_approval, official_letter, etc.)
            user_role: User role (student, faculty, admin)
        
        Returns: Dict with score, breakdown, and flags
        """
        
        # Check for auto-rejection conditions
        utilization_ratio = num_participants / lab_capacity
        if utilization_ratio > self.MAX_UTILIZATION:
            return {
                "accepted": False,
                "score": 0,
                "breakdown": {},
                "flags": ["CAPACITY_EXCEEDED"],
                "message": f"Participants ({num_participants}) exceed maximum allowed ({int(lab_capacity * self.MAX_UTILIZATION)})"
            }
        
        # 1. Capacity Match Score (50 points)
        capacity_score = self._calculate_capacity_score(num_participants, lab_capacity)
        
        # 2. Authenticity & Verification Score (25 points)
        authenticity_score = self._calculate_authenticity_score(
            purpose, description, has_proof, proof_type, user_role
        )
        
        # 3. Timing & Urgency Score (15 points)
        timing_score = self._calculate_timing_score(urgency, booking_date, description)
        
        # 4. Fairness & Past Usage Score (10 points)
        fairness_score = self._calculate_fairness_score(user_email, num_participants)
        
        # Calculate total
        total_score = capacity_score + authenticity_score + timing_score + fairness_score
        
        # Detect fraud flags
        flags = self._detect_fraud_flags(description, purpose, utilization_ratio, has_proof)
        
        # Apply penalties for suspicious behavior
        if flags:
            penalty = len(flags) * 5  # 5 points per flag
            total_score = max(0, total_score - penalty)
        
        # Determine acceptance
        accepted = total_score >= 50 and utilization_ratio <= self.ACCEPTABLE_UTILIZATION_MAX
        
        breakdown = {
            "capacity_score": round(capacity_score, 2),
            "authenticity_score": round(authenticity_score, 2),
            "timing_score": round(timing_score, 2),
            "fairness_score": round(fairness_score, 2),
            "fraud_penalty": len(flags) * 5 if flags else 0,
            "utilization_ratio": round(utilization_ratio, 3)
        }
        
        logger.info(f"Fair scoring - Total: {total_score:.1f} | Breakdown: {breakdown} | Flags: {flags}")
        
        return {
            "accepted": accepted,
            "score": round(total_score, 2),
            "breakdown": breakdown,
            "flags": flags
        }
    
    def _calculate_capacity_score(self, num_participants, lab_capacity):
        """
        Calculate score based on capacity utilization (50 points max).
        Uses Gaussian curve centered at optimal utilization.
        
        Scoring:
        - 85-100% capacity: 50 points (optimal)
        - 70-85%: 40-49 points (good)
        - 50-70%: 30-39 points (acceptable)
        - <50% or >105%: <30 points (poor utilization)
        """
        utilization_ratio = num_participants / lab_capacity
        
        # Optimal range (85-100%)
        if self.OPTIMAL_UTILIZATION_MIN <= utilization_ratio <= self.OPTIMAL_UTILIZATION_MAX:
            # Perfect score
            return 50.0
        
        # Gaussian curve for other ranges
        optimal_center = (self.OPTIMAL_UTILIZATION_MIN + self.OPTIMAL_UTILIZATION_MAX) / 2
        
        # Calculate distance from optimal center
        distance = abs(utilization_ratio - optimal_center)
        
        # Gaussian scoring with steeper penalty for extremes
        sigma = 0.3  # Standard deviation
        gaussian_score = 50 * math.exp(-(distance ** 2) / (2 * sigma ** 2))
        
        # Extra penalty for very low utilization (<30%) - wasteful
        if utilization_ratio < 0.30:
            gaussian_score *= 0.5
        
        # Penalty for slight overbooking (100-105%)
        if 1.00 < utilization_ratio <= 1.05:
            gaussian_score *= 0.85
        
        # Heavy penalty for significant overbooking (105-120%)
        if 1.05 < utilization_ratio <= 1.20:
            gaussian_score *= 0.4
        
        return max(0, min(50, gaussian_score))
    
    def _calculate_authenticity_score(self, purpose, description, has_proof, proof_type, user_role):
        """
        Calculate authenticity score (25 points max).
        
        Focuses on proof and detail quality, NOT purpose labels.
        Purpose labels alone don't give high scores.
        """
        score = 0
        
        # Base score from role (0-5 points)
        role_scores = {
            'faculty': 5,
            'admin': 5,
            'phd': 4,
            'postgrad': 3,
            'student': 2
        }
        score += role_scores.get(user_role, 2)
        
        # Proof verification (0-12 points) - MOST IMPORTANT
        if has_proof:
            proof_scores = {
                'faculty_approval': 12,
                'official_letter': 10,
                'department_email': 9,
                'event_registration': 8,
                'course_syllabus': 7,
                'admin_approval': 12
            }
            score += proof_scores.get(proof_type, 5)
        else:
            # No proof for academic purposes = penalty
            if purpose in ['exam', 'lecture', 'research']:
                score -= 5  # Heavy penalty for claiming academic use without proof
        
        # Description detail quality (0-8 points)
        detail_score = self._analyze_description_details(description)
        score += detail_score
        
        return max(0, min(25, score))
    
    def _analyze_description_details(self, description):
        """
        Analyze description for concrete details (8 points max).
        Looks for specific information, not just generic claims.
        """
        if not description or len(description.strip()) < 20:
            return 0
        
        score = 0
        description_lower = description.lower()
        
        # Check for specific details (each adds points)
        detail_patterns = {
            'date_mention': r'\b(january|february|march|april|may|june|july|august|september|october|november|december|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            'time_mention': r'\b(\d{1,2}:\d{2}|am|pm|morning|afternoon|evening)\b',
            'faculty_name': r'\b(dr\.|prof\.|professor|dr |faculty)\s+[a-z]+\b',
            'course_code': r'\b([a-z]{2,4}\s*\d{3,4}|course\s+\d+)\b',
            'venue_mention': r'\b(room|hall|auditorium|lab|building|block|floor)\s+[a-z0-9]+\b',
            'participant_list': r'\b(students?|participants?|attendees?|members?)\s+(from|of|in)\b',
        }
        
        for pattern_name, pattern in detail_patterns.items():
            if re.search(pattern, description_lower):
                score += 1.5
        
        # Penalty for generic/vague descriptions
        generic_phrases = [
            'very important', 'urgent meeting', 'important event',
            'necessary', 'required', 'must have', 'need urgently'
        ]
        
        generic_count = sum(1 for phrase in generic_phrases if phrase in description_lower)
        if generic_count > 2:
            score -= 2  # Penalty for too many generic urgency claims
        
        return max(0, min(8, score))
    
    def _calculate_timing_score(self, urgency, booking_date, description):
        """
        Calculate timing score (15 points max).
        Real urgency based on actual event proximity, not just labels.
        """
        score = 0
        
        # Time until event (if booking_date provided)
        if booking_date:
            try:
                event_date = datetime.fromisoformat(booking_date) if isinstance(booking_date, str) else booking_date
                days_until = (event_date - datetime.now()).days
                
                # Proximity scoring
                if days_until <= 2:
                    score += 8  # Very soon
                elif days_until <= 7:
                    score += 6  # Within a week
                elif days_until <= 14:
                    score += 4  # Within 2 weeks
                else:
                    score += 2  # More than 2 weeks
            except:
                score += 2  # Fallback if date parsing fails
        else:
            score += 2  # No date provided
        
        # Urgency level (0-7 points) - but only if justified
        urgency_base = {
            'high': 7,
            'medium': 4,
            'normal': 2,
            'low': 0
        }
        urgency_score = urgency_base.get(urgency, 2)
        
        # Check if urgency is justified by description
        if urgency in ['high', 'medium']:
            urgency_keywords = ['deadline', 'urgent', 'critical', 'emergency', 'tomorrow', 'today']
            has_urgency_context = any(kw in description.lower() for kw in urgency_keywords)
            
            if not has_urgency_context:
                urgency_score *= 0.3  # Reduce if claiming urgency without context
        
        score += urgency_score
        
        return max(0, min(15, score))
    
    def _calculate_fairness_score(self, user_email, num_participants):
        """
        Calculate fairness score (10 points max).
        Penalizes frequent over-bookers and cancellers.
        """
        score = 10  # Start with full score
        
        if not user_email or user_email not in self.user_history:
            return score  # New user, give benefit of doubt
        
        history = self.user_history[user_email]
        
        # Penalty for frequent cancellations
        total_bookings = len(history.get('bookings', []))
        cancellations = len(history.get('cancellations', []))
        
        if total_bookings > 0:
            cancellation_rate = cancellations / total_bookings
            if cancellation_rate > 0.3:  # >30% cancellation rate
                score -= 3
            elif cancellation_rate > 0.15:  # >15% cancellation rate
                score -= 1.5
        
        # Penalty for pattern of overbooking (booking more than needed)
        past_bookings = history.get('bookings', [])
        if len(past_bookings) >= 3:
            avg_utilization = np.mean([b.get('utilization', 1.0) for b in past_bookings[-5:]])
            if avg_utilization < 0.5:  # Consistently under-utilizing
                score -= 2
        
        # Penalty for frequent high-participant bookings (potential gaming)
        high_count_bookings = [b for b in past_bookings if b.get('participants', 0) > 50]
        if len(high_count_bookings) > len(past_bookings) * 0.7:  # >70% are high count
            score -= 2
        
        return max(0, score)
    
    def _detect_fraud_flags(self, description, purpose, utilization_ratio, has_proof):
        """
        Detect suspicious patterns that indicate gaming/fraud.
        Returns list of flag names.
        """
        flags = []
        
        # Flag 1: Generic description with high-priority purpose
        if purpose in ['exam', 'emergency', 'lecture'] and len(description.strip()) < 30:
            flags.append("GENERIC_DESCRIPTION")
        
        # Flag 2: No proof for academic purpose
        if purpose in ['exam', 'lecture', 'research'] and not has_proof:
            flags.append("NO_PROOF_ACADEMIC")
        
        # Flag 3: Extremely low utilization (<25%)
        if utilization_ratio < 0.25:
            flags.append("WASTEFUL_UTILIZATION")
        
        # Flag 4: Description filled with urgency keywords but no details
        urgency_keywords = ['urgent', 'emergency', 'critical', 'immediately', 'asap', 'important']
        urgency_count = sum(1 for kw in urgency_keywords if kw in description.lower())
        
        if urgency_count >= 3 and len(description.strip()) < 50:
            flags.append("KEYWORD_STUFFING")
        
        # Flag 5: Repetitive generic phrases
        if description.count('important') > 2 or description.count('urgent') > 2:
            flags.append("REPETITIVE_CLAIMS")
        
        return flags
    
    def explain(self, result):
        """
        Generate human-readable explanation of scoring result.
        
        Args:
            result: Output from calculate_priority()
        
        Returns: Dictionary with explanation text
        """
        breakdown = result.get('breakdown', {})
        flags = result.get('flags', [])
        score = result.get('score', 0)
        accepted = result.get('accepted', False)
        
        explanation = {
            "status": "✅ ACCEPTED" if accepted else "❌ REJECTED",
            "total_score": f"{score}/100",
            "verdict": self._generate_verdict(accepted, score),
            "breakdown_explanation": {
                "capacity_match": self._explain_capacity(breakdown.get('capacity_score', 0), 
                                                         breakdown.get('utilization_ratio', 0)),
                "authenticity": self._explain_authenticity(breakdown.get('authenticity_score', 0)),
                "timing": self._explain_timing(breakdown.get('timing_score', 0)),
                "fairness": self._explain_fairness(breakdown.get('fairness_score', 0))
            },
            "flags_explanation": self._explain_flags(flags),
            "recommendation": self._generate_recommendation(accepted, score, breakdown, flags)
        }
        
        return explanation
    
    def _generate_verdict(self, accepted, score):
        if accepted:
            if score >= 80:
                return "Excellent match! High priority for approval."
            elif score >= 65:
                return "Good reservation. Approved with standard priority."
            else:
                return "Acceptable reservation. Approved with lower priority."
        else:
            if score < 30:
                return "Score too low. Improve capacity match and provide verification."
            elif score < 50:
                return "Below threshold. Consider alternative dates or provide proof."
            else:
                return "Rejected due to capacity or verification issues."
    
    def _explain_capacity(self, score, utilization):
        if score >= 45:
            return f"Excellent capacity match ({utilization*100:.0f}% utilization). Optimal use of resources."
        elif score >= 35:
            return f"Good capacity match ({utilization*100:.0f}% utilization)."
        elif score >= 25:
            return f"Acceptable capacity match ({utilization*100:.0f}% utilization)."
        else:
            return f"Poor capacity match ({utilization*100:.0f}% utilization). Consider smaller lab or more participants."
    
    def _explain_authenticity(self, score):
        if score >= 20:
            return "Strong verification with proof provided."
        elif score >= 15:
            return "Good authenticity. Details provided."
        elif score >= 10:
            return "Moderate authenticity. Consider providing proof."
        else:
            return "Low authenticity. Proof required for academic purposes."
    
    def _explain_timing(self, score):
        if score >= 12:
            return "Urgent timing justified."
        elif score >= 8:
            return "Reasonable timing."
        else:
            return "Low urgency."
    
    def _explain_fairness(self, score):
        if score >= 8:
            return "Good user history."
        elif score >= 5:
            return "Acceptable user behavior."
        else:
            return "Concerns with past bookings (cancellations/misuse)."
    
    def _explain_flags(self, flags):
        if not flags:
            return "✅ No suspicious patterns detected."
        
        flag_descriptions = {
            "GENERIC_DESCRIPTION": "Description lacks specific details",
            "NO_PROOF_ACADEMIC": "Academic purpose claimed without verification",
            "WASTEFUL_UTILIZATION": "Very low capacity utilization (wasteful)",
            "KEYWORD_STUFFING": "Too many urgency keywords without substance",
            "REPETITIVE_CLAIMS": "Repetitive urgency claims",
            "CAPACITY_EXCEEDED": "Exceeds maximum capacity"
        }
        
        return "⚠️ Flags: " + ", ".join([flag_descriptions.get(f, f) for f in flags])
    
    def _generate_recommendation(self, accepted, score, breakdown, flags):
        if accepted:
            return "Booking recommended for approval."
        
        recommendations = []
        
        if breakdown.get('capacity_score', 0) < 25:
            util = breakdown.get('utilization_ratio', 0)
            if util < 0.5:
                recommendations.append("Choose a smaller lab to match your group size")
            else:
                recommendations.append("Consider adding more participants or choose a smaller venue")
        
        if breakdown.get('authenticity_score', 0) < 10:
            recommendations.append("Provide verification (faculty approval, official letter, etc.)")
        
        if "NO_PROOF_ACADEMIC" in flags:
            recommendations.append("Academic purposes require proof of authorization")
        
        if "GENERIC_DESCRIPTION" in flags:
            recommendations.append("Add specific details: faculty names, dates, course codes, agenda")
        
        if not recommendations:
            recommendations.append("Improve overall score by addressing capacity match and verification")
        
        return " | ".join(recommendations)

