---
applyTo: "*agent*"
---

# Strict Coding Requirements

## Scope

These requirements apply to all programming languages, frameworks, and environments used in this project.

## Core Principles

1. **Production-Ready Code**: Every line must be complete, fully implemented, and ready for immediate production use.
2. **Zero Tolerance for Incompletes**: Absolutely no:
   - Stub code
   - Placeholders (e.g., `// TODO`, `FIXME`)
   - Demo/pseudo-code
   - Untested implementations
3. **Professional Engineering Standards**: All code must meet professional standards including:
   - Proper error handling
   - Edge case coverage
   - Documentation where needed (see below)
   - Adherence to project conventions and style guides
4. **Security Focus**: All code must adhere to security best practices, including:
   - Proper handling of sensitive data
   - Prevention of common vulnerabilities (e.g., SQL injection, XSS)
   - Secure coding practices
5. **Accessibility**: For UI code, ensure compliance with accessibility standards (e.g., WCAG).

## Mandatory Practices

- **Full Implementation**: Functions, classes, and modules must be completely implemented with all required components.
- **Documentation**: Provide clear docstrings for all public functions/classes, inline comments for complex logic, and update external documentation as needed.
- **Testing**: All code must include automated tests with comprehensive coverage (target: 90%+ where feasible). Tests must cover edge cases and failure scenarios.
- **Code Review**: All code must be reviewed by a peer or pass automated review checks before merging.
- **Style Guide**: Adhere to the project's [style guide](link-to-style-guide) for the relevant language(s).
- **Version Control**: Use meaningful commit messages and follow branching/PR conventions.

- **Immediate Communication**: If unable to meet these requirements for any reason, immediately:

  1. Halt coding
  2. Report the obstacle
  3. Request guidance

- **Scope Compliance**: Requirements apply equally to all tasks regardless of complexity or size.

## Validation Checklist

- [ ] No partial implementations
- [ ] All edge cases handled
- [ ] Meets project style guidelines ([link](link-to-style-guide))
- [ ] Documentation is complete (docstrings, comments, external docs)
- [ ] Code is readable and maintainable
- [ ] Automated test coverage is comprehensive (≥90%)
- [ ] Code has passed review (peer or automated)
- [ ] Version control best practices followed

**Violation of these requirements is unacceptable and will result in immediate code rejection.**
