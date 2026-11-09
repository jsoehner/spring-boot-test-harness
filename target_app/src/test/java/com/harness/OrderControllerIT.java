package com.harness;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class OrderControllerIT {

    @Autowired
    private MockMvc mockMvc;

    private static final String API_KEY = "secure-secret-key";

    @Test
    void testBillOrder_ValidId() throws Exception {
        mockMvc.perform(post("/api/orders/bill/101")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user1"))
                .andExpect(status().isOk())
                .andExpect(content().string("Order 101 billed successfully"));
    }

    @Test
    void testBillOrder_InvalidId() throws Exception {
        mockMvc.perform(post("/api/orders/bill/abc")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user1"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string("Error: Invalid Order ID format. Must be numeric."));
    }

    @Test
    void testShipOrder_ValidId() throws Exception {
        // First bill it
        mockMvc.perform(post("/api/orders/bill/102")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user2"))
                .andExpect(status().isOk());
        // Then ship it
        mockMvc.perform(post("/api/orders/ship/102")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user2"))
                .andExpect(status().isOk())
                .andExpect(content().string("Order 102 shipped successfully"));
    }

    @Test
    void testShipOrder_InvalidId() throws Exception {
        mockMvc.perform(post("/api/orders/ship/xyz")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user1"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string("Error: Invalid Order ID format. Must be numeric."));
    }

    @Test
    void testBillOrder_NotFound() throws Exception {
        mockMvc.perform(post("/api/orders/bill/999")
                .header("X-API-KEY", API_KEY)
                .header("X-USER-ID", "user1"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string("Request failed"));
    }
}
