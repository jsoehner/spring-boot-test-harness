package com.harness;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.concurrent.CountDownLatch;
import static org.junit.jupiter.api.Assertions.*;

public class WorkOrderServiceTest {
    private WorkOrderService service;

    @BeforeEach
    void setUp() {
        service = new WorkOrderService();
    }

    @Test
    void testBillOrder_Success() {
        String result = service.billOrder("101", "user1");
        assertEquals("Order 101 billed successfully", result);
    }

    @Test
    void testBillOrder_NotFound() {
        String result = service.billOrder("999", "user1");
        assertEquals("Error: Request failed", result);
    }

    @Test
    void testBillOrder_AlreadyBilled() {
        service.billOrder("101", "user1");
        String result = service.billOrder("101", "user1");
        assertEquals("Error: Request failed", result);
    }

    @Test
    void testShipOrder_Success() {
        service.billOrder("101", "user1");
        String result = service.shipOrder("101", "user1");
        assertEquals("Order 101 shipped successfully", result);
    }

    @Test
    void testShipOrder_NotFound() {
        String result = service.shipOrder("999", "user1");
        assertEquals("Error: Request failed", result);
    }

    @Test
    void testShipOrder_NotBilled() {
        String result = service.shipOrder("102", "user2");
        assertEquals("Error: Request failed", result);
    }

    @Test
    void testShipOrder_AlreadyShipped() {
        service.billOrder("101", "user1");
        service.shipOrder("101", "user1");
        String result = service.shipOrder("101", "user1");
        assertEquals("Error: Request failed", result);
    }

    @Test
    void testConcurrentBillOrder() throws InterruptedException {
        int threadCount = 10;
        Thread[] threads = new Thread[threadCount];
        CountDownLatch latch = new CountDownLatch(1);
        
        for (int i = 0; i < threadCount; i++) {
            threads[i] = new Thread(() -> {
                try {
                    latch.await();
                    service.billOrder("101", "user1");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            threads[i].start();
        }

        latch.countDown();
        for (Thread t : threads) {
            t.join();
        }

        // Only one should have succeeded in changing it to BILLED, 
        // but since the service is synchronized, it should just be BILLED.
        String result = service.billOrder("101", "user1");
        assertEquals("Error: Request failed", result);
    }
}
