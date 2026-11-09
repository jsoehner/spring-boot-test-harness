package com.harness;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpServletResponseWrapper;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;
import java.util.regex.Pattern;

@SpringBootApplication
public class TargetApplication {
    public static void main(String[] args) {
        SpringApplication.run(TargetApplication.class, args);
    }
}

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class SecurityHeadersFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        if (response instanceof HttpServletResponse httpResponse) {
            httpResponse.setHeader("X-Content-Type-Options", "nosniff");
            httpResponse.setHeader("X-Frame-Options", "DENY");
            httpResponse.setHeader("Content-Security-Policy", "default-src 'self'");
            httpResponse.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");

            HttpServletResponse wrappedResponse = new HttpServletResponseWrapper(httpResponse) {
                @Override
                public void setHeader(String name, String value) {
                    if (!"Server".equalsIgnoreCase(name)) {
                        super.setHeader(name, value);
                    }
                }

                @Override
                public void addHeader(String name, String value) {
                    if (!"Server".equalsIgnoreCase(name)) {
                        super.addHeader(name, value);
                    }
                }
            };

            chain.doFilter(request, wrappedResponse);
            return;
        }

        chain.doFilter(request, response);
    }
}

@RestController
@RestControllerAdvice
class HarnessInventoryAndHelloController {

    private static final Pattern VALID_SKU_PATTERN = Pattern.compile("^[A-Za-z0-9_-]{1,64}$");
    private static final Pattern STRICT_BASE10_INT_PATTERN = Pattern.compile("^-?[0-9]+$");
    private static final int MAX_RESERVE_QUANTITY = 1_000;
    private static final int MAX_RESET_QUANTITY = 10_000;
    private static final int MAX_TRACKED_SKUS = 100;
    private static final int MAX_HELLO_INPUT_LENGTH = 256;

    private final Map<String, AtomicInteger> stock = new ConcurrentHashMap<>();

    public HarnessInventoryAndHelloController() {
        stock.put("SKU-ITEM-001", new AtomicInteger(1));
        stock.put("SKU-ITEM-002", new AtomicInteger(5));
    }

    private boolean hasDuplicateParameters(HttpServletRequest request) {
        if (request == null) {
            return false;
        }
        for (String[] values : request.getParameterMap().values()) {
            if (values != null && values.length > 1) {
                return true;
            }
        }
        return false;
    }

    private boolean isValidSku(String sku) {
        return sku != null && VALID_SKU_PATTERN.matcher(sku).matches();
    }

    private boolean containsControlChars(String value) {
        if (value == null) {
            return false;
        }
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c < 0x20 || c == 0x7F) {
                return true;
            }
        }
        return false;
    }

    @GetMapping("/hello")
    public ResponseEntity<Map<String, String>> hello(
            @RequestParam(value = "input", defaultValue = "world") String input,
            HttpServletRequest request) {
        if (hasDuplicateParameters(request)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "PARAMETER_POLLUTION",
                    "message", "Duplicate query parameters are not permitted"
            ));
        }
        if (input == null || input.length() > MAX_HELLO_INPUT_LENGTH || containsControlChars(input)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_INPUT",
                    "message", "Input exceeds maximum length or contains control characters"
            ));
        }
        return ResponseEntity.ok(Map.of(
                "message", "Hello from Spring Boot Test Harness Target Service!",
                "input", input
        ));
    }

    @PostMapping("/api/inventory/reserve")
    public synchronized ResponseEntity<Map<String, Object>> reserveStock(
            @RequestParam(value = "sku", defaultValue = "SKU-ITEM-001") String sku,
            @RequestParam(value = "quantity", defaultValue = "1") int quantity,
            HttpServletRequest request) {

        if (hasDuplicateParameters(request)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "PARAMETER_POLLUTION",
                    "message", "Duplicate query parameters are not permitted"
            ));
        }

        String rawSku = request != null ? request.getParameter("sku") : null;
        String effectiveSku = (rawSku != null) ? rawSku : sku;
        if (!isValidSku(effectiveSku)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_SKU",
                    "message", "SKU must be 1-64 alphanumeric, dash, or underscore characters"
            ));
        }

        String rawQuantity = request != null ? request.getParameter("quantity") : null;
        if (rawQuantity != null && !STRICT_BASE10_INT_PATTERN.matcher(rawQuantity).matches()) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "TYPE_MISMATCH",
                    "parameter", "quantity",
                    "message", "Quantity must be a strict base-10 integer"
            ));
        }

        if (quantity <= 0 || quantity > MAX_RESERVE_QUANTITY) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_QUANTITY",
                    "message", "Reservation quantity must be between 1 and " + MAX_RESERVE_QUANTITY
            ));
        }

        AtomicInteger currentStock = stock.get(effectiveSku);
        int available = (currentStock != null) ? currentStock.get() : 0;

        if (currentStock != null && available >= quantity) {
            try {
                Thread.sleep(50);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }

            int remaining = currentStock.addAndGet(-quantity);
            return ResponseEntity.ok(Map.of(
                    "sku", effectiveSku,
                    "status", "RESERVED",
                    "remaining", remaining
            ));
        }

        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of(
                "sku", effectiveSku,
                "status", "OUT_OF_STOCK",
                "remaining", available
        ));
    }

    @GetMapping("/api/inventory/status/{sku}")
    public ResponseEntity<Map<String, Object>> getStock(@PathVariable String sku) {
        if (!isValidSku(sku)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_SKU",
                    "message", "SKU format is invalid"
            ));
        }
        AtomicInteger currentStock = stock.get(sku);
        if (currentStock == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(Map.of(
                "sku", sku,
                "available", currentStock.get()
        ));
    }

    @PostMapping("/api/inventory/reset")
    public synchronized ResponseEntity<Map<String, Object>> resetStock(
            @RequestParam(value = "sku", defaultValue = "SKU-ITEM-001") String sku,
            @RequestParam(value = "quantity", defaultValue = "1") int quantity,
            HttpServletRequest request) {

        if (hasDuplicateParameters(request)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "PARAMETER_POLLUTION",
                    "message", "Duplicate query parameters are not permitted"
            ));
        }

        String rawSku = request != null ? request.getParameter("sku") : null;
        String effectiveSku = (rawSku != null) ? rawSku : sku;
        if (!isValidSku(effectiveSku)) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_SKU",
                    "message", "SKU must be 1-64 alphanumeric, dash, or underscore characters"
            ));
        }

        String rawQuantity = request != null ? request.getParameter("quantity") : null;
        if (rawQuantity != null && !STRICT_BASE10_INT_PATTERN.matcher(rawQuantity).matches()) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "TYPE_MISMATCH",
                    "parameter", "quantity",
                    "message", "Quantity must be a strict base-10 integer"
            ));
        }

        if (quantity < 0 || quantity > MAX_RESET_QUANTITY) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "INVALID_QUANTITY",
                    "message", "Reset quantity must be between 0 and " + MAX_RESET_QUANTITY
            ));
        }

        if (!stock.containsKey(effectiveSku) && stock.size() >= MAX_TRACKED_SKUS) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(Map.of(
                    "error", "SKU_CAPACITY_EXCEEDED",
                    "message", "Maximum tracked SKU capacity reached"
            ));
        }

        stock.put(effectiveSku, new AtomicInteger(quantity));
        return ResponseEntity.ok(Map.of(
                "sku", effectiveSku,
                "available", quantity,
                "status", "RESET_OK"
        ));
    }

    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<Map<String, Object>> handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
        return ResponseEntity.badRequest().body(Map.of(
                "error", "TYPE_MISMATCH",
                "parameter", ex.getName() != null ? ex.getName() : "unknown",
                "message", "Invalid parameter type or numeric overflow"
        ));
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<Map<String, Object>> handleMethodNotSupported(HttpRequestMethodNotSupportedException ex) {
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(Map.of(
                "error", "METHOD_NOT_ALLOWED",
                "method", ex.getMethod() != null ? ex.getMethod() : "UNKNOWN",
                "message", "HTTP method is not supported for this endpoint"
        ));
    }
}

@RestController
@RequestMapping("/api/orders")
class OrderController {
    private final WorkOrderService workOrderService = new WorkOrderService();
    private static final String AUTH_TOKEN = "secure-secret-key";

    @PostMapping("/bill/{id}")
    public ResponseEntity<String> billOrder(
            @RequestHeader(value = "X-API-KEY", required = false) String apiKey,
            @PathVariable String id,
            @RequestHeader(value = "X-USER-ID", required = false) String userId) {

        if (!AUTH_TOKEN.equals(apiKey)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: Invalid API Key");
        }

        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: User ID required");
        }

        if (!id.matches("^\\d{1,12}$")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error: Invalid Order ID format. Must be numeric.");
        }

        String result = workOrderService.billOrder(id, userId);

        if (result.startsWith("Error:")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Request failed");
        }

        return ResponseEntity.ok(result);
    }

    @PostMapping("/ship/{id}")
    public ResponseEntity<String> shipOrder(
            @RequestHeader(value = "X-API-KEY", required = false) String apiKey,
            @PathVariable String id,
            @RequestHeader(value = "X-USER-ID", required = false) String userId) {

        if (!AUTH_TOKEN.equals(apiKey)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: Invalid API Key");
        }

        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: User ID required");
        }

        if (!id.matches("^\\d{1,12}$")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error: Invalid Order ID format. Must be numeric.");
        }

        String result = workOrderService.shipOrder(id, userId);

        if (result.startsWith("Error:")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Request failed");
        }

        return ResponseEntity.ok(result);
    }
}

class WorkOrderService {
    private static final Logger logger = Logger.getLogger(WorkOrderService.class.getName());
    private final Map<String, OrderData> orders = new ConcurrentHashMap<>();

    public WorkOrderService() {
        orders.put("101", new OrderData("PENDING", "user1"));
        orders.put("102", new OrderData("PENDING", "user2"));
    }

    private static class OrderData {
        String status;
        String ownerId;

        OrderData(String status, String ownerId) {
            this.status = status;
            this.ownerId = ownerId;
        }
    }

    public synchronized String billOrder(String id, String userId) {
        OrderData order = orders.get(id);

        if (order == null) {
            logger.warning("Attempted to bill non-existent order: " + id);
            return "Error: Request failed";
        }

        if (!order.ownerId.equals(userId)) {
            logger.warning("Unauthorized bill attempt on order " + id + " by user " + userId);
            return "Error: Unauthorized";
        }

        if ("PENDING".equals(order.status)) {
            try { Thread.sleep(100); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            order.status = "BILLED";
            logger.info("Order " + id + " billed by user " + userId);
            return "Order " + id + " billed successfully";
        }

        return "Error: Request failed";
    }

    public synchronized String shipOrder(String id, String userId) {
        OrderData order = orders.get(id);

        if (order == null) {
            logger.warning("Attempted to ship non-existent order: " + id);
            return "Error: Request failed";
        }

        if (!order.ownerId.equals(userId)) {
            logger.warning("Unauthorized ship attempt on order " + id + " by user " + userId);
            return "Error: Unauthorized";
        }

        if ("BILLED".equals(order.status)) {
            try { Thread.sleep(100); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            order.status = "SHIPPED";
            logger.info("Order " + id + " shipped by user " + userId);
            return "Order " + id + " shipped successfully";
        }

        return "Error: Request failed";
    }
}
