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
    
    def _distilbert_analysis(self, text):
        """
        Use DistilBERT to analyze semantic importance
        Returns 0-30 points based on urgency/importance indicators
        """
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        # Define reference embeddings for high-priority concepts
        high_priority_texts = [
            "urgent emergency critical deadline important",
            "exam assessment evaluation test examination",
            "conference presentation seminar workshop important meeting"
        ]
        
        priority_embeddings = []
        for ref_text in high_priority_texts:
            ref_inputs = self.tokenizer(ref_text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                ref_outputs = self.model(**ref_inputs)
                ref_embedding = ref_outputs.last_hidden_state.mean(dim=1)
                priority_embeddings.append(ref_embedding)
        
        # Calculate cosine similarity with each reference
        similarities = []
        for priority_emb in priority_embeddings:
            similarity = torch.cosine_similarity(embeddings, priority_emb, dim=1)
            similarities.append(similarity.item())
        
        # Use maximum similarity
        max_similarity = max(similarities)
        
        # Convert similarity (0-1) to score (0-30)
        # Apply sigmoid-like transformation to emphasize high similarities
        score = 30 * (1 / (1 + np.exp(-10 * (max_similarity - 0.5))))
        
        return score
    
    def _get_participant_score(self, num_participants):
        """
        Score based on number of participants
        More participants = higher priority (more people affected)
        Returns 0-15 points
        """
        if num_participants >= 60:
            return 15
        elif num_participants >= 40:
            return 12
        elif num_participants >= 25:
            return 9
        elif num_participants >= 15:
            return 6
        else:
            return 3
    
    def _get_urgency_score(self, urgency):
        """
        Score based on user-specified urgency
        Returns 0-15 points
        """
        urgency_scores = {
            'high': 15,
            'medium': 10,
            'normal': 5,
            'low': 0
        }
        return urgency_scores.get(urgency.lower(), 5)
    
    def explain_score(self, purpose, description, num_participants, urgency='normal'):
        """
        Provide detailed explanation of priority score
        """
        purpose_score = self._get_purpose_score(purpose)
        semantic_score = self._get_semantic_score(description)
        participant_score = self._get_participant_score(num_participants)
        urgency_score = self._get_urgency_score(urgency)
        total = min(100, purpose_score + semantic_score + participant_score + urgency_score)
        
        return {
            "total_score": total,
            "breakdown": {
                "purpose": purpose_score,
                "semantic_analysis": semantic_score,
                "participants": participant_score,
                "urgency": urgency_score
            },
            "explanation": f"Purpose '{purpose}' adds {purpose_score} points. "
                          f"Description analysis adds {semantic_score:.1f} points. "
                          f"{num_participants} participants adds {participant_score} points. "
                          f"Urgency '{urgency}' adds {urgency_score} points."
        }

