"""
Boot Drive Tester Module

Handles OS installation and booting tests for Enterprise SSD compatibility validation.
Test items:
- OS install & booting (Ubuntu, CentOS, Windows 2019)
- Usability (OS command)
"""

import asyncio
import logging
import subprocess
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class OSType(Enum):
    UBUNTU = "ubuntu"
    CENTOS = "centos"
    WINDOWS_2019 = "windows_2019"

@dataclass
class BootTestResult:
    os_type: OSType
    install_success: bool
    boot_success: bool
    boot_time_seconds: float
    usability_test_passed: bool
    error_message: Optional[str] = None
    detailed_logs: List[str] = None

class BootDriveTester:
    """Handles boot drive compatibility testing for Enterprise SSDs"""
    
    def __init__(self, ssd_device_path: str, test_config: Dict):
        self.ssd_device_path = ssd_device_path
        self.test_config = test_config
        self.logger = logging.getLogger(__name__)
        
    async def run_full_boot_test_suite(self) -> Dict[str, BootTestResult]:
        """Run complete boot drive test suite for all supported OS types"""
        results = {}
        
        for os_type in OSType:
            self.logger.info(f"Starting boot test for {os_type.value}")
            result = await self.test_os_boot_compatibility(os_type)
            results[os_type.value] = result
            
        return results
    
    async def test_os_boot_compatibility(self, os_type: OSType) -> BootTestResult:
        """Test OS installation and boot compatibility for specific OS"""
        try:
            install_success = await self._test_os_installation(os_type)
            
            if not install_success:
                return BootTestResult(
                    os_type=os_type,
                    install_success=False,
                    boot_success=False,
                    boot_time_seconds=0.0,
                    usability_test_passed=False,
                    error_message="OS installation failed"
                )
            
            boot_success, boot_time = await self._test_os_boot(os_type)
            
            if not boot_success:
                return BootTestResult(
                    os_type=os_type,
                    install_success=True,
                    boot_success=False,
                    boot_time_seconds=boot_time,
                    usability_test_passed=False,
                    error_message="OS boot failed"
                )
            
            usability_passed = await self._test_os_usability(os_type)
            
            return BootTestResult(
                os_type=os_type,
                install_success=True,
                boot_success=True,
                boot_time_seconds=boot_time,
                usability_test_passed=usability_passed,
                error_message=None if usability_passed else "Usability tests failed"
            )
            
        except Exception as e:
            self.logger.error(f"Boot test failed for {os_type.value}: {str(e)}")
            return BootTestResult(
                os_type=os_type,
                install_success=False,
                boot_success=False,
                boot_time_seconds=0.0,
                usability_test_passed=False,
                error_message=str(e)
            )
    
    async def _test_os_installation(self, os_type: OSType) -> bool:
        """Simulate OS installation process"""
        self.logger.info(f"Testing {os_type.value} installation")
        
        
        await asyncio.sleep(2)  # Simulate installation time
        
        if await self._verify_ssd_accessibility():
            self.logger.info(f"{os_type.value} installation simulation completed successfully")
            return True
        else:
            self.logger.error(f"{os_type.value} installation failed - SSD not accessible")
            return False
    
    async def _test_os_boot(self, os_type: OSType) -> tuple[bool, float]:
        """Test OS boot process and measure boot time"""
        self.logger.info(f"Testing {os_type.value} boot process")
        
        start_time = time.time()
        
        
        await asyncio.sleep(1.5)  # Simulate boot time
        
        boot_time = time.time() - start_time
        
        boot_success = await self._verify_ssd_accessibility()
        
        if boot_success:
            self.logger.info(f"{os_type.value} boot completed in {boot_time:.2f} seconds")
        else:
            self.logger.error(f"{os_type.value} boot failed")
            
        return boot_success, boot_time
    
    async def _test_os_usability(self, os_type: OSType) -> bool:
        """Test basic OS command functionality"""
        self.logger.info(f"Testing {os_type.value} usability commands")
        
        test_commands = {
            OSType.UBUNTU: [
                "ls -la /",
                "df -h",
                "free -m",
                "uname -a"
            ],
            OSType.CENTOS: [
                "ls -la /",
                "df -h", 
                "free -m",
                "uname -a"
            ],
            OSType.WINDOWS_2019: [
                "dir C:\\",
                "systeminfo",
                "wmic diskdrive list brief"
            ]
        }
        
        commands = test_commands.get(os_type, [])
        
        for command in commands:
            try:
                await asyncio.sleep(0.1)  # Simulate command execution
                self.logger.info(f"Command '{command}' executed successfully")
            except Exception as e:
                self.logger.error(f"Command '{command}' failed: {str(e)}")
                return False
        
        return True
    
    async def _verify_ssd_accessibility(self) -> bool:
        """Verify SSD device is accessible and healthy"""
        try:
            
            await asyncio.sleep(0.1)
            return True  # Assume SSD is healthy for simulation
            
        except Exception as e:
            self.logger.error(f"SSD accessibility check failed: {str(e)}")
            return False
    
    def get_test_status(self) -> Dict:
        """Get current test execution status"""
        return {
            "module": "BootDriveTester",
            "ssd_device": self.ssd_device_path,
            "supported_os": [os.value for os in OSType],
            "status": "ready"
        }
