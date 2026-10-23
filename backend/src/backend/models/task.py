"""
Sagarvani Reconstructed — Task Harness Schemas
Typed contracts for DAG tasks, handoffs, execution bounds, and outputs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.enums import TaskStatus


class TaskContract(BaseModel):
    """Specification of an acquisition or processing task in the DAG."""
    task_id: str = Field(..., description="Unique task identifier, e.g., task_fetch_marine_weather")
    task_name: str = Field(..., description="Readable task name")
    gateway_id: str = Field(..., description="Target gateway identifier, e.g., open_meteo_marine")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete first")
    timeout_seconds: float = Field(default=10.0, gt=0, description="Task execution timeout in seconds")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Typed arguments for the gateway")


class TaskResult(BaseModel):
    """Execution outcome of a completed or failed task."""
    task_id: str = Field(..., description="Task identifier corresponding to TaskContract")
    status: TaskStatus = Field(..., description="Final status of task execution")
    started_at: datetime = Field(..., description="Timestamp when task began")
    completed_at: datetime = Field(..., description="Timestamp when task ended")
    duration_ms: float = Field(..., ge=0, description="Execution duration in milliseconds")
    evidence_ids: List[str] = Field(default_factory=list, description="Evidence record IDs produced by this task")
    error_message: Optional[str] = Field(default=None, description="Detailed error description if task failed")
    raw_artifact_path: Optional[str] = Field(default=None, description="Path to raw cached payload")
