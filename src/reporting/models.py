from dataclasses import dataclass, field


@dataclass
class PytestSummary:
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_seconds: float = 0.0


@dataclass
class DeepEvalMetricResult:
    name: str
    score: float
    threshold: float
    success: bool
    reason: str
    evaluation_model: str | None = None
    evaluation_cost: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass
class DeepEvalTestResult:
    name: str
    success: bool
    actual_output: str
    duration_seconds: float
    evaluation_cost: float | None = None
    metrics: list[DeepEvalMetricResult] = field(default_factory=list)
    trajectory: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    run_id: str
    timestamp: str

    pytest: PytestSummary | None = None
    deepeval: list[DeepEvalTestResult] = field(default_factory=list)

    security_results: dict[str, bool] = field(default_factory=dict)
    performance: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)