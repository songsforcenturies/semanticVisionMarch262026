# INCIDENT REPORT — Emergent Platform Deployment Failure & Data Loss
## Date: March 11-12, 2026

---

**To:** Emergent Support Team (support@emergent.sh)  
**From:** Allen (allen@songsforcenturies.com)  
**App:** learning-portal-v1 (Semantic Vision)  
**Custom Domain:** semanticvision.ai  
**Severity:** CRITICAL — Production data loss + complete service outage  

---

## SUMMARY

On March 11, 2026, I used the "Replace Deployment" feature on the Emergent platform to update my production application (learning-portal-v1 / semanticvision.ai). This action resulted in:

1. **Complete production database wipe** — All user accounts, student data, word banks, stories, progress reports, payment records, and configuration were permanently deleted.
2. **Persistent deployment failure** — Despite multiple re-deployment attempts (6+), the app shows "Live" in the Emergent management panel but returns "Deployment not found" on all access URLs.

---

## TIMELINE OF EVENTS

| Time (UTC) | Event |
|------------|-------|
| March 10, ~23:00 | App fully operational. Deployment 4 live. All features working. Users registered, data intact. |
| March 11, ~18:00 | Opened new build session to add features (Cumulative Time Log, Backup & Restore) |
| March 11, ~20:30 | Features completed and tested in preview environment. Clicked "Replace Deployment" |
| March 11, ~21:00 | Attempted login on semanticvision.ai — **"Login failed"**. Discovered all user data was gone. |
| March 11, ~21:30 | Added self-bootstrapping code (auto-create admin on empty DB). Re-deployed. |
| March 11, ~22:00 | Deployment shows "Live" (d6p198k) but semanticvision.ai shows **"Deployment not found"** |
| March 11, ~22:30 | Re-deployed again (Deployment 5, d6p1pn4). Same result — "Live" in panel, "Deployment not found" on URLs. |
| March 11, ~22:45 | Tried learning-portal-v1.emergent.host — also "Deployment not found" |
| March 11, ~23:00 | Tried d6p198k.emergent.host and d6p1pn4.emergent.host — both "Deployment not found" |
| March 12, ~01:30 | Multiple additional re-deploy attempts. All show "Live" but remain unreachable. |

---

## IMPACT

### Data Loss
- **User accounts:** All registered users (guardians, teachers, brand partners) — LOST
- **Student profiles:** All student data, learning preferences, interests — LOST
- **Word banks:** All vocabulary banks (custom and system) — LOST
- **Stories/Narratives:** All AI-generated stories and reading progress — LOST
- **Assessment results:** All quiz scores and accuracy data — LOST
- **Payment records:** All transaction history — LOST
- **Configuration:** All admin settings, integrations, API keys stored in DB — LOST

### Service Outage
- semanticvision.ai has been completely unreachable since ~21:00 UTC on March 11
- No users can access the platform
- This is a production educational platform with active users

### Financial Impact
- Multiple deployment credits consumed (6+ deployments)
- From screenshots: credits dropped from 284.46 to 269.56 in just 30 minutes
- Estimated total credits consumed today: **100-150+ credits** (deployments + build session time)
- Loss of user trust due to extended outage

---

## TECHNICAL DETAILS

### What the code does correctly:
- Preview environment works perfectly (all APIs respond, login works, data intact)
- Deployment health check passes all criteria
- Self-bootstrapping code creates admin account on empty database
- No destructive operations in startup migrations
- No code changes that could cause data deletion

### What appears broken on Emergent's side:
1. **"Replace Deployment" wiped the MongoDB database** — This should only replace code, not data
2. **Deployment routing is broken** — Panel shows "Live" but all URLs return "Deployment not found"
3. **Custom domain mapping lost** — semanticvision.ai no longer resolves to the deployment

---

## REQUESTS

1. **Investigate why "Replace Deployment" deleted the production MongoDB database**
2. **Determine if any database backup exists** that can recover the March 10 data
3. **Fix the deployment routing** so the app is accessible at its URLs
4. **Credit refund** for all failed deployment attempts on March 11-12
5. **Documentation clarification** on whether "Replace Deployment" preserves or resets databases
6. **Preventive measures** to ensure this cannot happen to other users

---

## CONTACT

- **Email:** allen@songsforcenturies.com
- **App Name:** learning-portal-v1
- **Job ID:** b31fd16e-7706-4044-8348-9bf5ef6072a4

---

*This report was generated from the build environment with full technical context of the application.*
