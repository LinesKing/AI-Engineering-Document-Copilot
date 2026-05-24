from __future__ import annotations

from pathlib import Path


DEMO_MANUALS: dict[str, str] = {
    "compressor_maintenance_manual.md": """# Rotary Compressor Maintenance Manual

## Safety Isolation
Before inspection, isolate electrical supply, close inlet and discharge valves, and verify zero stored pressure. Lockout and tagout must be confirmed by the maintenance lead.

## Bearing Temperature Alarm
If bearing temperature exceeds 85 C, reduce load and inspect lubrication flow. If temperature exceeds 95 C, stop the compressor, check oil level, inspect the cooler, and do not restart until vibration is within normal range.

## Oil System Inspection
Inspect oil level every shift. Replace oil filters when differential pressure exceeds 1.5 bar or when oil analysis shows metal contamination. Record oil pressure, oil temperature, and filter differential pressure in the maintenance log.

## Restart Criteria
Restart is permitted only after guards are installed, oil pressure is stable, discharge valve position is confirmed, and vibration remains below 7 mm/s during trial operation.
""",
    "pump_overhaul_guide.md": """# Centrifugal Pump Overhaul Guide

## Seal Leakage
Visible seal leakage above 10 drops per minute requires planned shutdown. Check seal flush pressure, inspect the mechanical seal faces, and verify that the pump is not operating away from best efficiency point.

## Cavitation Symptoms
Noise, fluctuating discharge pressure, and pitted impeller surfaces indicate possible cavitation. Confirm suction strainer condition, suction valve position, net positive suction head margin, and process fluid temperature.

## Alignment Procedure
After coupling removal or motor work, perform laser alignment. Final offset and angular alignment must meet site tolerance before the coupling guard is reinstalled.

## Overhaul Acceptance
The pump may return to service when vibration is below 4.5 mm/s, bearing temperature is stable below 75 C, seal leakage is within tolerance, and discharge pressure matches the operating envelope.
""",
    "conveyor_troubleshooting_notes.md": """# Conveyor Troubleshooting Notes

## Belt Tracking
If the belt tracks toward one side, inspect carry roller condition, pulley lagging, material loading point, and take-up tension. Do not adjust multiple idlers at once; make small adjustments and observe two full belt revolutions.

## Drive Motor Trips
Repeated drive motor trips may indicate overloaded belt, failed bearings, jammed skirt rubber, or incorrect variable speed drive current limit. Check motor current trend before restarting.

## Emergency Stop Reset
After an emergency stop, inspect the pull-wire route, verify the stopped zone is clear, reset field devices, and confirm the control room has acknowledged the restart request.

## Preventive Maintenance
Weekly checks include belt condition, pulley guards, emergency stops, gearbox oil leaks, bearing noise, and housekeeping around transfer points.
""",
}


def create_demo_documents(document_dir: Path) -> list[Path]:
    document_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for filename, content in DEMO_MANUALS.items():
        path = document_dir / filename
        if not path.exists() or path.stat().st_size == 0:
            path.write_text(content, encoding="utf-8")
        created.append(path)
    return created
