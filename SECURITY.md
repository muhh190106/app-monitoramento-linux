# Security and privacy

## Current scope

Activity Monitor is a pre-alpha development project. The current demo uses synthetic data; it does not collect desktop activity or run a background service. There is no production release or long-term support commitment yet.

## Report a vulnerability privately

Use the repository's **Security > Report a vulnerability** option when private vulnerability reporting is available. If that option is unavailable, open an issue requesting a private reporting channel without including vulnerability details, personal data, or exploit instructions. Wait for a private channel before sharing sensitive information.

Include the affected commit or version, a minimal reproduction using synthetic data, the expected impact, and any suggested mitigation. Do not post real activity histories or credentials.

## Data handling principles

- Keep activity data out of Git, issue reports, CI artifacts, and cloud development workspaces.
- Use explicit user controls before starting future collectors.
- Keep future local services bound to the local device by default.
- Treat window titles and URLs as sensitive information.
- Design data retention, deletion, and synchronization deliberately before introducing them.

These are development requirements for upcoming features, not claims that collection and storage have already been implemented.
