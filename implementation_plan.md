# Change Request (CR) - Implementation Plan
**Project:** MindCare AI  
**Release Baseline:** v2.0.1  
**Status:** Approved & Executed  

---

## 1. Goal Description
The objective of this change is to transition the MindCare AI platform from a stateless prototype to a secure, stateful, and production-ready ecosystem. 

## 2. Proposed Changes
### [Component Name] - Core Backend & SCM Setup
*   **[MODIFY] app.py:** Add `APP_VERSION`, session-based history, and Gemini AI integration.
*   **[NEW] tests/test_app.py:** Implement automated functional audits for login/signup and AI triage.
*   **[NEW] Dockerfile:** Create an environment baseline for consistent deployment.
*   **[NEW] .env:** Securely manage API keys and secret credentials.

## 3. Impact Analysis
*   **Configuration Items Impacted:** Source Code, Database Schema, Build Scripts.
*   **Risk:** Data migration risk for the SQLite store; mitigated by a fresh schema audit.

## 4. Verification Plan
### Automated Tests
*   Run `pytest tests/` to confirm 100% pass rate on Auth and AI logic.
*   Run `flake8 app.py` to ensure 0 physical audit violations.

### Manual Verification
*   Verify that the "v2.0.1" version badge is visible in the UI stats row.
