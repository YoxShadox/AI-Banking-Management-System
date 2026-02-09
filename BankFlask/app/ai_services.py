"""
AI Services - Modular AI processing for EduAI platform
Includes NLP, skill extraction, recommendations, and more
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

class NLPService:
    """Natural Language Processing for resume and text analysis"""
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email from text"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number from text"""
        pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_work_experience(text: str) -> List[Dict]:
        """Extract work experience entries"""
        experiences = []
        # Simple pattern for years in roles
        pattern = r'(\d{4})[–-](\d{4}|Present|present|Current|current)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            start_year = int(match.group(1))
            end_year = int(match.group(2)) if match.group(2).isdigit() else 2024
            
            experiences.append({
                'start_year': start_year,
                'end_year': end_year,
                'duration': end_year - start_year
            })
        
        return experiences
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calculate text readability score (0-100)"""
        words = text.split()
        if len(words) < 50:
            return 20  # Too short
        
        sentences = len(re.split(r'[.!?]+', text))
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / max(sentences, 1)
        
        # Flesch Reading Ease adapted for 0-100 scale
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 5)
        return max(0, min(100, score))


class SkillExtractionService:
    """Extract and analyze skills from resume text"""
    
    # Predefined skill taxonomy
    TECHNICAL_SKILLS = {
        'Python': {'category': 'programming', 'demand': 95, 'growth': 92},
        'JavaScript': {'category': 'programming', 'demand': 90, 'growth': 85},
        'React': {'category': 'framework', 'demand': 88, 'growth': 90},
        'AWS': {'category': 'cloud', 'demand': 92, 'growth': 95},
        'Docker': {'category': 'devops', 'demand': 85, 'growth': 88},
        'Kubernetes': {'category': 'devops', 'demand': 80, 'growth': 92},
        'PostgreSQL': {'category': 'database', 'demand': 80, 'growth': 75},
        'Machine Learning': {'category': 'ai', 'demand': 95, 'growth': 98},
        'TensorFlow': {'category': 'ai', 'demand': 85, 'growth': 90},
        'SQL': {'category': 'database', 'demand': 90, 'growth': 70},
        'Git': {'category': 'tools', 'demand': 95, 'growth': 80},
        'REST API': {'category': 'architecture', 'demand': 90, 'growth': 80},
        'Agile': {'category': 'methodology', 'demand': 85, 'growth': 75},
    }
    
    SOFT_SKILLS = {
        'Leadership': {'demand': 85, 'growth': 80},
        'Communication': {'demand': 90, 'growth': 85},
        'Problem Solving': {'demand': 95, 'growth': 85},
        'Team Collaboration': {'demand': 88, 'growth': 80},
        'Project Management': {'demand': 80, 'growth': 75},
    }
    
    @classmethod
    def extract_skills(cls, text: str) -> List[Dict]:
        """Extract skills from resume text"""
        skills = []
        text_lower = text.lower()
        
        # Extract technical skills
        for skill, metadata in cls.TECHNICAL_SKILLS.items():
            if skill.lower() in text_lower:
                skills.append({
                    'name': skill,
                    'category': metadata['category'],
                    'market_demand': metadata['demand'],
                    'growth_potential': metadata['growth'],
                    'proficiency': 70  # Default proficiency
                })
        
        # Extract soft skills
        for skill, metadata in cls.SOFT_SKILLS.items():
            if skill.lower() in text_lower:
                skills.append({
                    'name': skill,
                    'category': 'soft',
                    'market_demand': metadata['demand'],
                    'growth_potential': metadata['growth'],
                    'proficiency': 65
                })
        
        return skills
    
    @classmethod
    def calculate_skill_gap(cls, user_skills: List[str], target_role: str) -> Dict:
        """Calculate skill gap for target role"""
        # Predefined skill requirements by role
        role_requirements = {
            'Data Scientist': ['Python', 'Machine Learning', 'SQL', 'Problem Solving', 'Communication'],
            'Full Stack Developer': ['JavaScript', 'Python', 'React', 'SQL', 'Git', 'REST API'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'Git', 'Problem Solving'],
            'Product Manager': ['Communication', 'Leadership', 'Project Management', 'Problem Solving'],
        }
        
        required = set(role_requirements.get(target_role, []))
        current = set(user_skills)
        
        missing = required - current
        excess = current - required
        
        gap_percentage = (len(missing) / len(required)) * 100 if required else 0
        
        return {
            'missing_skills': list(missing),
            'excess_skills': list(excess),
            'gap_percentage': gap_percentage,
            'completion_percentage': 100 - gap_percentage
        }


class RecommendationService:
    """AI-powered recommendations engine"""
    
    @staticmethod
    def recommend_learning_path(user: Dict, skills: List[str], target_role: str) -> Dict:
        """Generate personalized learning path"""
        
        skill_gap = SkillExtractionService.calculate_skill_gap(skills, target_role)
        missing_skills = skill_gap['missing_skills']
        
        # Create learning milestones
        milestones = [
            {
                'title': f'Master {missing_skills[0]}' if missing_skills else 'Advanced Skills',
                'duration_weeks': 4,
                'resources': ['Online Course', 'Practice Projects', 'Documentation']
            }
        ]
        
        if len(missing_skills) > 1:
            milestones.extend([
                {
                    'title': f'Learn {skill}',
                    'duration_weeks': 3,
                    'resources': ['Tutorial', 'Hands-on Labs']
                }
                for skill in missing_skills[1:3]  # Top 3 missing skills
            ])
        
        milestones.append({
            'title': 'Build Portfolio Project',
            'duration_weeks': 4,
            'resources': ['GitHub Repo', 'Project Demo', 'Blog Post']
        })
        
        total_days = sum(m['duration_weeks'] for m in milestones) * 7
        confidence = 100 - min(skill_gap['gap_percentage'], 50)  # Max 50% gap affects confidence
        
        return {
            'title': f'Path to {target_role}',
            'target_role': target_role,
            'milestones': milestones,
            'estimated_duration_days': total_days,
            'ai_confidence': confidence,
            'personalization_score': 85
        }
    
    @staticmethod
    def recommend_mentors(user: Dict, target_role: str, skills: List[str]) -> List[Dict]:
        """Recommend mentors based on target role"""
        
        mentor_profiles = [
            {
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'title': f'Senior {target_role}',
                'company': 'Google',
                'expertise': ['Python', 'System Design', 'Leadership'],
                'rating': 4.9,
                'reviews': 127,
                'hourly_rate': 150
            },
            {
                'first_name': 'Marcus',
                'last_name': 'Johnson',
                'title': f'{target_role} Lead',
                'company': 'Amazon',
                'expertise': ['Cloud Architecture', 'Team Management', 'Problem Solving'],
                'rating': 4.8,
                'reviews': 89,
                'hourly_rate': 120
            },
            {
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'title': f'Principal {target_role}',
                'company': 'Microsoft',
                'expertise': ['AI/ML', 'Mentoring', 'Career Growth'],
                'rating': 5.0,
                'reviews': 156,
                'hourly_rate': 180
            }
        ]
        
        return mentor_profiles
    
    @staticmethod
    def recommend_insights(user: Dict, recent_activity: Dict) -> List[Dict]:
        """Generate AI insights based on user activity"""
        
        insights = [
            {
                'type': 'SKILL_DEMAND',
                'title': 'High-Demand Skill Alert',
                'description': 'Machine Learning is in high demand. Consider adding this skill to your profile.',
                'priority': 'high',
                'action_items': ['Take ML course', 'Build ML project']
            },
            {
                'type': 'LEARNING_RECOMMENDATION',
                'title': 'Personalized Learning Path',
                'description': 'Based on your profile, we recommend focusing on cloud technologies.',
                'priority': 'medium',
                'action_items': ['Start AWS course', 'Practice with projects']
            },
            {
                'type': 'INTERVIEW_TIP',
                'title': 'Interview Preparation',
                'description': 'Practice behavioral questions for leadership roles.',
                'priority': 'high',
                'action_items': ['Review STAR method', 'Mock interviews']
            }
        ]
        
        return insights


class JobMatchService:
    """Calculate job match scores"""
    
    @staticmethod
    def calculate_match_score(user_skills: List[str], job_requirements: List[str]) -> Tuple[float, Dict]:
        """Calculate job-resume match score"""
        
        user_set = set(s.lower() for s in user_skills)
        req_set = set(r.lower() for r in job_requirements)
        
        matching_skills = user_set.intersection(req_set)
        missing_skills = req_set - user_set
        
        match_percentage = (len(matching_skills) / len(req_set)) * 100 if req_set else 0
        
        # Boost score for exact matches
        score = match_percentage * 1.1
        score = min(100, score)
        
        analysis = {
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills),
            'match_percentage': match_percentage,
            'confidence': 85
        }
        
        return float(score), analysis


class ATSService:
    """ATS (Applicant Tracking System) compatibility scoring"""
    
    @staticmethod
    def calculate_ats_score(resume_text: str) -> Tuple[float, List[str]]:
        """Calculate ATS compatibility score"""
        
        score = 100.0
        issues = []
        
        # Check for formatting issues
        if len(resume_text) < 100:
            score -= 20
            issues.append('Resume seems too short')
        
        if '[[' in resume_text or ']]' in resume_text:
            score -= 10
            issues.append('Contains special characters that may confuse ATS')
        
        # Check for keywords
        important_keywords = ['Skills', 'Experience', 'Education', 'Projects']
        missing = [kw for kw in important_keywords if kw.lower() not in resume_text.lower()]
        
        if missing:
            score -= len(missing) * 5
            issues.append(f'Missing sections: {", ".join(missing)}')
        
        # Whitespace analysis
        lines = resume_text.split('\n')
        if len(lines) < 10:
            score -= 15
            issues.append('Consider expanding resume content')
        
        score = max(0, min(100, score))
        
        return float(score), issues


class ImpactScoreService:
    """Calculate resume impact score"""
    
    @staticmethod
    def calculate_impact_score(resume_text: str, skills: List[str]) -> float:
        """Calculate how impactful the resume is"""
        
        score = 50.0
        
        # Action verbs indicate stronger impact
        action_verbs = ['Led', 'Managed', 'Developed', 'Designed', 'Improved', 'Increased', 'Reduced', 'Implemented']
        verb_count = sum(1 for verb in action_verbs if verb.lower() in resume_text.lower())
        score += min(verb_count * 3, 20)  # Max +20 points
        
        # Quantifiable results
        numbers = re.findall(r'\d+', resume_text)
        if len(numbers) > 5:
            score += 15
        
        # Skills diversity
        if len(skills) > 8:
            score += 10
        
        # Professional language
        unprofessional_words = ['awesome', 'cool', 'stuff', 'basically']
        unprofessional_count = sum(1 for word in unprofessional_words if word.lower() in resume_text.lower())
        score -= unprofessional_count * 5
        
        score = max(0, min(100, score))
        
        return float(score)
