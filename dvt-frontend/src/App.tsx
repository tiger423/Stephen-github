import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Play, 
  Settings, 
  Monitor,
  HardDrive,
  Shield,
  Award,
  AlertCircle
} from 'lucide-react'

interface TestResult {
  test_id: string
  test_category: string
  test_type: string
  status: string
  start_time: string
  end_time?: string
  results: any
  error_message?: string
}

interface TestConfig {
  ssd_device_path: string
  ssd_devices?: string[]
  test_parameters: Record<string, any>
}

function App() {
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [activeTests, setActiveTests] = useState<Set<string>>(new Set())
  const [testConfig, setTestConfig] = useState<TestConfig>({
    ssd_device_path: '/dev/nvme0n1',
    ssd_devices: ['/dev/nvme0n1', '/dev/nvme1n1'],
    test_parameters: {}
  })

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    const ws = new WebSocket(`${API_BASE.replace('http', 'ws')}/ws`)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('WebSocket message:', data)
      
      if (data.type === 'test_started') {
        setActiveTests(prev => new Set([...prev, data.test_id]))
      } else if (data.type === 'test_completed' || data.type === 'test_failed') {
        setActiveTests(prev => {
          const newSet = new Set(prev)
          newSet.delete(data.test_id)
          return newSet
        })
        fetchTestResults()
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    fetchTestResults()
    
    return () => {
      ws.close()
    }
  }, [])

  const fetchTestResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/test-results`)
      const results = await response.json()
      setTestResults(results)
    } catch (error) {
      console.error('Failed to fetch test results:', error)
    }
  }

  const runTest = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/compatibility/${testType}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_category: 'compatibility',
          test_type: testType,
          config: testConfig
        })
      })
      
      const result = await response.json()
      console.log(`${testType} test started:`, result)
    } catch (error) {
      console.error(`Failed to start ${testType} test:`, error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'running':
        return <Clock className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      completed: "default",
      failed: "destructive", 
      running: "secondary"
    }
    return <Badge variant={variants[status] || "outline"}>{status}</Badge>
  }

  const compatibilityTests = [
    {
      id: 'boot-drive',
      title: 'Boot Drive Testing',
      description: 'OS install & booting (Ubuntu, CentOS, Windows 2019), Usability testing',
      icon: <Monitor className="h-6 w-6" />,
      details: [
        'OS Installation Testing',
        'Boot Time Measurement', 
        'OS Command Usability',
        'Multi-OS Compatibility'
      ]
    },
    {
      id: 'data-drive',
      title: 'Data Drive Validation',
      description: 'Direct access, Filesystem access, SW RAID workloads (RAID 0,1,5,6)',
      icon: <HardDrive className="h-6 w-6" />,
      details: [
        'Direct Access Workload',
        'Filesystem Access Testing',
        'Software RAID Validation',
        'Performance Benchmarking'
      ]
    },
    {
      id: 'system-robustness',
      title: 'System Robustness',
      description: 'Power cycles, IPMI, resets, SMBus monitoring, Quarch testing, NVMe-MI',
      icon: <Shield className="h-6 w-6" />,
      details: [
        'AC Power Cycle Testing',
        'IPMI Power Management',
        'Reset Sequence Testing',
        'Hot Swap & Glitch Testing'
      ]
    },
    {
      id: 'certification',
      title: 'Certification Testing',
      description: 'Intel VROC, WHQL, Windows NVMe Driver, ESXi VMD Driver, UEFI 2.7',
      icon: <Award className="h-6 w-6" />,
      details: [
        'Intel VROC Certification',
        'WHQL Compliance',
        'Driver Compatibility',
        'UEFI 2.7 Validation'
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Enterprise SSD DVT Framework
          </h1>
          <p className="text-gray-600">
            Compatibility Testing Dashboard - Boot Drive, Data Drive, System Robustness & Certification
          </p>
        </div>

        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="dashboard">Test Dashboard</TabsTrigger>
            <TabsTrigger value="results">Test Results</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {compatibilityTests.map((test) => {
                const isRunning = Array.from(activeTests).some(testId => testId.includes(test.id.replace('-', '_')))
                const latestResult = testResults
                  .filter(r => r.test_type === test.id.replace('-', '_'))
                  .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())[0]

                return (
                  <Card key={test.id} className="relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {test.icon}
                          <div>
                            <CardTitle className="text-lg">{test.title}</CardTitle>
                            <CardDescription className="text-sm">
                              {test.description}
                            </CardDescription>
                          </div>
                        </div>
                        {latestResult && getStatusIcon(latestResult.status)}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        {test.details.map((detail, index) => (
                          <div key={index} className="flex items-center text-sm text-gray-600">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                            {detail}
                          </div>
                        ))}
                      </div>
                      
                      {latestResult && (
                        <div className="flex items-center justify-between pt-2 border-t">
                          <span className="text-sm text-gray-500">
                            Last run: {new Date(latestResult.start_time).toLocaleString()}
                          </span>
                          {getStatusBadge(latestResult.status)}
                        </div>
                      )}
                      
                      <Button 
                        onClick={() => runTest(test.id)}
                        disabled={isRunning}
                        className="w-full"
                      >
                        {isRunning ? (
                          <>
                            <Clock className="mr-2 h-4 w-4 animate-spin" />
                            Running Test...
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-4 w-4" />
                            Run Test
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {activeTests.size > 0 && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Tests Running</AlertTitle>
                <AlertDescription>
                  {activeTests.size} test(s) currently executing. Results will update automatically.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Test Results History</CardTitle>
                <CardDescription>
                  View detailed results from all compatibility tests
                </CardDescription>
              </CardHeader>
              <CardContent>
                {testResults.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No test results available. Run some tests to see results here.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {testResults.map((result) => (
                      <div key={result.test_id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            {getStatusIcon(result.status)}
                            <div>
                              <h3 className="font-medium">{result.test_type.replace('_', ' ').toUpperCase()}</h3>
                              <p className="text-sm text-gray-500">
                                Started: {new Date(result.start_time).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          {getStatusBadge(result.status)}
                        </div>
                        
                        {result.error_message && (
                          <Alert className="mt-2">
                            <XCircle className="h-4 w-4" />
                            <AlertTitle>Error</AlertTitle>
                            <AlertDescription>{result.error_message}</AlertDescription>
                          </Alert>
                        )}
                        
                        {result.results && Object.keys(result.results).length > 0 && (
                          <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(result.results, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="config" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Test Configuration</CardTitle>
                <CardDescription>
                  Configure SSD devices and test parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ssd-device">Primary SSD Device Path</Label>
                  <Input
                    id="ssd-device"
                    value={testConfig.ssd_device_path}
                    onChange={(e) => setTestConfig(prev => ({
                      ...prev,
                      ssd_device_path: e.target.value
                    }))}
                    placeholder="/dev/nvme0n1"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="ssd-devices">Additional SSD Devices (for RAID testing)</Label>
                  <Input
                    id="ssd-devices"
                    value={testConfig.ssd_devices?.join(', ') || ''}
                    onChange={(e) => setTestConfig(prev => ({
                      ...prev,
                      ssd_devices: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }))}
                    placeholder="/dev/nvme0n1, /dev/nvme1n1"
                  />
                </div>
                
                <Alert>
                  <Settings className="h-4 w-4" />
                  <AlertTitle>Configuration Note</AlertTitle>
                  <AlertDescription>
                    Ensure SSD device paths are correct and accessible. RAID testing requires multiple devices.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
