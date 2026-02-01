"""
Synthetic MRI Inspector - Agentic Quality Control System

This package provides intelligent, interpretable MRI quality inspection
with dynamic tool selection and LLM-powered reasoning.
"""

from data_generator import SyntheticMRIGenerator
from feature_extractor import FeatureExtractor
from classifier import QualityClassifier
from visualizer import MRIVisualizer
from report_generator import ReportGenerator, BatchReportGenerator
from tool_registry import ToolRegistry, Tool, ToolResult, ToolCategory, get_default_registry
from quality_control_agent import (
    QualityControlAgent, 
    AgentState, 
    ConfidenceLevel,
    InspectionResult,
    create_agent
)
from llm_reasoning import (
    LLMReasoningLayer,
    LLMConfig,
    LLMProvider,
    ReasoningResult,
    create_reasoning_layer
)

__all__ = [
    # Data generation
    'SyntheticMRIGenerator',
    
    # Feature extraction
    'FeatureExtractor',
    
    # Classification
    'QualityClassifier',
    
    # Visualization
    'MRIVisualizer',
    
    # Reporting
    'ReportGenerator',
    'BatchReportGenerator',
    
    # Tool registry (Upgrade 2)
    'ToolRegistry',
    'Tool',
    'ToolResult',
    'ToolCategory',
    'get_default_registry',
    
    # Quality Control Agent (Upgrade 1)
    'QualityControlAgent',
    'AgentState',
    'ConfidenceLevel',
    'InspectionResult',
    'create_agent',
    
    # LLM Reasoning (Upgrade 3)
    'LLMReasoningLayer',
    'LLMConfig',
    'LLMProvider',
    'ReasoningResult',
    'create_reasoning_layer'
]

__version__ = '2.0.0'  # Major version bump for agentic upgrade
