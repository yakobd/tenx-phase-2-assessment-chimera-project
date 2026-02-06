# Project Chimera — Skills Registry

## Overview
This directory contains modular skill packages for Chimera's FastRender Swarm. Each skill is a self-contained capability with defined input/output contracts, designed to be invoked via MCP.

## Available Skills
| Skill | Owner | Purpose | Status |
|-------|-------|---------|--------|
| [`trend_analyzer`](./trend_analyzer/) | Planner Agent | Fetch and score trends from social sources | Contract Defined ✅ |
| [`video_assembler`](./video_assembler/) | Worker Agent | Assemble video artifacts from assets | Contract Defined ✅ |
| [`safety_judge`](./safety_judge/) | Judge Agent | Validate content safety and enforce governance | Contract Defined ✅ |

## Usage Pattern
All skills are invoked via **MCP envelopes** (`mcp_request`/`mcp_response`) for traceability. Reference individual skill READMEs for:
- JSON input/output schemas
- Pydantic models for validation
- Database integration notes
- Audit requirements

## Development Guide
To implement a skill:
1. **Create Python package** in the skill directory
2. **Implement I/O contract** using the provided Pydantic models
3. **Expose as MCP tool** following Chimera's envelope standards
4. **Add unit tests** for serialization and business logic
5. **Integrate with audit system** via `campaign_metadata` table