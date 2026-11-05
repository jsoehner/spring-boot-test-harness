package com.harness;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

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

    @PostMapping("/bill/{id}")
    public String billOrder(@PathVariable String id) {
        // FIX: Added strict validation on order ID
        if (!id.matches("\\d+")) {
            return "Error: Invalid Order ID format. Must be numeric.";
        }
        return workOrderService.billOrder(id);
    }

    @PostMapping("/ship/{id}")
    public String shipOrder(@PathVariable String id) {
        // FIX: Added strict validation on order ID
        if (!id.matches("\\d+")) {
            return "Error: Invalid Order ID format. Must be numeric.";
        }
        return workOrderService.shipOrder(id);
    }
}

class WorkOrderService {
    // Simulating a database with a Map
    private final Map<String, String> orderStatuses = new ConcurrentHashMap<>();

    public WorkOrderService() {
        // Pre-populate some orders
        orderStatuses.put("101", "PENDING");
        orderStatuses.put("102", "PENDING");
    }

    /**
     * FIX: Added synchronization to prevent race conditions.
     */
    public synchronized String billOrder(String id) {
        String currentStatus = orderStatuses.get(id);
        if (currentStatus == null) {
            return "Order not found";
        }
        if ("PENDING".equals(currentStatus)) {
            // Simulate some processing time
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            orderStatuses.put(id, "BILLED");
            return "Order " + id + " billed successfully";
        }
        return "Order " + id + " is already " + currentStatus;
    }

    public synchronized String shipOrder(String id) {
        String currentStatus = orderStatuses.get(id);
        if (currentStatus == null) {
            return "Order not found";
        }
        if ("BILLED".equals(currentStatus)) {
            // Simulate some processing time
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            orderStatuses.put(id, "SHIPPED");
            return "Order " + id + " shipped successfully";
        }
        return "Order " + id + " is not in BILLED state (current: " + currentStatus + ")";
    }
}
