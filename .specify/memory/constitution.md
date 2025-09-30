<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0 (major architectural change)
- Modified principles: 
  * II. 多租户安全 → 多租户隔离 (reduced from strict security to basic isolation)
  * III. 微服务架构 → 单体后端架构 (major architectural change from microservices to monolith)
- Added sections: None
- Removed sections: None
- Templates requiring updates: 
  ✅ Updated: constitution.md
  ⚠ Pending: None identified (existing templates accommodate both architectures)
- Follow-up TODOs: None
-->

# grainAdminPro B2B2C Platform Constitution

## Core Principles

### I. API优先原则 (API-First Development)
All features MUST be designed with API interfaces before frontend implementation. APIs serve as contracts between frontend and backend and MUST be documented with OpenAPI specifications. Frontend applications consume these APIs without direct database access. This ensures consistent data access patterns, enables multiple frontend implementations, and supports future integrations.

### II. 多租户隔离 (Multi-Tenant Isolation)
The system MUST enforce basic data isolation and access controls between tenants (商家). Each tenant's data MUST be properly isolated at the application level with clear tenant boundaries. All API endpoints MUST verify tenant context before data access. User permissions MUST be validated for every operation with appropriate role-based access control.

### III. 单体后端架构 (Monolithic Backend Architecture)
The platform MUST be architected as a unified API backend service with separate static frontend applications: 主后台 (Admin Frontend) and 商家后台 (Merchant Frontend). The backend provides a single, cohesive API that serves both frontend applications. This architecture simplifies deployment, data consistency, and cross-functional operations while maintaining clear separation of concerns through API design.

### IV. 测试驱动开发 (Test-Driven Development) - NON-NEGOTIABLE
Critical business logic MUST be developed using TDD methodology: Tests written → Tests fail → Implementation → Tests pass → Refactor. Unit tests are required for all business logic. Integration tests MUST cover API endpoints, payment flows, user authentication, and data consistency scenarios. Test coverage below 80% for core modules is not acceptable.

### V. 性能优先 (Performance-First)
The system MUST support high concurrency with response times under 200ms for API calls. Database queries MUST be optimized with proper indexing strategies. Multi-layer caching (application cache, Redis, CDN) is mandatory for frequently accessed data. Performance monitoring and alerting MUST be implemented to track SLA compliance.

### VI. 可扩展性设计 (Extensibility Design)
The platform MUST support plugin-based architecture for feature modules that can be dynamically loaded without system restart. Business rules MUST be configurable through admin interfaces rather than hard-coded. The system MUST support horizontal scaling and new tenant onboarding without service interruption.

### VII. 基础日志记录 (Essential Logging)
All critical operations (user actions, payment transactions, security events, errors) MUST be logged with structured JSON format. Logs MUST include correlation IDs for request tracing across the application. Centralized log aggregation and alerting MUST be implemented for production environments. Personal data in logs MUST be masked or encrypted.

### VIII. 代码规范统一 (Code Standards Uniformity)
All code MUST follow established coding standards with automated enforcement through linting tools. Code reviews are mandatory for all pull requests. Static analysis tools MUST be integrated into CI/CD pipelines. Code formatting MUST be consistent across the entire codebase and enforced automatically.

## Security Requirements

The backend service MUST implement HTTPS with valid certificates. Authentication tokens MUST expire within 24 hours and support refresh mechanisms. Sensitive data (payment info, personal data) MUST be encrypted both at rest and in transit. All database connections MUST use encrypted channels. Security patches MUST be applied within 7 days of release.

## Quality Gates

Before production deployment, the system MUST pass: all automated tests (unit, integration, contract), security scans with zero critical vulnerabilities, performance benchmarks meeting SLA requirements, and manual acceptance testing. Database migrations MUST be reversible and tested in staging environments identical to production.

## Governance

This Constitution supersedes all other development practices and technical decisions. All pull requests and code reviews MUST verify compliance with these principles. Any deviation MUST be documented with explicit justification and temporary exception approval. 

Constitution amendments require: technical impact assessment, team consensus, migration plan for existing code, and updated documentation. All violations discovered in production MUST be addressed within the next sprint cycle.

Constitutional compliance is verified through automated checks in CI/CD pipelines and quarterly architecture reviews.

**Version**: 2.0.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2025-09-29