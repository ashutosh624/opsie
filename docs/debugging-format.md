# Software Engineering Triage Bot - Debugging Format Template

## Standard Debugging Information Format

When reporting technical issues in support threads, please provide the following information to ensure efficient triage and resolution:

### 🔍 **Issue Summary**
- **Title**: Brief, descriptive title of the issue
- **Severity**: Critical/High/Medium/Low
- **Impact**: Who/what is affected (users, systems, processes)

### 📝 **Problem Description**
- Clear description of what's happening
- When the issue started occurring
- Frequency (always, intermittent, specific conditions)

### 🔄 **Steps to Reproduce**
1. Step one
2. Step two
3. Step three
...

### ✅ **Expected Behavior**
- What should happen normally

### ❌ **Actual Behavior**
- What actually happens instead

### 🖥️ **Environment Details**
- **Operating System**: (e.g., Ubuntu 20.04, macOS 13.0, Windows 11)
- **Application Version**: (e.g., v2.1.3)
- **Browser**: (if applicable - Chrome 115, Firefox 116)
- **Database**: (if applicable - PostgreSQL 14.2)
- **Dependencies**: Relevant library/package versions

### 📋 **Error Messages/Logs**
```
Paste exact error messages, stack traces, or relevant log entries here
```

### 🔧 **Attempted Solutions**
- What troubleshooting steps have already been tried
- Any workarounds currently in use

### 📎 **Additional Context**
- Screenshots (if visual issue)
- Code snippets (if relevant)
- Configuration files (sanitized)
- Network topology (if connectivity issue)

---

## Channel-Specific Guidelines

### For #critical-incidents
- Include customer impact assessment
- Provide timeline of when issue started
- List any current mitigations in place

### For #bug-reports  
- Include reproduction steps with test data
- Specify if issue exists in multiple environments
- Reference any related tickets or previous issues

### For #performance-issues
- Include metrics/graphs showing performance degradation
- Specify baseline vs current performance
- Include resource utilization data (CPU, memory, disk, network)

### For #deployment-issues
- Include deployment logs
- Specify which environment(s) affected
- List rollback options available

---

## Triage Bot Capabilities

The AI triage bot will:

1. **Verify Information Completeness**: Check if all required debugging information is provided
2. **Assess Severity**: Evaluate the impact and urgency of the issue
3. **Suggest Next Steps**: Provide initial troubleshooting recommendations
4. **Identify Missing Information**: Request additional details if needed
5. **Escalation Guidance**: Recommend escalation path if required

## Example Usage

Good issue report:
```
🔍 **Issue Summary**
Title: User authentication failing for OAuth login
Severity: High
Impact: 50% of users unable to login via Google OAuth

📝 **Problem Description**
Since 2024-01-15 14:30 UTC, users attempting to login via Google OAuth 
are receiving "Invalid credentials" error. Username/password login works fine.

🔄 **Steps to Reproduce**
1. Go to login page
2. Click "Login with Google"
3. Complete Google OAuth flow
4. Redirected back with error

✅ **Expected Behavior**
User should be logged in and redirected to dashboard

❌ **Actual Behavior**
Error message: "Authentication failed - Invalid credentials"

🖥️ **Environment Details**
- Operating System: Production servers (Ubuntu 20.04)
- Application Version: v3.2.1 (deployed 2024-01-15 14:00 UTC)
- Database: PostgreSQL 14.2

📋 **Error Messages/Logs**
[2024-01-15 14:32:15] ERROR: OAuth token validation failed
[2024-01-15 14:32:15] ERROR: Invalid audience in JWT token
```

The triage bot will analyze this information and provide guidance on next steps, escalation needs, and any missing information.
