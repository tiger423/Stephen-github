# Enterprise SSD DVT Test Framework

A comprehensive test management framework for Enterprise SSD Design Verification Testing (DVT).

## Architecture

- **Top Level**: Node.js web platform with React frontend
- **Second Level**: Python test execution modules
- **Database**: PostgreSQL for production, SQLite for development

## Test Categories

Based on the Enterprise SSD DVT test plan-v01.xlsx:

1. **Data Integrity** - IO Stress testing with Single/Multi Namespace
2. **Robustness** - Reset Handling (SPO/BOOT/NPO/PWRDIS, PERST/NSSR/HOT Reset, FLR/CTRL Reset, Composite POR)
3. **Functionality** - NVMe, OCP, Security, NVMe-MI, SMBus, Time To Ready
4. **Reliability** - RDT, eRDT, 4corner testing, WAF Endurance (RandW.4k, JEDEC)
5. **Compatibility** - Boot Drive, Data Drive, System Robustness, Certification
6. **Compliance** - UNH-IOL, Oakgate DT, Sanblaze Cert, ULINK, Quarch, NVMe-MI, PCIe
7. **Performance/Power** - Synthetic, Real world, and Customer workloads

## Project Structure

```
enterprise-ssd-dvt-framework/
├── web-platform/          # Node.js + React web interface
├── python-test-modules/    # Python test execution modules
├── docs/                   # Documentation
└── README.md
```

## Getting Started

1. Set up the web platform (Node.js + React)
2. Configure Python test modules
3. Initialize database schema
4. Configure test hardware interfaces

## Development

- Web Platform: Node.js + Express + React + TypeScript
- Test Modules: Python 3.12+
- Database: PostgreSQL/SQLite
- Real-time: Socket.IO
