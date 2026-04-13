# E14 ORACLE — DEPLOYMENT CHECKLIST

## Phase 0: Understanding ✓ DONE

- [x] E14 is a distributed consensus oracle (NOT a synchronization toy)
- [x] K-score measures system coherence (0.0–1.0)
- [x] Decision windows = periods safe for critical operations
- [x] Drift + Pullback = real-world competing forces
- [x] Operational gain = know when to execute vs. wait

## Phase 1: Calibration (1–2 hours)

### Measurement
- [ ] Run `test_e14_real_world_operational.py` with real engine data
- [ ] Record average K-score from output
- [ ] Record phase error (chaos vs. order measure)
- [ ] Record decision window count and duration
- [ ] Note current operational readiness status

### Parameter Tuning
- [ ] Adjust DRIFT_MAGNITUDE based on actual system
  - Measure: What's your clock sync precision? (NTP, GPS, atomic?)
  - Set to: Measured drift ± 20%
  
- [ ] Adjust PHASE_PULLBACK for control strength
  - Start with: 0.85
  - Target: First decision windows appear
  
- [ ] Adjust K_THRESHOLD_HIGH for decision gate
  - Conservative: 0.90 (rare windows, safe)
  - Balanced: 0.80 (moderate windows)
  - Aggressive: 0.70 (frequent windows, more risk)

### Testing
- [ ] Run 48-hour simulation with each configuration
- [ ] Record K-score distribution
- [ ] Compare decision window counts
- [ ] Pick best configuration that meets operational needs

### Documentation
- [ ] Document final parameters in README
- [ ] Explain why chosen (drift measurement, pullback reasoning)
- [ ] Record expected K-score distribution
- [ ] Record expected decision window frequency

---

## Phase 2: Monitoring Setup (2–4 hours)

### Prometheus Integration
- [ ] Create metrics collector:
  ```python
  k_score_current
  k_score_average (1h window)
  decision_windows_total
  decision_windows_duration_seconds
  phase_error_current
  ```

- [ ] Emit metrics every second:
  ```python
  from prometheus_client import Gauge, Counter
  k_gauge = Gauge('e14_k_score', 'Current K-score')
  window_counter = Counter('e14_decision_windows', 'Decision windows opened')
  ```

### Grafana Dashboard
- [ ] Create dashboard with panels:
  - K-score gauge (0.0–1.0, color zones: red <0.5, yellow 0.5–0.7, green >0.7)
  - K-score history (24h rolling, with threshold lines)
  - Decision windows timeline (when open/closed)
  - Phase error gauge (chaos indicator)
  - Engine count (how many converged per axis)

- [ ] Add alerts:
  - Alert when K-score > 0.90 ("Decision window opening")
  - Alert when K-score < 0.50 ("System diverging")

### Alerting
- [ ] Slack/PagerDuty integration for decision windows
- [ ] Ops team trained: "When K > 0.90, you can execute"

---

## Phase 3: Decision Automation (4–8 hours)

### Decision Execution Framework
- [ ] Create decision executor:
  ```python
  def execute_if_ready(operation, k_score, weather_safe, xyo_valid):
      if k_score >= K_THRESHOLD_HIGH and weather_safe and xyo_valid:
          return execute(operation)
      else:
          return queue_for_next_window(operation)
  ```

- [ ] Integrate with your business logic:
  - Blockchain: "Only finalize block if K >= 0.95"
  - Payment: "Only process transaction if K >= 0.90"
  - Fleet: "Only execute maneuver if K >= 0.90"

### Fallback Policies
- [ ] What happens when K < threshold?
  - Option A: Queue and retry later
  - Option B: Degrade to lower-confidence path
  - Option C: Escalate to human decision
  - Option D: Fail safely and abort

- [ ] Timeout policies:
  - "Wait max 5 minutes for K > 0.90"
  - "If timeout, execute with K >= 0.70"
  - "Log why fallback was used"

### Audit & Logging
- [ ] Log every execution with:
  ```python
  {
      "timestamp": "2024-01-15T12:34:56Z",
      "operation": "finalize_block_123",
      "k_score": 0.9176,
      "weather_safe": true,
      "xyo_valid": true,
      "decision": "EXECUTED",
      "window_id": "w_001_9234",
  }
  ```

- [ ] Retention: Keep 2 years minimum (compliance)

---

## Phase 4: Production Deployment (1 day)

### Docker Containerization
- [ ] Create Dockerfile:
  ```dockerfile
  FROM python:3.11-slim
  COPY test_e14_real_world_operational.py /app/
  COPY engines.yaml /app/
  CMD ["python", "/app/test_e14_real_world_operational.py"]
  ```

- [ ] Build image: `docker build -t e14-oracle:latest .`
- [ ] Push to registry: `docker push registry.example.com/e14-oracle:latest`

### Kubernetes Deployment
- [ ] Create deployment manifest (monitors K-score)
- [ ] Create configmap for parameters (DRIFT, PULLBACK, THRESHOLD)
- [ ] Create service for metrics export
- [ ] Deploy: `kubectl apply -f e14-oracle-deployment.yaml`

### Health Checks
- [ ] Liveness probe: Check if process running
- [ ] Readiness probe: Check if K-score computed (not startup lag)
- [ ] Set resource limits (CPU, memory)

### Networking
- [ ] Expose Prometheus metrics endpoint (:9090)
- [ ] Connect to Prometheus scraper
- [ ] Verify Grafana dashboard receives data

---

## Phase 5: Operational (Ongoing)

### Daily Monitoring
- [ ] Check Grafana dashboard each day
- [ ] Verify K-score distribution matches expectations
- [ ] Monitor decision window frequency
- [ ] Review alerts in Slack/PagerDuty

### Weekly Review
- [ ] Analyze decision audit logs
- [ ] Check for any operation failures
- [ ] Verify XYO witness availability
- [ ] Check weather gate effectiveness

### Monthly Tuning
- [ ] Analyze K-score trends
- [ ] Compare actual drift vs. configured DRIFT_MAGNITUDE
- [ ] Adjust thresholds if needed
- [ ] Review operational readiness metrics

### Incident Response
- [ ] If K-score crashes below 0.3: Investigate system health
- [ ] If decision windows disappear: Check if parameters changed
- [ ] If XYO witness fails: Verify cryptographic infrastructure
- [ ] If phase error grows: Check for clock synchronization issues

---

## Success Criteria

### Phase 1 (Calibration)
- [x] Parameters documented
- [x] K-score distribution understood
- [x] Decision windows appear in simulation

### Phase 2 (Monitoring)
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboard live
- [ ] K-score updating in real-time
- [ ] Alerts firing correctly

### Phase 3 (Automation)
- [ ] Decision executor integrated
- [ ] Fallback policies implemented
- [ ] Audit logging working
- [ ] No missed decision windows

### Phase 4 (Deployment)
- [ ] Docker image deployed
- [ ] Kubernetes pod running
- [ ] Metrics flowing to Prometheus
- [ ] Grafana dashboard accessible

### Phase 5 (Operation)
- [ ] Decision execution rate > 10% (target for your system)
- [ ] Zero unexpected rejections
- [ ] Audit trail complete and reviewed
- [ ] Ops team confident in K-score gates

---

## Rollback Plan

If deployment fails:

1. **Immediate** (rollback to previous)
   ```bash
   kubectl set image deployment/e14-oracle e14=e14-oracle:v1.0
   ```

2. **Short-term** (manual decision making)
   - Disable K-score gating
   - Execute on manual decision
   - Log all decisions
   - Investigate root cause

3. **Investigation**
   - Check: Are parameters wrong?
   - Check: Is infrastructure changed?
   - Check: Is engine count different?
   - Recalibrate if needed

4. **Redeploy**
   - Apply new parameters
   - Test in staging
   - Deploy with monitoring

---

## Training Checklist

### For Operations Team
- [ ] Understand what K-score means
- [ ] Know how to read Grafana dashboard
- [ ] Understand decision windows
- [ ] Know what to do if K < 0.70
- [ ] Know where to find audit logs

### For Engineering Team
- [ ] Understand drift + pullback model
- [ ] Can tune DRIFT_MAGNITUDE and PHASE_PULLBACK
- [ ] Can modify decision executor
- [ ] Can add new decision types
- [ ] Can interpret K-score trends

### For Leadership
- [ ] Understand operational gain (fewer failures)
- [ ] Know improvement over baseline
- [ ] Understand cost (monitoring + compute)
- [ ] Know timeline to production

---

## Estimated Costs

| Phase | Time | Cost | Notes |
|-------|------|------|-------|
| Calibration | 2h | $0 | Laptop time |
| Monitoring | 4h | $500/month | Prometheus + Grafana |
| Automation | 8h | $2k/month | Dev engineer |
| Deployment | 1d | $1k setup | One-time K8s setup |
| Operation | Ongoing | $1k/month | Monitoring + ops time |

**Break-even**: Avoid 1 failed transaction × $10k = 1 month

---

## Go/No-Go Decision

### GO if:
- [ ] K-score in simulation reaches 0.80+
- [ ] Decision windows appear regularly
- [ ] Business case justifies monitoring cost
- [ ] Ops team confident in procedures

### NO-GO if:
- [ ] K-score stays below 0.60 (recalibrate)
- [ ] Decision windows < 1 window per day (not operational)
- [ ] Business case doesn't justify cost (scale down)
- [ ] Infrastructure can't support parameters

---

## Project Sign-off

- [ ] Product: "___ has reviewed and approves"
- [ ] Engineering: "___ has reviewed and approves"
- [ ] Operations: "___ trained and ready"
- [ ] Security: "___ audit completed"
- [ ] Compliance: "___ meets requirements"

**Deploy date**: ___________

**Deployment lead**: ___________

**Escalation contact**: ___________

---

**Use this checklist to track progress from concept to production.**
