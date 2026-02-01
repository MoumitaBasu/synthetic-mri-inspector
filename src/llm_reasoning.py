"""
LLM Reasoning Layer for MRI Quality Control
Provides intelligent explanations, decision recommendations, and threshold suggestions.

This module can integrate with various LLM providers (OpenAI, Google Gemini, Anthropic, etc.)
or work in a local/rule-based mode when no API is configured.
"""
import os
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # Rule-based fallback


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    api_key: Optional[str] = None
    model_name: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 1024
    timeout: int = 30
    
    @classmethod
    def from_env(cls, provider: LLMProvider = None) -> 'LLMConfig':
        """Create config from environment variables"""
        # Auto-detect provider from available API keys
        if provider is None:
            if os.getenv('OPENAI_API_KEY'):
                provider = LLMProvider.OPENAI
            elif os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'):
                provider = LLMProvider.GEMINI
            elif os.getenv('ANTHROPIC_API_KEY'):
                provider = LLMProvider.ANTHROPIC
            else:
                provider = LLMProvider.LOCAL
        
        # Get API key based on provider
        api_key = None
        model_name = "local"
        
        if provider == LLMProvider.OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            model_name = os.getenv('OPENAI_MODEL', 'gpt-4')
        elif provider == LLMProvider.GEMINI:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        elif provider == LLMProvider.ANTHROPIC:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            model_name = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
        
        return cls(
            provider=provider,
            api_key=api_key,
            model_name=model_name
        )


@dataclass
class ReasoningResult:
    """Result from LLM reasoning"""
    explanation: str
    confidence_assessment: str
    suggested_action: str
    threshold_suggestions: Optional[Dict] = None
    additional_insights: Optional[List[str]] = None
    raw_response: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'explanation': self.explanation,
            'confidence_assessment': self.confidence_assessment,
            'suggested_action': self.suggested_action,
            'threshold_suggestions': self.threshold_suggestions,
            'additional_insights': self.additional_insights
        }


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")
        return self._client
    
    def is_available(self) -> bool:
        return self.config.api_key is not None
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response.choices[0].message.content


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._model = None
    
    def _get_model(self):
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self._model = genai.GenerativeModel(self.config.model_name)
            except ImportError:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        return self._model
    
    def is_available(self) -> bool:
        return self.config.api_key is not None
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        model = self._get_model()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        return self._client
    
    def is_available(self) -> bool:
        return self.config.api_key is not None
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        client = self._get_client()
        
        message = client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            system=system_prompt or "You are a quality control expert for MRI analysis.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text


class LocalReasoningProvider(BaseLLMProvider):
    """
    Local rule-based reasoning when no LLM API is available.
    Provides deterministic explanations based on feature patterns.
    """
    
    def __init__(self, config: LLMConfig = None):
        self.config = config
    
    def is_available(self) -> bool:
        return True  # Always available
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        # Parse the prompt to extract key information
        # This is a simplified rule-based response generator
        
        # Extract features from prompt
        uniformity = self._extract_value(prompt, r"uniformity[:\s]+(\d+\.?\d*)")
        symmetry = self._extract_value(prompt, r"symmetry[:\s]+(\d+\.?\d*)")
        anomaly = "anomaly" in prompt.lower() and "true" in prompt.lower()
        quality = self._extract_pattern(prompt, r"quality[:\s]+['\"]?(\w+)['\"]?")
        confidence = self._extract_value(prompt, r"confidence[:\s]+(\d+\.?\d*)")
        
        # Generate explanation based on extracted values
        return self._generate_rule_based_response(
            uniformity, symmetry, anomaly, quality, confidence
        )
    
    def _extract_value(self, text: str, pattern: str) -> Optional[float]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def _extract_pattern(self, text: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _generate_rule_based_response(self, uniformity: float, symmetry: float,
                                       anomaly: bool, quality: str, 
                                       confidence: float) -> str:
        """Generate rule-based explanation"""
        parts = []
        
        # Quality explanation
        if quality:
            if quality.lower() == 'premium':
                parts.append(f"The sample has been classified as {quality.upper()} grade, indicating it meets all quality criteria for market release.")
            elif quality.lower() == 'standard':
                parts.append(f"The sample has been classified as {quality.upper()} grade, suggesting it meets minimum quality standards but shows some areas for improvement.")
            else:
                parts.append(f"The sample has been classified as {quality.upper()}, indicating significant quality concerns that require attention.")
        
        # Feature-based insights
        if uniformity is not None:
            if uniformity > 0.75:
                parts.append(f"The uniformity score of {uniformity:.2f} indicates excellent consistency throughout the sample structure.")
            elif uniformity > 0.6:
                parts.append(f"The uniformity score of {uniformity:.2f} shows acceptable consistency with minor variations.")
            else:
                parts.append(f"The low uniformity score of {uniformity:.2f} suggests significant structural inconsistencies that may impact quality.")
        
        if symmetry is not None:
            if symmetry > 0.75:
                parts.append(f"The symmetry score of {symmetry:.2f} demonstrates well-balanced structural development.")
            elif symmetry > 0.65:
                parts.append(f"The symmetry score of {symmetry:.2f} is within acceptable range but could be improved.")
            else:
                parts.append(f"The asymmetry (score: {symmetry:.2f}) may indicate developmental irregularities.")
        
        if anomaly:
            parts.append("Anomalous regions have been detected which require careful consideration in the final assessment.")
        
        # Confidence assessment
        if confidence is not None:
            if confidence > 85:
                parts.append(f"The classification confidence of {confidence:.1f}% is high, indicating reliable results.")
            elif confidence > 70:
                parts.append(f"The classification confidence of {confidence:.1f}% is moderate. The decision is reasonably reliable but edge cases may exist.")
            else:
                parts.append(f"The classification confidence of {confidence:.1f}% is relatively low. Human review is recommended to verify the automated assessment.")
        
        # Recommendations
        parts.append("\nRECOMMENDATIONS:")
        if quality and quality.lower() == 'premium':
            parts.append("• Proceed with standard market release protocols")
            parts.append("• No additional inspection required")
        elif quality and quality.lower() == 'standard':
            parts.append("• Consider secondary processing or grading")
            parts.append("• Re-inspection may be beneficial after processing")
        else:
            parts.append("• Quarantine sample for detailed review")
            parts.append("• Document defects for process improvement")
            parts.append("• Consider root cause analysis if defect rate is elevated")
        
        return "\n".join(parts)


class LLMReasoningLayer:
    """
    LLM-powered reasoning layer for the Quality Control Agent.
    
    Provides:
    - Natural language explanations of decisions
    - Confidence assessment and recommendations
    - Threshold adjustment suggestions
    - Additional insights from pattern recognition
    """
    
    SYSTEM_PROMPT = """You are an expert quality control analyst specializing in MRI-based inspection systems.
Your role is to:
1. Explain inspection results in clear, professional language
2. Assess the reliability of classification decisions
3. Suggest appropriate actions based on the analysis
4. Recommend threshold adjustments when patterns suggest optimization opportunities

Always be specific about the data you're interpreting and provide actionable insights.
Format your response with clear sections for Explanation, Confidence Assessment, and Recommendations."""
    
    def __init__(self, config: LLMConfig = None):
        """
        Initialize the LLM reasoning layer.
        
        Args:
            config: LLM configuration. If None, auto-detects from environment.
        """
        self.config = config or LLMConfig.from_env()
        self.provider = self._create_provider()
    
    def _create_provider(self) -> BaseLLMProvider:
        """Create the appropriate LLM provider"""
        if self.config.provider == LLMProvider.OPENAI:
            return OpenAIProvider(self.config)
        elif self.config.provider == LLMProvider.GEMINI:
            return GeminiProvider(self.config)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return AnthropicProvider(self.config)
        else:
            return LocalReasoningProvider(self.config)
    
    def is_available(self) -> bool:
        """Check if LLM reasoning is available"""
        return self.provider.is_available()
    
    def get_provider_name(self) -> str:
        """Get the name of the active provider"""
        return self.config.provider.value
    
    def explain_decision(self, features: Dict, classification: Dict,
                        tools_used: List[str] = None,
                        requires_review: bool = False) -> str:
        """
        Generate a natural language explanation of the inspection decision.
        
        Args:
            features: Dictionary of extracted features
            classification: Classification results
            tools_used: List of tools that were used in the analysis
            requires_review: Whether human review was flagged
            
        Returns:
            Natural language explanation
        """
        prompt = self._build_explanation_prompt(features, classification, 
                                                 tools_used, requires_review)
        
        try:
            response = self.provider.generate(prompt, self.SYSTEM_PROMPT)
            return response
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def assess_confidence(self, features: Dict, classification: Dict) -> ReasoningResult:
        """
        Perform comprehensive confidence assessment.
        
        Args:
            features: Dictionary of extracted features
            classification: Classification results
            
        Returns:
            ReasoningResult with detailed assessment
        """
        prompt = self._build_confidence_prompt(features, classification)
        
        try:
            response = self.provider.generate(prompt, self.SYSTEM_PROMPT)
            return self._parse_reasoning_response(response)
        except Exception as e:
            return ReasoningResult(
                explanation=f"Assessment unavailable: {str(e)}",
                confidence_assessment="Unable to assess",
                suggested_action="Proceed with caution; consider human review"
            )
    
    def suggest_threshold_adjustments(self, batch_results: List[Dict],
                                       current_thresholds: Dict) -> Dict:
        """
        Analyze batch results and suggest threshold adjustments.
        
        Args:
            batch_results: List of inspection results from a batch
            current_thresholds: Current threshold configuration
            
        Returns:
            Dictionary with suggested threshold adjustments and reasoning
        """
        prompt = self._build_threshold_prompt(batch_results, current_thresholds)
        
        try:
            response = self.provider.generate(prompt, self.SYSTEM_PROMPT)
            return self._parse_threshold_response(response, current_thresholds)
        except Exception as e:
            return {
                'suggestions': {},
                'reasoning': f"Unable to generate suggestions: {str(e)}",
                'apply_changes': False
            }
    
    def get_additional_insights(self, features: Dict) -> List[str]:
        """
        Generate additional insights from the features.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            List of insight strings
        """
        prompt = f"""Analyze these MRI inspection features and provide 3-5 brief additional insights that might be useful for quality control:

Features:
{json.dumps({k: v for k, v in features.items() if not isinstance(v, (list,)) or (isinstance(v, list) and len(v) < 10)}, indent=2)}

Provide insights as a numbered list, focusing on:
- Patterns that might indicate specific conditions
- Relationships between features
- Quality improvement opportunities"""
        
        try:
            response = self.provider.generate(prompt, self.SYSTEM_PROMPT)
            # Parse numbered list from response
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    clean = re.sub(r'^[\d\.\-\•\*]+\s*', '', line)
                    if clean:
                        insights.append(clean)
            return insights[:5]  # Limit to 5 insights
        except Exception as e:
            return [f"Insights unavailable: {str(e)}"]
    
    def _build_explanation_prompt(self, features: Dict, classification: Dict,
                                   tools_used: List[str], requires_review: bool) -> str:
        """Build prompt for decision explanation"""
        # Filter features to essential ones
        key_features = {
            'uniformity_score': features.get('uniformity_score'),
            'overall_symmetry': features.get('overall_symmetry'),
            'has_anomaly': features.get('has_anomaly'),
            'anomaly_severity': features.get('anomaly_severity'),
            'estimated_wall_thickness': features.get('estimated_wall_thickness'),
            'has_core_structure': features.get('has_core_structure')
        }
        
        return f"""Please explain the following MRI quality inspection decision in clear, professional language:

EXTRACTED FEATURES:
{json.dumps(key_features, indent=2)}

CLASSIFICATION:
- Quality: {classification.get('quality', 'Unknown')}
- Quality Score: {classification.get('quality_score', 0)}/100
- Confidence: {classification.get('confidence', 0)}%
- Decision: {classification.get('decision', 'N/A')}

ANALYSIS TOOLS USED: {', '.join(tools_used or ['N/A'])}
HUMAN REVIEW REQUIRED: {requires_review}

REASONING FROM SYSTEM:
{json.dumps(classification.get('reasoning', []), indent=2)}

Please provide:
1. A clear explanation of why this classification was made
2. An assessment of the confidence level
3. Any concerns or additional considerations
4. Recommended next steps"""
    
    def _build_confidence_prompt(self, features: Dict, classification: Dict) -> str:
        """Build prompt for confidence assessment"""
        return f"""Assess the confidence level of this MRI quality classification:

Features Summary:
- Uniformity: {features.get('uniformity_score', 'N/A')}
- Symmetry: {features.get('overall_symmetry', 'N/A')}
- Anomaly Detected: {features.get('has_anomaly', False)}
- Anomaly Severity: {features.get('anomaly_severity', 0)}

Classification:
- Quality: {classification.get('quality', 'Unknown')}
- Score: {classification.get('quality_score', 0)}/100
- Stated Confidence: {classification.get('confidence', 0)}%

Please provide:
1. EXPLANATION: A paragraph explaining the decision
2. CONFIDENCE ASSESSMENT: Your assessment of whether the confidence is appropriate
3. SUGGESTED ACTION: What should be done with this sample
4. THRESHOLD SUGGESTIONS: Any recommendations for threshold adjustments"""
    
    def _build_threshold_prompt(self, batch_results: List[Dict],
                                 current_thresholds: Dict) -> str:
        """Build prompt for threshold adjustment suggestions"""
        # Summarize batch results
        quality_counts = {}
        avg_confidence = 0
        low_confidence_count = 0
        
        for result in batch_results:
            quality = result.get('quality', 'Unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            avg_confidence += result.get('confidence', 0)
            if result.get('confidence', 100) < 70:
                low_confidence_count += 1
        
        avg_confidence /= max(len(batch_results), 1)
        
        return f"""Analyze this batch of MRI inspection results and suggest threshold adjustments:

BATCH SUMMARY ({len(batch_results)} samples):
- Quality Distribution: {json.dumps(quality_counts)}
- Average Confidence: {avg_confidence:.1f}%
- Low Confidence Samples: {low_confidence_count}

CURRENT THRESHOLDS:
{json.dumps(current_thresholds, indent=2)}

Based on this data, please suggest:
1. Whether any thresholds should be adjusted
2. Specific values for any recommended changes
3. Reasoning for each suggestion
4. Expected impact of the changes"""
    
    def _parse_reasoning_response(self, response: str) -> ReasoningResult:
        """Parse LLM response into ReasoningResult"""
        # Try to extract sections
        explanation = ""
        confidence_assessment = ""
        suggested_action = ""
        
        # Simple section extraction
        sections = re.split(r'\n(?=\d+\.|[A-Z]+:|\*\*)', response)
        
        for section in sections:
            lower = section.lower()
            if 'explanation' in lower or len(explanation) == 0:
                explanation = section.strip()
            elif 'confidence' in lower:
                confidence_assessment = section.strip()
            elif 'action' in lower or 'recommend' in lower:
                suggested_action = section.strip()
        
        # Fallback if parsing didn't work well
        if not explanation:
            explanation = response
        
        return ReasoningResult(
            explanation=explanation,
            confidence_assessment=confidence_assessment or "See explanation",
            suggested_action=suggested_action or "Follow standard protocols",
            raw_response=response
        )
    
    def _parse_threshold_response(self, response: str, 
                                   current_thresholds: Dict) -> Dict:
        """Parse threshold suggestion response"""
        suggestions = {}
        
        # Try to extract suggested values
        for key in current_thresholds.keys():
            # Look for patterns like "uniformity_min: 0.65" or "uniformity_min = 0.65"
            pattern = rf'{key}[:\s=]+(\d+\.?\d*)'
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    suggestions[key] = float(match.group(1))
                except ValueError:
                    pass
        
        return {
            'suggestions': suggestions,
            'reasoning': response,
            'apply_changes': len(suggestions) > 0,
            'current_thresholds': current_thresholds
        }


def create_reasoning_layer(provider: LLMProvider = None,
                           api_key: str = None) -> LLMReasoningLayer:
    """
    Factory function to create an LLM reasoning layer.
    
    Args:
        provider: LLM provider to use (auto-detects if None)
        api_key: API key (uses environment variable if None)
        
    Returns:
        Configured LLMReasoningLayer
    """
    if provider is None and api_key is None:
        # Auto-detect from environment
        config = LLMConfig.from_env()
    else:
        config = LLMConfig(
            provider=provider or LLMProvider.LOCAL,
            api_key=api_key
        )
    
    return LLMReasoningLayer(config)


if __name__ == "__main__":
    # Demo usage
    print("LLM Reasoning Layer Demo")
    print("=" * 60)
    
    # Create reasoning layer (will use local/rule-based if no API configured)
    reasoning = create_reasoning_layer()
    
    print(f"Provider: {reasoning.get_provider_name()}")
    print(f"Available: {reasoning.is_available()}")
    
    # Test with sample data
    sample_features = {
        'uniformity_score': 0.78,
        'overall_symmetry': 0.82,
        'has_anomaly': False,
        'anomaly_severity': 0.001,
        'estimated_wall_thickness': 0.15,
        'has_core_structure': True
    }
    
    sample_classification = {
        'quality': 'Premium',
        'quality_score': 92,
        'confidence': 88.5,
        'decision': 'Premium Grade - Proceed to market',
        'reasoning': [
            '✓ Good uniformity: 0.78',
            '✓ Symmetric structure: 0.82',
            '✓ Optimal wall thickness: 0.15'
        ]
    }
    
    print("\nGenerating explanation...")
    explanation = reasoning.explain_decision(
        sample_features,
        sample_classification,
        tools_used=['basic_intensity_extractor', 'symmetry_analyzer', 'anomaly_detector'],
        requires_review=False
    )
    
    print("\n" + "=" * 60)
    print("EXPLANATION:")
    print("=" * 60)
    print(explanation)
