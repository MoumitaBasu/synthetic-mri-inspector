"""
Quality Control Agent for MRI Analysis
An agentic decision-making system that dynamically selects analysis tools
and determines inspection workflow based on confidence thresholds.
"""
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

from tool_registry import ToolRegistry, ToolResult, ToolCategory, get_default_registry


class AgentState(Enum):
    """States in the agent's decision workflow"""
    INITIAL = "initial"
    BASIC_INSPECTION = "basic_inspection"
    DEEPER_ANALYSIS = "deeper_analysis"
    ANOMALY_INVESTIGATION = "anomaly_investigation"
    QUALITY_ASSESSMENT = "quality_assessment"
    FINAL_DECISION = "final_decision"
    HUMAN_REVIEW = "human_review"
    COMPLETE = "complete"


class ConfidenceLevel(Enum):
    """Confidence level categories"""
    HIGH = "high"       # > 85%
    MEDIUM = "medium"   # 70-85%
    LOW = "low"         # < 70%
    UNCERTAIN = "uncertain"  # < 60%


@dataclass
class AgentDecision:
    """Represents a decision made by the agent"""
    action: str
    reasoning: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class InspectionResult:
    """Final inspection result from the agent"""
    sample_id: str
    quality: str
    quality_score: float
    confidence: float
    decision: str
    reasoning: List[str]
    tools_used: List[str]
    execution_history: List[Dict]
    requires_human_review: bool
    suggested_actions: List[str]
    llm_explanation: Optional[str] = None
    total_execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'sample_id': self.sample_id,
            'quality': self.quality,
            'quality_score': self.quality_score,
            'confidence': self.confidence,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'tools_used': self.tools_used,
            'execution_history': self.execution_history,
            'requires_human_review': self.requires_human_review,
            'suggested_actions': self.suggested_actions,
            'llm_explanation': self.llm_explanation,
            'total_execution_time_ms': self.total_execution_time_ms
        }


class QualityControlAgent:
    """
    Agentic Quality Control System
    
    This agent dynamically decides:
    - Which analysis tools to run
    - Whether current analysis is sufficient
    - When to escalate to deeper analysis
    - Whether to flag for human review
    - How to explain its decisions
    
    The workflow is dynamic, not linear - the agent adapts based on
    intermediate results and confidence levels.
    """
    
    def __init__(self, 
                 tool_registry: Optional[ToolRegistry] = None,
                 confidence_thresholds: Optional[Dict] = None,
                 quality_thresholds: Optional[Dict] = None,
                 llm_reasoning: Optional[Any] = None):
        """
        Initialize the Quality Control Agent
        
        Args:
            tool_registry: Registry of available tools (uses default if None)
            confidence_thresholds: Thresholds for confidence-based decisions
            quality_thresholds: Thresholds for quality classification
            llm_reasoning: Optional LLM reasoning layer
        """
        self.tool_registry = tool_registry or get_default_registry()
        
        self.confidence_thresholds = confidence_thresholds or {
            'high': 0.85,
            'medium': 0.70,
            'low': 0.60,
            'human_review': 0.55
        }
        
        self.quality_thresholds = quality_thresholds or {
            'uniformity_min': 0.6,
            'symmetry_min': 0.65,
            'anomaly_severity_max': 0.02,
            'wall_thickness_min': 0.05,
            'wall_thickness_max': 0.25
        }
        
        self.llm_reasoning = llm_reasoning
        
        # Execution tracking
        self.execution_history: List[Dict] = []
        self.tools_used: List[str] = []
        self.decisions: List[AgentDecision] = []
        self.current_state = AgentState.INITIAL
        self.current_features: Dict = {}
        self.current_confidence = 0.0
        
    def inspect(self, img: np.ndarray, sample_id: str = None) -> InspectionResult:
        """
        Main entry point for inspecting a sample.
        
        This method orchestrates the entire inspection workflow,
        dynamically choosing which tools to run based on results.
        
        Args:
            img: MRI image as numpy array
            sample_id: Optional identifier for the sample
            
        Returns:
            InspectionResult with complete analysis
        """
        import time
        start_time = time.time()
        
        # Reset state for new inspection
        self._reset_state()
        sample_id = sample_id or f"sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._log_decision("start_inspection", 
                          f"Beginning inspection of {sample_id}", 
                          1.0)
        
        # ===== STEP 1: Basic Inspection =====
        self.current_state = AgentState.BASIC_INSPECTION
        self._run_basic_inspection(img)
        
        # ===== STEP 2: Evaluate if deeper analysis needed =====
        needs_deeper = self._decide_deeper_analysis()
        
        if needs_deeper:
            self.current_state = AgentState.DEEPER_ANALYSIS
            self._run_deeper_analysis(img)
        
        # ===== STEP 3: Check for anomaly investigation =====
        needs_anomaly_scan = self._decide_anomaly_investigation()
        
        if needs_anomaly_scan:
            self.current_state = AgentState.ANOMALY_INVESTIGATION
            self._run_anomaly_investigation(img)
        
        # ===== STEP 4: Quality Assessment =====
        self.current_state = AgentState.QUALITY_ASSESSMENT
        classification = self._run_quality_assessment()
        
        # ===== STEP 5: Final Decision =====
        self.current_state = AgentState.FINAL_DECISION
        final_result = self._make_final_decision(classification, sample_id)
        
        # ===== STEP 6: LLM Explanation (if available) =====
        if self.llm_reasoning is not None:
            llm_explanation = self._get_llm_explanation(final_result)
            final_result.llm_explanation = llm_explanation
        
        # Calculate total execution time
        total_time = (time.time() - start_time) * 1000
        final_result.total_execution_time_ms = total_time
        
        self.current_state = AgentState.COMPLETE
        return final_result
    
    def _reset_state(self):
        """Reset agent state for a new inspection"""
        self.execution_history = []
        self.tools_used = []
        self.decisions = []
        self.current_state = AgentState.INITIAL
        self.current_features = {}
        self.current_confidence = 0.0
    
    def _log_decision(self, action: str, reasoning: str, confidence: float, 
                      metadata: Dict = None):
        """Log a decision made by the agent"""
        decision = AgentDecision(
            action=action,
            reasoning=reasoning,
            confidence=confidence,
            metadata=metadata or {}
        )
        self.decisions.append(decision)
        self.execution_history.append({
            'state': self.current_state.value,
            'action': action,
            'reasoning': reasoning,
            'confidence': confidence,
            'timestamp': decision.timestamp
        })
    
    def _execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool and track results"""
        result = self.tool_registry.execute_tool(tool_name, **kwargs)
        
        if result.success:
            self.tools_used.append(tool_name)
            self.execution_history.append({
                'state': self.current_state.value,
                'tool': tool_name,
                'success': True,
                'execution_time_ms': result.execution_time_ms,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.execution_history.append({
                'state': self.current_state.value,
                'tool': tool_name,
                'success': False,
                'error': result.error_message,
                'timestamp': datetime.now().isoformat()
            })
        
        return result
    
    def _run_basic_inspection(self, img: np.ndarray):
        """
        Run basic inspection tools.
        Always runs these essential tools first.
        """
        self._log_decision("basic_inspection", 
                          "Running basic inspection tools for initial assessment",
                          1.0)
        
        # Always run these baseline tools
        basic_tools = [
            "basic_intensity_extractor",
            "uniformity_scorer",
            "basic_anomaly_detector"
        ]
        
        for tool_name in basic_tools:
            result = self._execute_tool(tool_name, img=img)
            if result.success:
                self.current_features.update(result.data)
        
        # Quick quality check to determine next steps
        quick_result = self._execute_tool("quick_quality_check", 
                                          features=self.current_features,
                                          thresholds=self.quality_thresholds)
        if quick_result.success:
            self.current_features.update(quick_result.data)
            self.current_confidence = quick_result.data.get('quick_confidence', 0.7)
    
    def _decide_deeper_analysis(self) -> bool:
        """
        Decide whether deeper analysis is needed.
        
        This is where the agent makes dynamic decisions based on
        current state rather than following a fixed pipeline.
        """
        # Check conditions that warrant deeper analysis
        reasons = []
        
        # Condition 1: Low confidence from quick check
        if self.current_confidence < self.confidence_thresholds['medium']:
            reasons.append(f"Quick check confidence too low ({self.current_confidence:.2f})")
        
        # Condition 2: Borderline uniformity
        uniformity = self.current_features.get('uniformity_score', 0)
        if 0.55 < uniformity < 0.65:
            reasons.append(f"Borderline uniformity ({uniformity:.3f})")
        
        # Condition 3: Quick check flagged for deeper analysis
        if self.current_features.get('needs_deeper_analysis', False):
            reasons.append("Quick check recommends deeper analysis")
        
        # Condition 4: Some checks failed
        pass_count = self.current_features.get('pass_count', 3)
        if pass_count < 3:
            reasons.append(f"Only {pass_count}/3 quick checks passed")
        
        needs_deeper = len(reasons) > 0
        
        if needs_deeper:
            self._log_decision(
                "deeper_analysis_needed",
                f"Deeper analysis required: {'; '.join(reasons)}",
                self.current_confidence,
                {'reasons': reasons}
            )
        else:
            self._log_decision(
                "skip_deeper_analysis",
                "Basic inspection sufficient, skipping deeper analysis",
                self.current_confidence
            )
        
        return needs_deeper
    
    def _run_deeper_analysis(self, img: np.ndarray):
        """Run deeper analysis tools"""
        self._log_decision("deeper_analysis",
                          "Running deeper structural and symmetry analysis",
                          self.current_confidence)
        
        # Select additional tools based on what's lacking
        tools_to_run = []
        
        # If symmetry not yet computed, add it
        if 'overall_symmetry' not in self.current_features:
            tools_to_run.append("symmetry_analyzer")
        
        # Always run density distribution in deeper analysis
        tools_to_run.append("advanced_density_extractor")
        
        # Structural layer detection
        if 'estimated_wall_thickness' not in self.current_features:
            tools_to_run.append("structural_layer_detector")
        
        for tool_name in tools_to_run:
            result = self._execute_tool(tool_name, img=img)
            if result.success:
                self.current_features.update(result.data)
        
        # Update confidence based on deeper analysis
        self._recalculate_confidence()
    
    def _decide_anomaly_investigation(self) -> bool:
        """
        Decide whether anomaly investigation is needed.
        
        Triggered when:
        - Anomalies detected in basic scan
        - Anomaly severity is borderline
        - High uncertainty about anomaly status
        """
        reasons = []
        
        # Condition 1: Anomaly detected
        has_anomaly = self.current_features.get('has_anomaly', False)
        anomaly_severity = self.current_features.get('anomaly_severity', 0)
        
        if has_anomaly:
            reasons.append("Anomalies detected in basic scan")
            
            # Condition 2: Borderline severity
            threshold = self.quality_thresholds['anomaly_severity_max']
            if 0.5 * threshold < anomaly_severity < 2 * threshold:
                reasons.append(f"Borderline anomaly severity ({anomaly_severity:.3f})")
        
        # Condition 3: Edge defects suspected (low uniformity + asymmetry)
        uniformity = self.current_features.get('uniformity_score', 0)
        symmetry = self.current_features.get('overall_symmetry', 0)
        
        if uniformity < 0.65 and symmetry < 0.7:
            reasons.append("Low uniformity and symmetry suggest potential defects")
        
        needs_investigation = len(reasons) > 0
        
        if needs_investigation:
            self._log_decision(
                "anomaly_investigation_needed",
                f"Anomaly investigation required: {'; '.join(reasons)}",
                self.current_confidence,
                {'reasons': reasons}
            )
        
        return needs_investigation
    
    def _run_anomaly_investigation(self, img: np.ndarray):
        """Run comprehensive anomaly investigation"""
        self._log_decision("anomaly_investigation",
                          "Running deep anomaly scan and edge defect detection",
                          self.current_confidence)
        
        # Deep anomaly scan
        result = self._execute_tool("deep_anomaly_scanner", img=img)
        if result.success:
            self.current_features.update(result.data)
            
            # If deep scan found confidence info, update it
            deep_confidence = result.data.get('deep_scan_confidence', 0)
            if deep_confidence > 0:
                self.current_confidence = max(self.current_confidence, 
                                             deep_confidence * 0.95)
        
        # Edge defect detection
        result = self._execute_tool("edge_defect_detector", img=img)
        if result.success:
            self.current_features.update(result.data)
        
        # Update confidence
        self._recalculate_confidence()
    
    def _run_quality_assessment(self) -> Dict:
        """Run comprehensive quality assessment"""
        self._log_decision("quality_assessment",
                          "Running comprehensive quality assessment",
                          self.current_confidence)
        
        result = self._execute_tool("comprehensive_quality_assessment",
                                    features=self.current_features,
                                    thresholds=self.quality_thresholds)
        
        if result.success:
            self.current_features.update(result.data)
            self.current_confidence = result.data.get('confidence', 0) / 100.0
            return result.data
        
        # Fallback to basic quality calculation
        return self._fallback_quality_assessment()
    
    def _fallback_quality_assessment(self) -> Dict:
        """Fallback quality assessment if main tool fails"""
        quality_score = 100
        factors = []
        reasoning = []
        
        uniformity = self.current_features.get('uniformity_score', 0)
        if uniformity < 0.6:
            quality_score -= 20
            factors.append('low_uniformity')
            reasoning.append(f"⚠️ Low uniformity: {uniformity:.3f}")
        else:
            reasoning.append(f"✓ Good uniformity: {uniformity:.3f}")
        
        if self.current_features.get('has_anomaly', False):
            severity = self.current_features.get('anomaly_severity', 0)
            if severity > 0.02:
                quality_score -= 50
                factors.append('severe_anomaly')
                reasoning.append(f"⚠️ Severe anomaly: {severity:.3f}")
        
        quality_score = max(0, min(100, quality_score))
        
        if quality_score >= 85:
            quality = 'Premium'
        elif quality_score >= 60:
            quality = 'Standard'
        else:
            quality = 'Defective'
        
        return {
            'quality': quality,
            'quality_score': quality_score,
            'confidence': self.current_confidence * 100,
            'decision': f'{quality} Grade',
            'reasoning': reasoning,
            'factors': factors
        }
    
    def _recalculate_confidence(self):
        """Recalculate overall confidence based on current features"""
        # Base confidence from feature clarity
        confidence_factors = []
        
        # Uniformity confidence
        uniformity = self.current_features.get('uniformity_score', 0)
        if uniformity > 0.75:
            confidence_factors.append(0.9)
        elif uniformity > 0.6:
            confidence_factors.append(0.75)
        else:
            confidence_factors.append(0.6)
        
        # Symmetry confidence
        symmetry = self.current_features.get('overall_symmetry', 0)
        if symmetry > 0.75:
            confidence_factors.append(0.9)
        elif symmetry > 0.65:
            confidence_factors.append(0.75)
        else:
            confidence_factors.append(0.6)
        
        # Anomaly detection confidence
        if 'deep_scan_confidence' in self.current_features:
            confidence_factors.append(self.current_features['deep_scan_confidence'])
        elif self.current_features.get('has_anomaly', False):
            severity = self.current_features.get('anomaly_severity', 0)
            if severity > 0.05:
                confidence_factors.append(0.9)  # Clear anomaly
            elif severity > 0.01:
                confidence_factors.append(0.7)  # Borderline
            else:
                confidence_factors.append(0.65)  # Unclear
        else:
            confidence_factors.append(0.8)  # No anomaly detected
        
        # Average with slight boost for more data points
        if len(confidence_factors) > 0:
            base_confidence = sum(confidence_factors) / len(confidence_factors)
            # Boost confidence slightly for having run more tools
            tools_bonus = min(0.05, len(self.tools_used) * 0.01)
            self.current_confidence = min(0.98, base_confidence + tools_bonus)
    
    def _make_final_decision(self, classification: Dict, sample_id: str) -> InspectionResult:
        """
        Make the final decision about the sample.
        
        Determines:
        - Final quality classification
        - Whether human review is needed
        - Suggested actions
        """
        quality = classification.get('quality', 'Unknown')
        quality_score = classification.get('quality_score', 0)
        confidence = classification.get('confidence', 0)
        
        # Determine if human review is needed
        requires_human_review = False
        review_reasons = []
        
        # Check confidence threshold
        if confidence < self.confidence_thresholds['human_review'] * 100:
            requires_human_review = True
            review_reasons.append(f"Low confidence ({confidence:.1f}%)")
        
        # Check for conflicting signals
        factors = classification.get('factors', [])
        if len(factors) >= 3:
            requires_human_review = True
            review_reasons.append(f"Multiple quality factors ({len(factors)})")
        
        # Check for borderline quality score
        if 58 < quality_score < 62 or 83 < quality_score < 87:
            requires_human_review = True
            review_reasons.append("Borderline quality score")
        
        # Edge defects + anomalies = definitely human review
        has_edge_defects = self.current_features.get('has_edge_defects', False)
        has_anomaly = self.current_features.get('has_anomaly', False)
        if has_edge_defects and has_anomaly:
            requires_human_review = True
            review_reasons.append("Both edge defects and anomalies detected")
        
        # Generate decision text
        if requires_human_review:
            decision = f"{quality} Grade (Pending Human Review)"
            self.current_state = AgentState.HUMAN_REVIEW
        else:
            decision = classification.get('decision', f'{quality} Grade')
        
        # Log final decision
        self._log_decision(
            "final_decision",
            f"Final verdict: {decision}" + 
            (f" - Review reasons: {', '.join(review_reasons)}" if review_reasons else ""),
            confidence / 100
        )
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(
            quality, quality_score, confidence, requires_human_review
        )
        
        return InspectionResult(
            sample_id=sample_id,
            quality=quality,
            quality_score=quality_score,
            confidence=confidence,
            decision=decision,
            reasoning=classification.get('reasoning', []),
            tools_used=self.tools_used.copy(),
            execution_history=self.execution_history.copy(),
            requires_human_review=requires_human_review,
            suggested_actions=suggested_actions
        )
    
    def _generate_suggested_actions(self, quality: str, score: float, 
                                    confidence: float, needs_review: bool) -> List[str]:
        """Generate suggested next actions based on results"""
        actions = []
        
        if needs_review:
            actions.append("🔍 Submit for human expert review")
            actions.append("📸 Capture additional images from different angles")
        
        if quality == 'Premium':
            actions.append("✅ Approve for market release")
            actions.append("📦 Route to premium packaging line")
        elif quality == 'Standard':
            actions.append("📋 Route to secondary processing")
            actions.append("🔄 Consider re-inspection after processing")
        else:
            actions.append("❌ Reject and quarantine")
            actions.append("📊 Log for defect analysis statistics")
            actions.append("🔬 Consider sampling for root cause analysis")
        
        if confidence < 70:
            actions.append("⚙️ Consider threshold calibration for this batch")
        
        return actions
    
    def _get_llm_explanation(self, result: InspectionResult) -> Optional[str]:
        """Get LLM-generated explanation if reasoning layer is available"""
        if self.llm_reasoning is None:
            return None
        
        try:
            return self.llm_reasoning.explain_decision(
                features=self.current_features,
                classification={
                    'quality': result.quality,
                    'quality_score': result.quality_score,
                    'confidence': result.confidence,
                    'reasoning': result.reasoning
                },
                tools_used=result.tools_used,
                requires_review=result.requires_human_review
            )
        except Exception as e:
            return f"LLM explanation unavailable: {str(e)}"
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get current confidence level category"""
        if self.current_confidence >= self.confidence_thresholds['high']:
            return ConfidenceLevel.HIGH
        elif self.current_confidence >= self.confidence_thresholds['medium']:
            return ConfidenceLevel.MEDIUM
        elif self.current_confidence >= self.confidence_thresholds['low']:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def print_execution_summary(self):
        """Print a summary of the agent's execution"""
        print("\n" + "=" * 60)
        print("QUALITY CONTROL AGENT - EXECUTION SUMMARY")
        print("=" * 60)
        
        print(f"\nFinal State: {self.current_state.value}")
        print(f"Tools Used ({len(self.tools_used)}): {', '.join(self.tools_used)}")
        print(f"Decisions Made: {len(self.decisions)}")
        print(f"Final Confidence: {self.current_confidence:.2%}")
        
        print("\n📋 Decision Log:")
        for i, decision in enumerate(self.decisions, 1):
            print(f"  {i}. [{decision.action}] {decision.reasoning}")
        
        print("=" * 60 + "\n")
    
    def export_decision_trace(self) -> str:
        """Export the complete decision trace as JSON"""
        trace = {
            'final_state': self.current_state.value,
            'tools_used': self.tools_used,
            'final_confidence': self.current_confidence,
            'decisions': [
                {
                    'action': d.action,
                    'reasoning': d.reasoning,
                    'confidence': d.confidence,
                    'timestamp': d.timestamp,
                    'metadata': d.metadata
                }
                for d in self.decisions
            ],
            'execution_history': self.execution_history,
            'final_features': {k: v for k, v in self.current_features.items() 
                              if not isinstance(v, (np.ndarray, list)) or 
                              (isinstance(v, list) and len(v) < 50)}
        }
        return json.dumps(trace, indent=2, default=str)


def create_agent(confidence_thresholds: Dict = None,
                 quality_thresholds: Dict = None,
                 llm_reasoning: Any = None) -> QualityControlAgent:
    """Factory function to create a configured agent"""
    return QualityControlAgent(
        confidence_thresholds=confidence_thresholds,
        quality_thresholds=quality_thresholds,
        llm_reasoning=llm_reasoning
    )


if __name__ == "__main__":
    # Demo usage
    from data_generator import SyntheticMRIGenerator
    
    # Create agent
    agent = QualityControlAgent()
    
    # Generate sample
    generator = SyntheticMRIGenerator(image_size=256)
    img, metadata = generator.generate_sample(seed=42)
    
    # Inspect
    print("Starting inspection...")
    result = agent.inspect(img, sample_id="demo_sample_001")
    
    # Print results
    print(f"\n{'='*60}")
    print("INSPECTION RESULT")
    print('='*60)
    print(f"Quality: {result.quality}")
    print(f"Score: {result.quality_score:.1f}/100")
    print(f"Confidence: {result.confidence:.1f}%")
    print(f"Decision: {result.decision}")
    print(f"Human Review Required: {result.requires_human_review}")
    print(f"\nTools Used: {', '.join(result.tools_used)}")
    print(f"Total Execution Time: {result.total_execution_time_ms:.2f}ms")
    
    print("\nReasoning:")
    for r in result.reasoning:
        print(f"  • {r}")
    
    print("\nSuggested Actions:")
    for a in result.suggested_actions:
        print(f"  {a}")
    
    # Print execution summary
    agent.print_execution_summary()
