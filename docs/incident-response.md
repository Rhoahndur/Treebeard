# Incident Response Guide

## Overview

This guide outlines the incident response process for TreeBeard production issues.

## Incident Severity Levels

### Critical (P0)

**Response Time**: Immediate (< 5 minutes)
**Notification**: PagerDuty + Slack
**On-Call**: Required

**Criteria:**
- Complete service outage
- Data loss or corruption
- Security breach
- Error rate > 5%
- API completely unavailable

**Examples:**
- Database down
- All API pods crashed
- Redis unavailable
- Critical security vulnerability

### High (P1)

**Response Time**: < 15 minutes
**Notification**: Slack + Email
**On-Call**: Notified

**Criteria:**
- Partial service degradation
- Important features unavailable
- Performance severely degraded
- Error rate 2-5%

**Examples:**
- Claude API rate limited
- High latency (P95 > 3s)
- Specific endpoints failing
- Cache degraded performance

### Medium (P2)

**Response Time**: < 1 hour
**Notification**: Slack
**On-Call**: Informed

**Criteria:**
- Minor service degradation
- Non-critical features affected
- Performance moderately degraded
- Error rate 1-2%

**Examples:**
- Elevated error rate
- Slow database queries
- Low cache hit rate
- Minor performance issues

### Low (P3)

**Response Time**: Next business day
**Notification**: Email digest
**On-Call**: Not required

**Criteria:**
- Cosmetic issues
- Minimal user impact
- Performance slightly degraded
- Error rate < 1%

**Examples:**
- Single user reports
- UI glitches
- Non-critical warnings
- Minor configuration issues

## Incident Response Process

### 1. Detection & Alerting

**Automated Detection:**
- Monitoring alerts (DataDog, Sentry)
- Health check failures
- Anomaly detection
- Error rate spikes

**Manual Detection:**
- User reports
- Customer support tickets
- Team member observation

### 2. Initial Response (0-5 minutes)

1. **Acknowledge Alert**
   - Acknowledge in PagerDuty
   - Post in #alerts Slack channel
   - Assign incident commander

2. **Initial Assessment**
   - Check dashboards for impact
   - Review recent deployments
   - Check error logs
   - Determine severity

3. **Communication**
   ```
   🚨 INCIDENT DETECTED: [Title]

   Severity: [P0/P1/P2/P3]
   Status: Investigating
   Impact: [Brief description]
   Incident Commander: @[name]

   Initial Actions:
   - [Action 1]
   - [Action 2]

   Updates: Every [X] minutes in this thread.
   ```

### 3. Investigation (5-15 minutes)

1. **Gather Information**
   - Check service health dashboard
   - Review error logs in Sentry
   - Analyze APM traces
   - Check recent changes (deployments, config)
   - Review alert timeline

2. **Identify Root Cause**
   - Use runbooks for common issues
   - Check dependencies (database, cache, external APIs)
   - Review metrics and traces
   - Check infrastructure resources

3. **Document Findings**
   - Update incident ticket
   - Post updates in Slack
   - Note timeline of events

### 4. Mitigation (15-30 minutes)

1. **Immediate Actions**
   - Rollback recent deployment (if applicable)
   - Scale resources (if needed)
   - Enable fallback mode
   - Route traffic away from affected systems

2. **Apply Fix**
   - Deploy hotfix
   - Restart services
   - Clear problematic data
   - Update configuration

3. **Verify Fix**
   - Monitor error rates
   - Check key metrics
   - Test affected functionality
   - Confirm user reports resolved

### 5. Resolution & Recovery

1. **Confirm Resolution**
   - Error rate back to normal
   - Latency within targets
   - All services healthy
   - No new related issues

2. **Communication**
   ```
   ✅ INCIDENT RESOLVED: [Title]

   Duration: [X] minutes
   Root Cause: [Brief explanation]
   Resolution: [What was done]
   Impact: [User/service impact]

   Post-mortem scheduled for: [Date/Time]
   ```

3. **Update Status Page**
   - Mark incident as resolved
   - Provide summary
   - Include timeline

### 6. Post-Incident (24-48 hours)

1. **Post-Mortem Meeting**
   - Schedule within 48 hours
   - Include all stakeholders
   - Review timeline
   - Analyze root cause
   - Discuss response effectiveness

2. **Post-Mortem Document**
   ```markdown
   # Post-Mortem: [Incident Title]

   **Date**: [Date]
   **Duration**: [Duration]
   **Severity**: [P0/P1/P2/P3]
   **Incident Commander**: [Name]

   ## Summary
   [Brief overview of what happened]

   ## Timeline
   - [Time]: Event 1
   - [Time]: Event 2
   - ...

   ## Root Cause
   [Detailed explanation]

   ## Impact
   - Users affected: [Number/Percentage]
   - Services affected: [List]
   - Data loss: [Yes/No - Details]

   ## What Went Well
   - [Item 1]
   - [Item 2]

   ## What Could Be Improved
   - [Item 1]
   - [Item 2]

   ## Action Items
   - [ ] [Action 1] - Owner: [Name] - Due: [Date]
   - [ ] [Action 2] - Owner: [Name] - Due: [Date]

   ## Lessons Learned
   [Key takeaways]
   ```

3. **Follow-Up Actions**
   - Create tickets for action items
   - Update runbooks
   - Improve monitoring/alerts
   - Conduct training if needed

## Roles & Responsibilities

### Incident Commander

**Primary Responsibilities:**
- Overall coordination
- Decision making
- Communication coordination
- Escalation management

**Activities:**
- Assess severity
- Assign tasks to responders
- Maintain timeline
- Update stakeholders
- Ensure resolution

### Technical Responder

**Primary Responsibilities:**
- Technical investigation
- Implement fixes
- Execute recovery procedures
- Provide technical updates

**Activities:**
- Debug issues
- Deploy fixes
- Monitor systems
- Update incident commander

### Communications Lead

**Primary Responsibilities:**
- Internal communication
- External communication
- Status page updates
- Stakeholder updates

**Activities:**
- Post updates in Slack
- Update status page
- Notify stakeholders
- Prepare customer communications

## Communication Templates

### Initial Alert (Slack)

```
🚨 INCIDENT: [Title]

Severity: [P0/P1/P2]
Started: [Time]
Status: Investigating

Impact:
- [Impact 1]
- [Impact 2]

Actions:
- [Action 1]
- [Action 2]

IC: @[name]
Responders: @[names]

Updates in thread every [X] minutes.
```

### Status Update (Slack)

```
📊 UPDATE [+15min]: [Title]

Status: [Investigating/Identified/Monitoring/Resolved]

Progress:
- ✅ [Completed action]
- ⏳ [In progress action]
- 🔜 [Next action]

Current metrics:
- Error rate: [X]%
- Latency P95: [X]ms
- Affected users: [X]

Next update in [X] minutes.
```

### Resolution Notice (Slack)

```
✅ RESOLVED: [Title]

Duration: [X] minutes
Root cause: [Brief explanation]
Fix: [What was done]

Current status:
- Error rate: [X]%
- Latency P95: [X]ms
- All services: ✅ Healthy

Post-mortem: [Date/Time]
Thanks to @[responders] for quick response!
```

### External Communication (Users)

```
[Service Name] Incident - [Date]

We experienced [brief issue description] from [start time] to [end time] ([duration]).

Impact:
- [Impact description]
- [Affected features]

Resolution:
[What was done to resolve]

Status:
All services are now operating normally. We're monitoring closely to ensure stability.

We apologize for any inconvenience. A full post-mortem will be published within 48 hours.

- The [Company] Team
```

## Escalation Paths

### Technical Escalation

```
Level 1: On-Call Engineer (0-15 min)
    ↓ (if no progress)
Level 2: Senior Engineer (15-30 min)
    ↓ (if no progress)
Level 3: Engineering Manager (30-60 min)
    ↓ (if critical)
Level 4: VP Engineering / CTO (60+ min)
```

### Business Escalation

```
Level 1: Customer Support Lead
    ↓
Level 2: Customer Success Manager
    ↓
Level 3: VP Customer Success
    ↓
Level 4: CEO
```

## Tools & Resources

### Monitoring & Alerting

- **DataDog**: https://app.datadoghq.com
- **Sentry**: https://sentry.io/organizations/treebeard
- **PagerDuty**: https://treebeard.pagerduty.com

### Dashboards

- Service Health: [Link]
- Infrastructure: [Link]
- Application Performance: [Link]
- Business Metrics: [Link]

### Runbooks

- High Error Rate: `/docs/runbooks/high-error-rate.md`
- High Latency: `/docs/runbooks/high-latency.md`
- Database Issues: `/docs/runbooks/database-issues.md`
- Cache Failure: `/docs/runbooks/cache-failure.md`
- Claude API Issues: `/docs/runbooks/claude-api-issues.md`

### Communication Channels

- **Slack**: #alerts, #incidents, #engineering
- **Status Page**: status.treebeard.com
- **Incident Log**: [Confluence/Notion link]

## Best Practices

### Do's

✅ **Acknowledge quickly** - Within 5 minutes
✅ **Communicate frequently** - Regular updates
✅ **Follow runbooks** - Use established procedures
✅ **Document everything** - Timeline, actions, decisions
✅ **Focus on mitigation first** - Fix now, perfect later
✅ **Learn from incidents** - Conduct post-mortems
✅ **Be blameless** - Focus on systems, not people

### Don'ts

❌ **Don't panic** - Stay calm and methodical
❌ **Don't guess** - Use data and metrics
❌ **Don't work in silos** - Communicate with team
❌ **Don't skip communication** - Keep stakeholders informed
❌ **Don't rush without thinking** - Avoid making things worse
❌ **Don't skip post-mortems** - Always learn and improve
❌ **Don't blame individuals** - Focus on process improvement

## Training & Preparedness

### Regular Drills

- **Monthly**: Game days for common scenarios
- **Quarterly**: Full incident response drill
- **Annually**: Disaster recovery test

### Incident Response Training

- New engineer onboarding includes incident response
- Runbook review sessions
- Post-mortem discussion meetings
- On-call rotation training

### Continuous Improvement

- Review incidents monthly
- Update runbooks based on learnings
- Improve monitoring and alerting
- Automate common responses
- Reduce MTTR over time

## Metrics

### Key Metrics to Track

- **MTTA** (Mean Time To Acknowledge): < 5 minutes
- **MTTI** (Mean Time To Identify): < 15 minutes
- **MTTR** (Mean Time To Resolve): Varies by severity
  - P0: < 1 hour
  - P1: < 4 hours
  - P2: < 24 hours
- **Incident Frequency**: Track trends
- **False Positive Rate**: < 5%

### Goals

- Reduce incident frequency
- Reduce MTTR
- Increase automation
- Improve runbook coverage
- Decrease repeat incidents

## Support Contacts

### Internal

- **Engineering On-Call**: See PagerDuty schedule
- **DevOps Team**: #devops Slack channel
- **Engineering Manager**: [Email/Phone]
- **CTO**: [Email/Phone]

### External

- **AWS Support**: [Phone/Email]
- **DataDog Support**: support@datadoghq.com
- **Anthropic Support**: support@anthropic.com
- **Database Vendor**: [Contact info]

## Appendix

### Incident Log Template

```
Incident ID: INC-[DATE]-[NUMBER]
Severity: [P0/P1/P2/P3]
Status: [Open/Resolved]
Created: [Date/Time]
Resolved: [Date/Time]
Duration: [Duration]

Title: [Brief description]

Impact:
- [Impact details]

Root Cause:
- [Root cause analysis]

Actions Taken:
- [Action 1]
- [Action 2]

Follow-up Items:
- [Item 1]
- [Item 2]

Links:
- Slack thread: [Link]
- Post-mortem: [Link]
- Related tickets: [Links]
```

### Checklist: Incident Commander

```
During Incident:
- [ ] Acknowledge alert within 5 minutes
- [ ] Post initial message in #alerts
- [ ] Assess severity
- [ ] Assign responders
- [ ] Create incident ticket
- [ ] Maintain timeline
- [ ] Post regular updates
- [ ] Coordinate resolution
- [ ] Verify fix
- [ ] Post resolution message
- [ ] Update status page

After Incident:
- [ ] Schedule post-mortem (within 48h)
- [ ] Create post-mortem document
- [ ] Document timeline
- [ ] Create follow-up tickets
- [ ] Update runbooks
- [ ] Share learnings with team
```
