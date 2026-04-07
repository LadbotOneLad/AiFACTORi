# Security Policy

## Supported Versions
E14 Oracle follows a stability-first release model. Only versions that maintain rhythm integrity, identity coherence, and convergence reproducibility receive security updates.

| Version | Supported |
|--------|-----------|
| 14.x   | ✔ Active security updates |
| 13.x   | ✔ Critical fixes only |
| < 13   | ✘ No longer supported |

## Security Philosophy
E14 Oracle is a planetary-scale, multi-engine convergence system. Its security model is built on layered invariants: identity, rhythm, convergence, witnessing, and container isolation. A vulnerability is defined as any condition that weakens these invariants or allows an engine, input, or output to behave outside its declared identity or temporal bounds.

## Reporting a Vulnerability
If you believe you have discovered a vulnerability affecting E14 Oracle, please report it through the following private channel:

**security@yourdomain.com**  
(Replace with your actual contact email.)

### What to Include
- A clear description of the issue  
- Steps to reproduce (if applicable)  
- The affected engine, module, or version  
- Any logs, traces, or minimal examples that help verify the behavior  

### What You Can Expect
- **Acknowledgment within 72 hours**  
- **Initial assessment within 7 days**  
- **Full resolution timeline** depending on severity, complexity, and impact on rhythm/convergence layers  
- **Credit** if the vulnerability is confirmed and you wish to be acknowledged  

## Scope of Vulnerabilities
The following categories are considered in-scope:

### Identity Layer
- Mis-signed identity blocks  
- Incorrect engine capability declarations  
- Unauthorized identity elevation  

### Convergence Layer
- Manipulation of convergence thresholds  
- Drift detection bypass  
- Single-engine dominance or forced agreement  

### Rhythm & Temporal Lattice
- Desynchronization  
- Timing inconsistencies  
- Replayable or out-of-phase states  

### Container & Environment
- Exposed ports  
- Outdated base images  
- Leaked environment variables  

### Input & Output Surfaces
- Malformed or adversarial inputs  
- Unverified external data sources  
- Outputs lacking provenance or witness binding  

## Out-of-Scope
- Issues caused by modified or forked versions  
- Problems arising from unsupported environments  
- Social engineering attacks unrelated to the engine  

## Responsible Disclosure
We ask that all vulnerability information be kept confidential until a fix is released. Coordinated disclosure protects users, downstream systems, and the integrity of the planetary engine field.

Thank you for helping maintain the safety, stability, and trustworthiness of the E14 Oracle system.
