# Test Plan for Target Application

## Overview
This plan covers the testing of the `TargetApplication` which provides an order management API.

## Scope
- `POST /api/orders/bill/{id}`
- `POST /api/orders/ship/{id}`

## Test Cases

### 1. Unit Tests (WorkOrderService)
- `testBillOrder_Success`: Bill a pending order.
- `testBillOrder_NotFound`: Bill a non-existent order.
- `testBillOrder_AlreadyBilled`: Bill an order already in BILLED state.
- `testShipOrder_Success`: Ship a billed order.
- `testShipOrder_NotFound`: Ship a non-existent order.
- `testShipOrder_NotBilled`: Ship an order that is still PENDING.
- `testShipOrder_AlreadyShipped`: Ship an order already in SHIPPED state.

### 2. Integration Tests (OrderController)
- `testBillOrder_ValidId`: Successful billing with numeric ID.
- `testBillOrder_InvalidId`: Error message for non-numeric ID.
- `testShipOrder_ValidId`: Successful shipping with numeric ID.
- `testShipOrder_InvalidId`: Error message for non-numeric ID.
- `testBillOrder_OrderNotFound`: 404/Error for non-existent ID.
- `testShipOrder_OrderNotFound`: 404/Error for non-existent ID.

### 3. Concurrency Tests
- `testConcurrentBillOrder`: Multiple threads attempting to bill the same order simultaneously.
- `testConcurrentShipOrder`: Multiple threads attempting to ship the same order simultaneously.

### 4. Functional/E2E Tests (Python/Requests)
- `test_api_flow_success`: Full flow from PENDING -> BILLED -> SHIPPED.
- `test_api_flow_invalid_id`: Verify error responses for bad inputs.
- `test_api_flow_concurrency`: Verify that only one thread succeeds in a race condition.
