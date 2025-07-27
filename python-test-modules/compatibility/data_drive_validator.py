"""
Data Drive Validator Module

Handles data drive compatibility testing for Enterprise SSD validation.
Test items:
- Direct access Workload
- Filesystem access Workload  
- SW RAID access Workload (RAID 0,1,5,6)
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class WorkloadType(Enum):
    DIRECT_ACCESS = "direct_access"
    FILESYSTEM_ACCESS = "filesystem_access"
    SW_RAID_ACCESS = "sw_raid_access"

class RAIDLevel(Enum):
    RAID_0 = "raid_0"
    RAID_1 = "raid_1" 
    RAID_5 = "raid_5"
    RAID_6 = "raid_6"

@dataclass
class DataDriveTestResult:
    workload_type: WorkloadType
    raid_level: Optional[RAIDLevel]
    test_passed: bool
    throughput_mbps: float
    iops: int
    latency_ms: float
    error_rate: float
    test_duration_seconds: float
    error_message: Optional[str] = None

class DataDriveValidator:
    """Handles data drive compatibility testing for Enterprise SSDs"""
    
    def __init__(self, ssd_devices: List[str], test_config: Dict):
        self.ssd_devices = ssd_devices
        self.test_config = test_config
        self.logger = logging.getLogger(__name__)
        
    async def run_full_data_drive_test_suite(self) -> Dict[str, List[DataDriveTestResult]]:
        """Run complete data drive test suite for all workload types"""
        results = {}
        
        results["direct_access"] = await self.test_direct_access_workload()
        
        results["filesystem_access"] = await self.test_filesystem_access_workload()
        
        results["sw_raid_access"] = await self.test_sw_raid_access_workload()
        
        return results
    
    async def test_direct_access_workload(self) -> List[DataDriveTestResult]:
        """Test direct access to SSD without filesystem layer"""
        self.logger.info("Starting direct access workload test")
        
        results = []
        
        for device in self.ssd_devices:
            try:
                start_time = time.time()
                
                
                await asyncio.sleep(2)  # Simulate test duration
                
                test_duration = time.time() - start_time
                
                result = DataDriveTestResult(
                    workload_type=WorkloadType.DIRECT_ACCESS,
                    raid_level=None,
                    test_passed=True,
                    throughput_mbps=3500.0,  # Simulated throughput
                    iops=450000,  # Simulated IOPS
                    latency_ms=0.08,  # Simulated latency
                    error_rate=0.0,
                    test_duration_seconds=test_duration
                )
                
                results.append(result)
                self.logger.info(f"Direct access test completed for {device}")
                
            except Exception as e:
                self.logger.error(f"Direct access test failed for {device}: {str(e)}")
                results.append(DataDriveTestResult(
                    workload_type=WorkloadType.DIRECT_ACCESS,
                    raid_level=None,
                    test_passed=False,
                    throughput_mbps=0.0,
                    iops=0,
                    latency_ms=0.0,
                    error_rate=1.0,
                    test_duration_seconds=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    async def test_filesystem_access_workload(self) -> List[DataDriveTestResult]:
        """Test filesystem-based access workloads"""
        self.logger.info("Starting filesystem access workload test")
        
        results = []
        filesystems = ["ext4", "xfs", "ntfs"]
        
        for device in self.ssd_devices:
            for fs_type in filesystems:
                try:
                    start_time = time.time()
                    
                    
                    await asyncio.sleep(1.5)  # Simulate test duration
                    
                    test_duration = time.time() - start_time
                    
                    result = DataDriveTestResult(
                        workload_type=WorkloadType.FILESYSTEM_ACCESS,
                        raid_level=None,
                        test_passed=True,
                        throughput_mbps=3200.0,  # Slightly lower due to filesystem overhead
                        iops=420000,
                        latency_ms=0.12,
                        error_rate=0.0,
                        test_duration_seconds=test_duration
                    )
                    
                    results.append(result)
                    self.logger.info(f"Filesystem access test completed for {device} with {fs_type}")
                    
                except Exception as e:
                    self.logger.error(f"Filesystem access test failed for {device} with {fs_type}: {str(e)}")
                    results.append(DataDriveTestResult(
                        workload_type=WorkloadType.FILESYSTEM_ACCESS,
                        raid_level=None,
                        test_passed=False,
                        throughput_mbps=0.0,
                        iops=0,
                        latency_ms=0.0,
                        error_rate=1.0,
                        test_duration_seconds=0.0,
                        error_message=str(e)
                    ))
        
        return results
    
    async def test_sw_raid_access_workload(self) -> List[DataDriveTestResult]:
        """Test software RAID configurations (RAID 0,1,5,6)"""
        self.logger.info("Starting SW RAID access workload test")
        
        results = []
        
        if len(self.ssd_devices) < 2:
            self.logger.warning("Insufficient devices for RAID testing")
            return results
        
        for raid_level in RAIDLevel:
            try:
                min_devices = self._get_min_devices_for_raid(raid_level)
                if len(self.ssd_devices) < min_devices:
                    self.logger.warning(f"Insufficient devices for {raid_level.value} (need {min_devices})")
                    continue
                
                start_time = time.time()
                
                
                await asyncio.sleep(3)  # Simulate RAID test duration
                
                test_duration = time.time() - start_time
                
                throughput, iops, latency = self._get_simulated_raid_performance(raid_level)
                
                result = DataDriveTestResult(
                    workload_type=WorkloadType.SW_RAID_ACCESS,
                    raid_level=raid_level,
                    test_passed=True,
                    throughput_mbps=throughput,
                    iops=iops,
                    latency_ms=latency,
                    error_rate=0.0,
                    test_duration_seconds=test_duration
                )
                
                results.append(result)
                self.logger.info(f"SW RAID test completed for {raid_level.value}")
                
            except Exception as e:
                self.logger.error(f"SW RAID test failed for {raid_level.value}: {str(e)}")
                results.append(DataDriveTestResult(
                    workload_type=WorkloadType.SW_RAID_ACCESS,
                    raid_level=raid_level,
                    test_passed=False,
                    throughput_mbps=0.0,
                    iops=0,
                    latency_ms=0.0,
                    error_rate=1.0,
                    test_duration_seconds=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    def _get_min_devices_for_raid(self, raid_level: RAIDLevel) -> int:
        """Get minimum number of devices required for RAID level"""
        min_devices = {
            RAIDLevel.RAID_0: 2,
            RAIDLevel.RAID_1: 2,
            RAIDLevel.RAID_5: 3,
            RAIDLevel.RAID_6: 4
        }
        return min_devices.get(raid_level, 2)
    
    def _get_simulated_raid_performance(self, raid_level: RAIDLevel) -> tuple[float, int, float]:
        """Get simulated performance metrics for different RAID levels"""
        performance_map = {
            RAIDLevel.RAID_0: (6000.0, 800000, 0.06),  # High performance, no redundancy
            RAIDLevel.RAID_1: (3200.0, 420000, 0.10),  # Mirror performance
            RAIDLevel.RAID_5: (4500.0, 600000, 0.15),  # Good performance with parity
            RAIDLevel.RAID_6: (4000.0, 550000, 0.18)   # Dual parity overhead
        }
        return performance_map.get(raid_level, (3000.0, 400000, 0.20))
    
    def get_test_status(self) -> Dict:
        """Get current test execution status"""
        return {
            "module": "DataDriveValidator",
            "ssd_devices": self.ssd_devices,
            "supported_workloads": [wl.value for wl in WorkloadType],
            "supported_raid_levels": [raid.value for raid in RAIDLevel],
            "status": "ready"
        }
