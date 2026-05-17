from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GenerateRequest(BaseModel):
    name: str
    runSettings: Dict[str, Any]
    promptSettings: Dict[str, Any]
    testSuiteId: Optional[str] = None
    timeout: Optional[int] = None

class RunRequest(BaseModel):
    buildName: Optional[str] = None
    targets: Optional[List[Dict[str, Any]]] = None
    scTunnelName: Optional[str] = None

class ScheduleRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    testSuiteIds: Optional[List[str]] = None
    stateName: Optional[str] = None
