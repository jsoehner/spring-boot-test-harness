# ADR 0001: Security Threat Model for Order Processing

## Status
Proposed

## Context
The `OrderController` provides endpoints for billing and shipping orders. We need to ensure these endpoints are resilient against common attack vectors, especially since they interact with the core business state of the application.

## Decision
We will implement a multi-layered security defense for the `OrderController`:
1. **Authentication**: Require valid JWT tokens for all `/api/orders/**` endpoints.
2. **Authorization**: Ensure that the authenticated user has permission to access the specific order ID (Ownership check).
3. **Input Validation**: Enforce strict numeric and range checks on order IDs.
4. **Audit Logging**: Record every state transition (PENDING -> BILLED, etc.) in a secure audit log.
5. **Rate Limiting**: Implement per-user rate limits to prevent DoS attacks on the billing flow.

## Consequences
- **Pros**:
    - Prevents unauthorized billing of orders.
    - Protects against injection and malformed input.
    - Provides a clear audit trail for customer support.
- **Cons**:
    - Adds latency due to auth and ownership checks.
    - Increases complexity of the `WorkOrderService`.

## Threat Analysis (STRIDE)
| Threat | Description | Mitigation |
|--------|-------------|------------|
| Spoofing | Attacker impersonates a user to bill an order. | Implement JWT-based authentication. |
| Tampering | Attacker modifies the `id` parameter to access other orders. | Implement ownership verification (User ID must match Order owner). |
| Repudiation | User claims they didn't bill an order. | Implement an immutable audit log for all state changes. |
| Info Disclosure | Response leaks internal order IDs or statuses. | Sanitize responses to only show necessary information. |
| DoS | Attacker floods the billing endpoint. | Implement rate limiting and request validation. |
| Elevation of Privilege | User accesses admin-only billing functions. | Implement Role-Based Access Control (RBAC). |
