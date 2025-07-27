from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
import logging
import sys
import os
from datetime import datetime

from .compatibility import (
    BootDriveTester, 
    DataDriveValidator, 
    SystemRobustnessTester, 
    CertificationManager
)

app = FastAPI(title="Enterprise SSD DVT Framework", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_results_db = {}
active_connections: List[WebSocket] = []

class TestConfig(BaseModel):
    ssd_device_path: str
    ssd_devices: Optional[List[str]] = None
    test_parameters: Dict = {}

class TestExecutionRequest(BaseModel):
    test_category: str
    test_type: str
    config: TestConfig

class TestResult(BaseModel):
    test_id: str
    test_category: str
    test_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: Dict = {}
    error_message: Optional[str] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/compatibility/status")
async def get_compatibility_status():
    """Get status of all compatibility test modules"""
    return {
        "boot_drive": {"status": "ready", "module": "BootDriveTester"},
        "data_drive": {"status": "ready", "module": "DataDriveValidator"},
        "system_robustness": {"status": "ready", "module": "SystemRobustnessTester"},
        "certification": {"status": "ready", "module": "CertificationManager"}
    }

@app.post("/api/compatibility/boot-drive/test")
async def run_boot_drive_test(request: TestExecutionRequest):
    """Execute boot drive compatibility test"""
    test_id = f"boot_drive_{datetime.now().isoformat()}"
    
    try:
        test_result = TestResult(
            test_id=test_id,
            test_category="compatibility",
            test_type="boot_drive",
            status="running",
            start_time=datetime.now()
        )
        test_results_db[test_id] = test_result
        
        await manager.broadcast(json.dumps({
            "type": "test_started",
            "test_id": test_id,
            "test_type": "boot_drive"
        }))
        
        asyncio.create_task(execute_boot_drive_test(test_id, request.config))
        
        return {"test_id": test_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start boot drive test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compatibility/data-drive/test")
async def run_data_drive_test(request: TestExecutionRequest):
    """Execute data drive compatibility test"""
    test_id = f"data_drive_{datetime.now().isoformat()}"
    
    try:
        test_result = TestResult(
            test_id=test_id,
            test_category="compatibility",
            test_type="data_drive",
            status="running",
            start_time=datetime.now()
        )
        test_results_db[test_id] = test_result
        
        await manager.broadcast(json.dumps({
            "type": "test_started",
            "test_id": test_id,
            "test_type": "data_drive"
        }))
        
        asyncio.create_task(execute_data_drive_test(test_id, request.config))
        
        return {"test_id": test_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start data drive test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compatibility/system-robustness/test")
async def run_system_robustness_test(request: TestExecutionRequest):
    """Execute system robustness compatibility test"""
    test_id = f"system_robustness_{datetime.now().isoformat()}"
    
    try:
        test_result = TestResult(
            test_id=test_id,
            test_category="compatibility",
            test_type="system_robustness",
            status="running",
            start_time=datetime.now()
        )
        test_results_db[test_id] = test_result
        
        await manager.broadcast(json.dumps({
            "type": "test_started",
            "test_id": test_id,
            "test_type": "system_robustness"
        }))
        
        asyncio.create_task(execute_system_robustness_test(test_id, request.config))
        
        return {"test_id": test_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start system robustness test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compatibility/certification/test")
async def run_certification_test(request: TestExecutionRequest):
    """Execute certification compatibility test"""
    test_id = f"certification_{datetime.now().isoformat()}"
    
    try:
        test_result = TestResult(
            test_id=test_id,
            test_category="compatibility",
            test_type="certification",
            status="running",
            start_time=datetime.now()
        )
        test_results_db[test_id] = test_result
        
        await manager.broadcast(json.dumps({
            "type": "test_started",
            "test_id": test_id,
            "test_type": "certification"
        }))
        
        asyncio.create_task(execute_certification_test(test_id, request.config))
        
        return {"test_id": test_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start certification test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-results/{test_id}")
async def get_test_result(test_id: str):
    """Get test result by ID"""
    if test_id not in test_results_db:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    return test_results_db[test_id]

@app.get("/api/test-results")
async def get_all_test_results():
    """Get all test results"""
    return list(test_results_db.values())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def execute_boot_drive_test(test_id: str, config: TestConfig):
    """Execute boot drive test in background"""
    try:
        tester = BootDriveTester(config.ssd_device_path, config.test_parameters)
        results = await tester.run_full_boot_test_suite()
        
        test_result = test_results_db[test_id]
        test_result.status = "completed"
        test_result.end_time = datetime.now()
        test_result.results = {
            os_type: {
                "install_success": result.install_success,
                "boot_success": result.boot_success,
                "boot_time_seconds": result.boot_time_seconds,
                "usability_test_passed": result.usability_test_passed,
                "error_message": result.error_message
            }
            for os_type, result in results.items()
        }
        
        await manager.broadcast(json.dumps({
            "type": "test_completed",
            "test_id": test_id,
            "test_type": "boot_drive",
            "results": test_result.results
        }))
        
    except Exception as e:
        logger.error(f"Boot drive test {test_id} failed: {str(e)}")
        test_result = test_results_db[test_id]
        test_result.status = "failed"
        test_result.end_time = datetime.now()
        test_result.error_message = str(e)
        
        await manager.broadcast(json.dumps({
            "type": "test_failed",
            "test_id": test_id,
            "test_type": "boot_drive",
            "error": str(e)
        }))

async def execute_data_drive_test(test_id: str, config: TestConfig):
    """Execute data drive test in background"""
    try:
        devices = config.ssd_devices or [config.ssd_device_path]
        validator = DataDriveValidator(devices, config.test_parameters)
        results = await validator.run_full_data_drive_test_suite()
        
        test_result = test_results_db[test_id]
        test_result.status = "completed"
        test_result.end_time = datetime.now()
        test_result.results = {
            workload_type: [
                {
                    "workload_type": result.workload_type.value,
                    "raid_level": result.raid_level.value if result.raid_level else None,
                    "test_passed": result.test_passed,
                    "throughput_mbps": result.throughput_mbps,
                    "iops": result.iops,
                    "latency_ms": result.latency_ms,
                    "error_rate": result.error_rate,
                    "test_duration_seconds": result.test_duration_seconds,
                    "error_message": result.error_message
                }
                for result in workload_results
            ]
            for workload_type, workload_results in results.items()
        }
        
        await manager.broadcast(json.dumps({
            "type": "test_completed",
            "test_id": test_id,
            "test_type": "data_drive",
            "results": test_result.results
        }))
        
    except Exception as e:
        logger.error(f"Data drive test {test_id} failed: {str(e)}")
        test_result = test_results_db[test_id]
        test_result.status = "failed"
        test_result.end_time = datetime.now()
        test_result.error_message = str(e)
        
        await manager.broadcast(json.dumps({
            "type": "test_failed",
            "test_id": test_id,
            "test_type": "data_drive",
            "error": str(e)
        }))

async def execute_system_robustness_test(test_id: str, config: TestConfig):
    """Execute system robustness test in background"""
    try:
        tester = SystemRobustnessTester(config.ssd_device_path, config.test_parameters)
        results = await tester.run_full_robustness_test_suite()
        
        test_result = test_results_db[test_id]
        test_result.status = "completed"
        test_result.end_time = datetime.now()
        test_result.results = {
            test_type: {
                "test_type": result.test_type.value,
                "test_passed": result.test_passed,
                "recovery_time_seconds": result.recovery_time_seconds,
                "data_integrity_maintained": result.data_integrity_maintained,
                "device_functional_after_test": result.device_functional_after_test,
                "cycle_count": result.cycle_count,
                "error_message": result.error_message
            }
            for test_type, result in results.items()
        }
        
        await manager.broadcast(json.dumps({
            "type": "test_completed",
            "test_id": test_id,
            "test_type": "system_robustness",
            "results": test_result.results
        }))
        
    except Exception as e:
        logger.error(f"System robustness test {test_id} failed: {str(e)}")
        test_result = test_results_db[test_id]
        test_result.status = "failed"
        test_result.end_time = datetime.now()
        test_result.error_message = str(e)
        
        await manager.broadcast(json.dumps({
            "type": "test_failed",
            "test_id": test_id,
            "test_type": "system_robustness",
            "error": str(e)
        }))

async def execute_certification_test(test_id: str, config: TestConfig):
    """Execute certification test in background"""
    try:
        manager_instance = CertificationManager(config.ssd_device_path, config.test_parameters)
        results = await manager_instance.run_full_certification_test_suite()
        
        test_result = test_results_db[test_id]
        test_result.status = "completed"
        test_result.end_time = datetime.now()
        test_result.results = {
            cert_type: {
                "certification_type": result.certification_type.value,
                "test_passed": result.test_passed,
                "certification_version": result.certification_version,
                "compliance_level": result.compliance_level,
                "test_duration_seconds": result.test_duration_seconds,
                "issues_found": result.issues_found,
                "recommendations": result.recommendations,
                "error_message": result.error_message
            }
            for cert_type, result in results.items()
        }
        
        await manager.broadcast(json.dumps({
            "type": "test_completed",
            "test_id": test_id,
            "test_type": "certification",
            "results": test_result.results
        }))
        
    except Exception as e:
        logger.error(f"Certification test {test_id} failed: {str(e)}")
        test_result = test_results_db[test_id]
        test_result.status = "failed"
        test_result.end_time = datetime.now()
        test_result.error_message = str(e)
        
        await manager.broadcast(json.dumps({
            "type": "test_failed",
            "test_id": test_id,
            "test_type": "certification",
            "error": str(e)
        }))
