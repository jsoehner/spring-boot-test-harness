package com.harness;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

@SpringBootApplication
public class TargetApplication {
    public static void main(String[] args) {
        SpringApplication.run(TargetApplication.class, args);
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

        if (userId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: User ID required");
        }

        if (!id.matches("\\d+")) {
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

        if (userId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Error: User ID required");
        }

        if (!id.matches("\\d+")) {
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
            try { Thread.sleep(100); } catch (InterruptedException e) {}
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
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            order.status = "SHIPPED";
            logger.info("Order " + id + " shipped by user " + userId);
            return "Order " + id + " shipped successfully";
        }
        
        return "Error: Request failed";
    }
}
