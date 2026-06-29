# Sample Output — High Vibration Fault

## Input
```json
{
  "machine_id": "Line3-Motor7",
  "vibration_mm_s": 8.3,
  "temp_c": 70
}
```

## Output
```json
{
  "status": "fault_detected",
  "machine_id": "Line3-Motor7",
  "fault_type": "high vibration",
  "occurrence_count": 2,
  "work_order": "WORK ORDER - Line3-Motor7: High Vibration Fault. High vibration detected on Line3-Motor7 (2nd occurrence this month). Immediately measure vibration levels and stop equipment if exceeding 7.5 mm/s RMS per SOP. Inspect bearing housing for excessive heat/noise and verify shaft alignment using laser tool. Escalate to senior technician due to recurring fault pattern and HIGH severity rating; schedule bearing replacement within 48h if issue persists after initial inspection."
}
```
