"""
Tool Registry for Agentic MRI Inspector
Defines available analysis tools that the Quality Control Agent can select
"""
import numpy as np
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolCategory(Enum):
    """Categories of analysis tools"""
    FEATURE_EXTRACTION = "feature_extraction"
    ANOMALY_DETECTION = "anomaly_detection"
    VISUALIZATION = "visualization"
    REPORTING = "reporting"
    QUALITY_ASSESSMENT = "quality_assessment"


@dataclass
class ToolResult:
    """Result from executing a tool"""
    tool_name: str
    success: bool
    data: Dict[str, Any]
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'data': self.data,
            'execution_time_ms': self.execution_time_ms,
            'error_message': self.error_message
        }


@dataclass
class Tool:
    """Definition of an analysis tool"""
    name: str
    description: str
    category: ToolCategory
    execute_fn: Callable
    requires_image: bool = True
    requires_features: bool = False
    cost: float = 1.0  # Relative computational cost (1.0 = baseline)
    tags: List[str] = field(default_factory=list)
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        import time
        start_time = time.time()
        
        try:
            result_data = self.execute_fn(**kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                data=result_data,
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={},
                execution_time_ms=execution_time,
                error_message=str(e)
            )


class ToolRegistry:
    """
    Registry of all available analysis tools.
    The Quality Control Agent uses this to select which tools to run.
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default analysis tools"""
        
        # ============ FEATURE EXTRACTION TOOLS ============
        
        self.register(Tool(
            name="basic_intensity_extractor",
            description="Extract basic intensity statistics (mean, std, min, max, range)",
            category=ToolCategory.FEATURE_EXTRACTION,
            execute_fn=self._extract_basic_intensity,
            cost=0.5,
            tags=["fast", "baseline", "intensity"]
        ))
        
        self.register(Tool(
            name="advanced_density_extractor",
            description="Compute radial density profiles and distribution metrics",
            category=ToolCategory.FEATURE_EXTRACTION,
            execute_fn=self._extract_density_distribution,
            cost=1.5,
            tags=["density", "radial", "distribution"]
        ))
        
        self.register(Tool(
            name="structural_layer_detector",
            description="Detect distinct layers, wall thickness, and core structures",
            category=ToolCategory.FEATURE_EXTRACTION,
            execute_fn=self._detect_layers,
            cost=2.0,
            tags=["structure", "layers", "wall", "core"]
        ))
        
        self.register(Tool(
            name="symmetry_analyzer",
            description="Compute horizontal, vertical, and overall symmetry scores",
            category=ToolCategory.FEATURE_EXTRACTION,
            execute_fn=self._compute_symmetry,
            cost=1.5,
            tags=["symmetry", "balance", "structure"]
        ))
        
        self.register(Tool(
            name="uniformity_scorer",
            description="Compute uniformity score combining intensity and spatial consistency",
            category=ToolCategory.FEATURE_EXTRACTION,
            execute_fn=self._compute_uniformity,
            cost=1.0,
            tags=["uniformity", "consistency", "quality"]
        ))
        
        # ============ ANOMALY DETECTION TOOLS ============
        
        self.register(Tool(
            name="basic_anomaly_detector",
            description="Detect anomalous regions using intensity deviation (fast)",
            category=ToolCategory.ANOMALY_DETECTION,
            execute_fn=self._detect_anomalies_basic,
            cost=1.0,
            tags=["anomaly", "fast", "baseline"]
        ))
        
        self.register(Tool(
            name="deep_anomaly_scanner",
            description="Deep scan for anomalies with morphological analysis and region properties",
            category=ToolCategory.ANOMALY_DETECTION,
            execute_fn=self._detect_anomalies_deep,
            cost=3.0,
            tags=["anomaly", "deep", "morphology", "comprehensive"]
        ))
        
        self.register(Tool(
            name="edge_defect_detector",
            description="Detect edge irregularities and boundary defects",
            category=ToolCategory.ANOMALY_DETECTION,
            execute_fn=self._detect_edge_defects,
            cost=2.0,
            tags=["edge", "boundary", "defect"]
        ))
        
        # ============ QUALITY ASSESSMENT TOOLS ============
        
        self.register(Tool(
            name="quick_quality_check",
            description="Fast quality assessment using key metrics only",
            category=ToolCategory.QUALITY_ASSESSMENT,
            execute_fn=self._quick_quality_check,
            requires_features=True,
            cost=0.5,
            tags=["fast", "quality", "screening"]
        ))
        
        self.register(Tool(
            name="comprehensive_quality_assessment",
            description="Full quality assessment with all metrics and confidence scoring",
            category=ToolCategory.QUALITY_ASSESSMENT,
            execute_fn=self._comprehensive_quality_assessment,
            requires_features=True,
            cost=2.0,
            tags=["comprehensive", "quality", "confidence"]
        ))
        
        # ============ VISUALIZATION TOOLS ============
        
        self.register(Tool(
            name="generate_heatmap",
            description="Generate intensity heatmap visualization",
            category=ToolCategory.VISUALIZATION,
            execute_fn=self._generate_heatmap,
            cost=1.0,
            tags=["visualization", "heatmap"]
        ))
        
        self.register(Tool(
            name="generate_anomaly_overlay",
            description="Generate visualization with anomaly regions highlighted",
            category=ToolCategory.VISUALIZATION,
            execute_fn=self._generate_anomaly_overlay,
            requires_features=True,
            cost=1.5,
            tags=["visualization", "anomaly", "overlay"]
        ))
        
        # ============ REPORTING TOOLS ============
        
        self.register(Tool(
            name="generate_summary_report",
            description="Generate brief summary report of analysis",
            category=ToolCategory.REPORTING,
            execute_fn=self._generate_summary_report,
            requires_features=True,
            cost=0.5,
            tags=["report", "summary", "fast"]
        ))
        
        self.register(Tool(
            name="generate_detailed_report",
            description="Generate comprehensive detailed analysis report",
            category=ToolCategory.REPORTING,
            execute_fn=self._generate_detailed_report,
            requires_features=True,
            cost=2.0,
            tags=["report", "detailed", "comprehensive"]
        ))
        
        self.register(Tool(
            name="generate_explanation_report",
            description="Generate human-readable explanation of findings and decisions",
            category=ToolCategory.REPORTING,
            execute_fn=self._generate_explanation_report,
            requires_features=True,
            cost=1.5,
            tags=["report", "explanation", "human-readable"]
        ))
    
    def register(self, tool: Tool):
        """Register a new tool"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[ToolCategory] = None, 
                   tags: Optional[List[str]] = None) -> List[Tool]:
        """List all tools, optionally filtered by category or tags"""
        tools = list(self._tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if tags:
            tools = [t for t in tools if any(tag in t.tags for tag in tags)]
        
        return tools
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names"""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if tool is None:
            return ToolResult(
                tool_name=name,
                success=False,
                data={},
                error_message=f"Tool '{name}' not found in registry"
            )
        return tool.execute(**kwargs)
    
    def get_tools_summary(self) -> str:
        """Get a summary of all available tools"""
        lines = ["Available Analysis Tools:", "=" * 50]
        
        for category in ToolCategory:
            tools = self.list_tools(category=category)
            if tools:
                lines.append(f"\n📁 {category.value.upper()}")
                for tool in tools:
                    lines.append(f"  • {tool.name} (cost: {tool.cost})")
                    lines.append(f"    {tool.description}")
        
        return "\n".join(lines)
    
    # ============ TOOL IMPLEMENTATIONS ============
    
    def _extract_basic_intensity(self, img: np.ndarray, **kwargs) -> Dict:
        """Extract basic intensity statistics"""
        return {
            'mean_intensity': float(np.mean(img)),
            'std_intensity': float(np.std(img)),
            'min_intensity': float(np.min(img)),
            'max_intensity': float(np.max(img)),
            'density_range': float(np.ptp(img))
        }
    
    def _extract_density_distribution(self, img: np.ndarray, **kwargs) -> Dict:
        """Compute density distribution metrics"""
        center = np.array(img.shape) // 2
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        distances = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        
        max_dist = np.max(distances)
        n_bins = 20
        radial_profile = []
        
        for i in range(n_bins):
            r_min = (i / n_bins) * max_dist
            r_max = ((i + 1) / n_bins) * max_dist
            mask = (distances >= r_min) & (distances < r_max)
            if mask.sum() > 0:
                radial_profile.append(float(np.mean(img[mask])))
            else:
                radial_profile.append(0.0)
        
        radial_profile = np.array(radial_profile)
        
        return {
            'radial_profile': radial_profile.tolist(),
            'radial_profile_mean': float(np.mean(radial_profile)),
            'radial_profile_std': float(np.std(radial_profile)),
            'radial_gradient': float(np.mean(np.abs(np.diff(radial_profile)))),
            'density_range': float(np.ptp(img))
        }
    
    def _detect_layers(self, img: np.ndarray, **kwargs) -> Dict:
        """Detect distinct layers or shells"""
        thresholds = [0.2, 0.4, 0.6, 0.8]
        layer_areas = []
        
        for thresh in thresholds:
            binary = img > thresh
            layer_areas.append(int(np.sum(binary)))
        
        layer_diffs = np.diff(layer_areas)
        wall_thickness_estimate = float(np.max(np.abs(layer_diffs))) if len(layer_diffs) > 0 else 0.0
        
        center_region = img[img.shape[0]//4:3*img.shape[0]//4, 
                           img.shape[1]//4:3*img.shape[1]//4]
        has_core = bool(np.mean(center_region) < 0.4)
        
        return {
            'estimated_wall_thickness': wall_thickness_estimate / 100,
            'n_distinct_layers': int(len(np.unique(np.digitize(img, thresholds)))),
            'has_core_structure': has_core,
            'core_intensity': float(np.mean(center_region)) if has_core else 0.0,
            'layer_areas': layer_areas
        }
    
    def _compute_symmetry(self, img: np.ndarray, **kwargs) -> Dict:
        """Compute symmetry metrics"""
        # Horizontal symmetry
        left = img[:, :img.shape[1]//2]
        right = np.fliplr(img[:, img.shape[1]//2:])
        min_width = min(left.shape[1], right.shape[1])
        h_symmetry = 1 - np.mean(np.abs(left[:, :min_width] - right[:, :min_width]))
        
        # Vertical symmetry
        top = img[:img.shape[0]//2, :]
        bottom = np.flipud(img[img.shape[0]//2:, :])
        min_height = min(top.shape[0], bottom.shape[0])
        v_symmetry = 1 - np.mean(np.abs(top[:min_height, :] - bottom[:min_height, :]))
        
        return {
            'horizontal_symmetry': float(max(0, h_symmetry)),
            'vertical_symmetry': float(max(0, v_symmetry)),
            'overall_symmetry': float(max(0, (h_symmetry + v_symmetry) / 2))
        }
    
    def _compute_uniformity(self, img: np.ndarray, **kwargs) -> Dict:
        """Compute overall uniformity score"""
        from scipy.ndimage import uniform_filter
        
        intensity_uniformity = 1 - (np.std(img) / (np.mean(img) + 1e-6))
        
        local_mean = uniform_filter(img.astype(float), size=20)
        local_variance = uniform_filter((img - local_mean)**2, size=20)
        spatial_uniformity = 1 - (np.mean(local_variance) / (np.var(img) + 1e-6))
        
        uniformity = (intensity_uniformity + spatial_uniformity) / 2
        uniformity = float(max(0, min(1, uniformity)))
        
        return {
            'uniformity_score': uniformity,
            'intensity_uniformity': float(intensity_uniformity),
            'spatial_uniformity': float(spatial_uniformity)
        }
    
    def _detect_anomalies_basic(self, img: np.ndarray, **kwargs) -> Dict:
        """Basic anomaly detection using intensity deviation"""
        from skimage.measure import label, regionprops
        
        mean_intensity = np.mean(img)
        std_intensity = np.std(img)
        
        anomaly_threshold = mean_intensity - 2 * std_intensity
        anomaly_mask = img < anomaly_threshold
        
        labeled = label(anomaly_mask)
        regions = regionprops(labeled)
        
        has_anomaly = len(regions) > 0
        anomaly_count = len(regions)
        max_anomaly_area = max([r.area for r in regions]) if regions else 0
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_count': anomaly_count,
            'max_anomaly_area': int(max_anomaly_area),
            'anomaly_severity': float(max_anomaly_area / img.size) if has_anomaly else 0.0,
            'anomaly_threshold': float(anomaly_threshold)
        }
    
    def _detect_anomalies_deep(self, img: np.ndarray, **kwargs) -> Dict:
        """Deep anomaly detection with morphological analysis"""
        from skimage.measure import label, regionprops
        from scipy import ndimage
        
        mean_intensity = np.mean(img)
        std_intensity = np.std(img)
        
        # Multi-threshold anomaly detection
        thresholds = [1.5, 2.0, 2.5, 3.0]
        anomaly_levels = {}
        
        for sigma in thresholds:
            anomaly_threshold = mean_intensity - sigma * std_intensity
            anomaly_mask = img < anomaly_threshold
            labeled = label(anomaly_mask)
            regions = regionprops(labeled)
            
            anomaly_levels[f'sigma_{sigma}'] = {
                'count': len(regions),
                'total_area': sum([r.area for r in regions]),
                'max_area': max([r.area for r in regions]) if regions else 0
            }
        
        # Primary detection at 2-sigma
        primary_threshold = mean_intensity - 2 * std_intensity
        primary_mask = img < primary_threshold
        primary_labeled = label(primary_mask)
        primary_regions = regionprops(primary_labeled)
        
        # Morphological analysis of anomalies
        anomaly_details = []
        for region in primary_regions[:10]:  # Limit to top 10 anomalies
            anomaly_details.append({
                'area': int(region.area),
                'centroid': [float(c) for c in region.centroid],
                'eccentricity': float(region.eccentricity) if hasattr(region, 'eccentricity') else 0.0,
                'solidity': float(region.solidity) if hasattr(region, 'solidity') else 0.0
            })
        
        # Calculate composite severity
        has_anomaly = len(primary_regions) > 0
        total_anomaly_area = sum([r.area for r in primary_regions])
        composite_severity = total_anomaly_area / img.size if has_anomaly else 0.0
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_count': len(primary_regions),
            'total_anomaly_area': int(total_anomaly_area),
            'max_anomaly_area': int(max([r.area for r in primary_regions])) if primary_regions else 0,
            'anomaly_severity': float(composite_severity),
            'anomaly_levels': anomaly_levels,
            'anomaly_details': anomaly_details,
            'deep_scan_confidence': 0.95  # Higher confidence from deep scan
        }
    
    def _detect_edge_defects(self, img: np.ndarray, **kwargs) -> Dict:
        """Detect edge irregularities and boundary defects"""
        from scipy import ndimage
        
        # Compute edges
        sobel_x = ndimage.sobel(img, axis=1)
        sobel_y = ndimage.sobel(img, axis=0)
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Find edge variations
        edge_mean = np.mean(edge_magnitude)
        edge_std = np.std(edge_magnitude)
        edge_irregularity = edge_std / (edge_mean + 1e-6)
        
        # Detect boundary
        threshold = np.mean(img) * 0.5
        binary = img > threshold
        
        # Find contour irregularities
        boundary = binary.astype(float) - ndimage.binary_erosion(binary).astype(float)
        boundary_pixels = np.sum(boundary)
        
        # Expected boundary for perfect circle
        expected_boundary = 2 * np.pi * np.sqrt(np.sum(binary) / np.pi)
        boundary_irregularity = abs(boundary_pixels - expected_boundary) / (expected_boundary + 1e-6)
        
        has_edge_defects = boundary_irregularity > 0.2 or edge_irregularity > 0.5
        
        return {
            'has_edge_defects': bool(has_edge_defects),
            'edge_irregularity': float(edge_irregularity),
            'boundary_irregularity': float(boundary_irregularity),
            'edge_magnitude_mean': float(edge_mean),
            'edge_magnitude_std': float(edge_std),
            'boundary_smoothness': float(1.0 - min(1.0, boundary_irregularity))
        }
    
    def _quick_quality_check(self, features: Dict, **kwargs) -> Dict:
        """Fast quality assessment using key metrics"""
        thresholds = kwargs.get('thresholds', {
            'uniformity_min': 0.6,
            'symmetry_min': 0.65,
            'anomaly_severity_max': 0.02
        })
        
        # Quick pass/fail checks
        checks = {
            'uniformity_pass': features.get('uniformity_score', 0) >= thresholds['uniformity_min'],
            'symmetry_pass': features.get('overall_symmetry', 0) >= thresholds['symmetry_min'],
            'no_severe_anomaly': features.get('anomaly_severity', 0) <= thresholds['anomaly_severity_max']
        }
        
        all_pass = all(checks.values())
        pass_count = sum(checks.values())
        
        # Quick quality estimate
        if pass_count == 3:
            quick_quality = "Likely Premium"
            quick_confidence = 0.75
        elif pass_count >= 2:
            quick_quality = "Likely Standard"
            quick_confidence = 0.70
        else:
            quick_quality = "Likely Defective"
            quick_confidence = 0.80
        
        return {
            'quick_quality': quick_quality,
            'quick_confidence': quick_confidence,
            'all_checks_pass': all_pass,
            'pass_count': pass_count,
            'checks': checks,
            'needs_deeper_analysis': not all_pass or quick_confidence < 0.8
        }
    
    def _comprehensive_quality_assessment(self, features: Dict, **kwargs) -> Dict:
        """Full quality assessment with detailed scoring"""
        thresholds = kwargs.get('thresholds', {
            'uniformity_min': 0.6,
            'symmetry_min': 0.65,
            'anomaly_severity_max': 0.02,
            'wall_thickness_min': 0.05,
            'wall_thickness_max': 0.25
        })
        
        quality_score = 100
        factors = []
        reasoning = []
        
        # Rule 1: Anomalies
        if features.get('has_anomaly', False) and features.get('anomaly_severity', 0) > thresholds['anomaly_severity_max']:
            quality_score -= 50
            factors.append('severe_anomaly')
            reasoning.append(f"⚠️ Significant anomaly (severity: {features.get('anomaly_severity', 0):.3f})")
        
        # Rule 2: Uniformity
        uniformity = features.get('uniformity_score', 0)
        if uniformity < thresholds['uniformity_min']:
            quality_score -= 20
            factors.append('low_uniformity')
            reasoning.append(f"⚠️ Low uniformity: {uniformity:.3f}")
        else:
            reasoning.append(f"✓ Good uniformity: {uniformity:.3f}")
        
        # Rule 3: Symmetry
        symmetry = features.get('overall_symmetry', 0)
        if symmetry < thresholds['symmetry_min']:
            quality_score -= 15
            factors.append('asymmetric')
            reasoning.append(f"⚠️ Asymmetric: {symmetry:.3f}")
        else:
            reasoning.append(f"✓ Symmetric: {symmetry:.3f}")
        
        # Rule 4: Wall thickness
        wall = features.get('estimated_wall_thickness', 0)
        if wall < thresholds['wall_thickness_min']:
            quality_score -= 15
            factors.append('thin_wall')
            reasoning.append(f"⚠️ Wall too thin: {wall:.3f}")
        elif wall > thresholds['wall_thickness_max']:
            quality_score -= 10
            factors.append('thick_wall')
            reasoning.append(f"⚠️ Wall too thick: {wall:.3f}")
        else:
            reasoning.append(f"✓ Optimal wall: {wall:.3f}")
        
        # Rule 5: Core structure
        if features.get('has_core_structure', False):
            if features.get('core_intensity', 1) < 0.35:
                quality_score += 5
                reasoning.append("✓ Well-formed core")
            else:
                quality_score -= 5
                reasoning.append("⚠️ Irregular core")
        
        quality_score = max(0, min(100, quality_score))
        
        # Determine quality category
        if quality_score >= 85 and 'severe_anomaly' not in factors:
            quality = 'Premium'
            decision = 'Premium Grade - Proceed to market'
        elif quality_score >= 60 and 'severe_anomaly' not in factors:
            quality = 'Standard'
            decision = 'Standard Grade - Secondary processing'
        else:
            quality = 'Defective'
            decision = 'Reject - Quality control failure'
        
        # Calculate confidence
        confidence = self._calculate_classification_confidence(features, factors)
        
        return {
            'quality': quality,
            'quality_score': quality_score,
            'confidence': confidence,
            'decision': decision,
            'reasoning': reasoning,
            'factors': factors,
            'comprehensive_assessment': True
        }
    
    def _calculate_classification_confidence(self, features: Dict, factors: List[str]) -> float:
        """Calculate classification confidence"""
        confidence = 90.0
        
        uniformity = features.get('uniformity_score', 0)
        symmetry = features.get('overall_symmetry', 0)
        
        # Edge cases reduce confidence
        if 0.55 < uniformity < 0.65:
            confidence -= 10
        if 0.60 < symmetry < 0.70:
            confidence -= 10
        
        # Clear cases increase confidence
        if features.get('has_anomaly', False) and features.get('anomaly_severity', 0) > 0.05:
            confidence = min(95, confidence + 5)
        if uniformity > 0.80:
            confidence = min(98, confidence + 5)
        
        # Conflicting signals reduce confidence
        if len(factors) >= 3:
            confidence -= 10
        
        return max(60, min(98, confidence))
    
    def _generate_heatmap(self, img: np.ndarray, **kwargs) -> Dict:
        """Generate heatmap data"""
        return {
            'heatmap_data': img.tolist(),
            'colormap': 'viridis',
            'description': 'Intensity heatmap of MRI cross-section'
        }
    
    def _generate_anomaly_overlay(self, img: np.ndarray, features: Dict, **kwargs) -> Dict:
        """Generate anomaly overlay visualization data"""
        from skimage.measure import label
        
        mean_intensity = np.mean(img)
        std_intensity = np.std(img)
        anomaly_threshold = mean_intensity - 2 * std_intensity
        anomaly_mask = img < anomaly_threshold
        
        labeled = label(anomaly_mask)
        
        return {
            'base_image': img.tolist(),
            'anomaly_mask': anomaly_mask.tolist(),
            'labeled_regions': labeled.tolist(),
            'anomaly_count': int(np.max(labeled)),
            'description': 'MRI with anomaly regions highlighted'
        }
    
    def _generate_summary_report(self, features: Dict, classification: Dict = None, **kwargs) -> Dict:
        """Generate brief summary report"""
        lines = [
            "=" * 40,
            "MRI ANALYSIS SUMMARY",
            "=" * 40,
            f"Uniformity: {features.get('uniformity_score', 0):.3f}",
            f"Symmetry: {features.get('overall_symmetry', 0):.3f}",
            f"Anomaly Detected: {features.get('has_anomaly', False)}",
        ]
        
        if classification:
            lines.extend([
                "",
                f"Quality: {classification.get('quality', 'Unknown')}",
                f"Score: {classification.get('quality_score', 0):.1f}/100",
                f"Confidence: {classification.get('confidence', 0):.1f}%"
            ])
        
        lines.append("=" * 40)
        
        return {
            'report_text': "\n".join(lines),
            'report_type': 'summary'
        }
    
    def _generate_detailed_report(self, features: Dict, classification: Dict = None, 
                                   metadata: Dict = None, **kwargs) -> Dict:
        """Generate comprehensive detailed report"""
        lines = [
            "=" * 60,
            "COMPREHENSIVE MRI QUALITY INSPECTION REPORT",
            "=" * 60,
            "",
            "[INTENSITY STATISTICS]",
            f"  Mean: {features.get('mean_intensity', 0):.3f}",
            f"  Std Dev: {features.get('std_intensity', 0):.3f}",
            f"  Range: {features.get('density_range', 0):.3f}",
            "",
            "[STRUCTURAL FEATURES]",
            f"  Wall Thickness: {features.get('estimated_wall_thickness', 0):.3f}",
            f"  Distinct Layers: {features.get('n_distinct_layers', 0)}",
            f"  Has Core: {features.get('has_core_structure', False)}",
            "",
            "[SYMMETRY ANALYSIS]",
            f"  Horizontal: {features.get('horizontal_symmetry', 0):.3f}",
            f"  Vertical: {features.get('vertical_symmetry', 0):.3f}",
            f"  Overall: {features.get('overall_symmetry', 0):.3f}",
            "",
            "[ANOMALY DETECTION]",
            f"  Anomalies: {features.get('has_anomaly', False)}",
            f"  Count: {features.get('anomaly_count', 0)}",
            f"  Severity: {features.get('anomaly_severity', 0):.3f}",
            "",
            "[QUALITY METRICS]",
            f"  Uniformity Score: {features.get('uniformity_score', 0):.3f}",
        ]
        
        if classification:
            lines.extend([
                "",
                "[CLASSIFICATION]",
                f"  Quality: {classification.get('quality', 'Unknown')}",
                f"  Score: {classification.get('quality_score', 0):.1f}/100",
                f"  Confidence: {classification.get('confidence', 0):.1f}%",
                f"  Decision: {classification.get('decision', 'N/A')}",
                "",
                "[REASONING]"
            ])
            for i, reason in enumerate(classification.get('reasoning', []), 1):
                lines.append(f"  {i}. {reason}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return {
            'report_text': "\n".join(lines),
            'report_type': 'detailed'
        }
    
    def _generate_explanation_report(self, features: Dict, classification: Dict = None, **kwargs) -> Dict:
        """Generate human-readable explanation of findings"""
        lines = [
            "=" * 60,
            "ANALYSIS EXPLANATION REPORT",
            "=" * 60,
            ""
        ]
        
        # Explain findings in plain language
        uniformity = features.get('uniformity_score', 0)
        symmetry = features.get('overall_symmetry', 0)
        has_anomaly = features.get('has_anomaly', False)
        anomaly_severity = features.get('anomaly_severity', 0)
        
        lines.append("📊 WHAT WE FOUND:")
        lines.append("")
        
        # Uniformity explanation
        if uniformity > 0.75:
            lines.append("✓ The sample shows excellent uniformity, indicating consistent")
            lines.append("  internal structure throughout the cross-section.")
        elif uniformity > 0.6:
            lines.append("• The sample shows acceptable uniformity. Some variations in")
            lines.append("  internal structure are present but within normal limits.")
        else:
            lines.append("⚠️ The sample shows low uniformity, suggesting inconsistent")
            lines.append("  internal structure that may indicate quality issues.")
        lines.append("")
        
        # Symmetry explanation
        if symmetry > 0.75:
            lines.append("✓ The sample demonstrates high structural symmetry,")
            lines.append("  typical of healthy, well-formed specimens.")
        elif symmetry > 0.65:
            lines.append("• The sample shows moderate symmetry. Minor asymmetries")
            lines.append("  are present but may not affect overall quality.")
        else:
            lines.append("⚠️ Significant asymmetry detected. This could indicate")
            lines.append("  developmental irregularities or structural defects.")
        lines.append("")
        
        # Anomaly explanation
        if has_anomaly and anomaly_severity > 0.02:
            lines.append(f"⚠️ Anomalous regions detected (severity: {anomaly_severity:.3f})")
            lines.append("  These areas show unusual intensity patterns that may")
            lines.append("  indicate defects, voids, or other structural issues.")
        elif has_anomaly:
            lines.append("• Minor anomalies detected but within acceptable limits.")
            lines.append("  These are unlikely to affect overall quality classification.")
        else:
            lines.append("✓ No significant anomalies detected in the sample.")
        lines.append("")
        
        # Classification explanation
        if classification:
            quality = classification.get('quality', 'Unknown')
            confidence = classification.get('confidence', 0)
            
            lines.append("🎯 CLASSIFICATION DECISION:")
            lines.append("")
            lines.append(f"Quality Grade: {quality}")
            lines.append(f"Classification Confidence: {confidence:.1f}%")
            lines.append("")
            
            if quality == 'Premium':
                lines.append("This sample meets all criteria for premium quality.")
                lines.append("It can proceed directly to market without additional processing.")
            elif quality == 'Standard':
                lines.append("This sample meets minimum quality standards but shows")
                lines.append("some areas of concern. It may benefit from secondary processing.")
            else:
                lines.append("This sample does not meet quality standards and should")
                lines.append("be rejected or flagged for detailed human review.")
            
            lines.append("")
            
            # Confidence explanation
            if confidence < 75:
                lines.append("⚠️ Note: Classification confidence is relatively low.")
                lines.append("Human review is recommended for this sample.")
        
        lines.append("")
        lines.append("=" * 60)
        
        return {
            'report_text': "\n".join(lines),
            'report_type': 'explanation'
        }


# Module-level instance for convenience
_default_registry = None

def get_default_registry() -> ToolRegistry:
    """Get the default tool registry instance"""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry


if __name__ == "__main__":
    # Demo usage
    registry = ToolRegistry()
    print(registry.get_tools_summary())
    
    # Test with a sample image
    import numpy as np
    sample_img = np.random.rand(256, 256)
    
    # Execute some tools
    result = registry.execute_tool("basic_intensity_extractor", img=sample_img)
    print(f"\nTool result: {result.tool_name}")
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    print(f"Data: {result.data}")
