import org.springframework.ai.autoconfigure.openai.OpenAiProperties;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.openai.OpenAiChatClient;
import org.springframework.ai.openai.OpenAiFunctionCallbackWrapper;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.*;
import java.util.stream.Collectors;

@SpringBootApplication
public class BankingAssistantApplication {

    public static void main(String[] args) {
        SpringApplication.run(BankingAssistantApplication.class, args);
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowCredentials(true);
        config.addAllowedOrigin("*");
        config.addAllowedHeader("*");
        config.addAllowedMethod("*");
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}

@Configuration
class OpenAiConfig {
    
    @Bean
    public OpenAiProperties openAiProperties() {
        OpenAiProperties properties = new OpenAiProperties();
        properties.setApiKey("your_openai_api_key"); // Replace with your actual API key
        properties.setModel("gpt-4-turbo");
        return properties;
    }
    
    @Bean
    public OpenAiApi openAiApi(OpenAiProperties properties) {
        return new OpenAiApi(properties.getApiKey());
    }
    
    @Bean
    public OpenAiChatClient openAiChatClient(OpenAiApi openAiApi, OpenAiProperties properties) {
        return new OpenAiChatClient(openAiApi, properties);
    }
}

@Service
class BankingService {
    private final RestTemplate restTemplate;
    private static final String SYSTEM_PROMPT = """
            You are an AI banking assistant. Answer user queries based on API functions.
            
            Available Functions:
            1. **get_balance(customerId)** - Fetches the user's bank balance.
            2. **get_spending(customerId, category)** - Fetches total spending in a category.
            3. **list_transactions(customerId, startDate, endDate)** - Retrieves transactions for a period.
            4. **find_nearest_atm()** - Finds the nearest ATM.
            5. **enroll_online_banking(customerId)** - Enrolls the customer for online banking.
            6. **get_account_details(customerId)** - Retrieves account details.
            
            Guidelines:
            - Answer in **natural, human-like language**.
            - Combine multiple function results when relevant.
            - If a question is unclear, ask for clarification.
            """;
    
    private final OpenAiChatClient openAiChatClient;
    
    public BankingService(RestTemplate restTemplate, OpenAiChatClient openAiChatClient) {
        this.restTemplate = restTemplate;
        this.openAiChatClient = openAiChatClient;
    }
    
    public String generateResponse(String userMessage, String customerId) {
        try {
            // Create the prompt with system and user messages
            Prompt prompt = new Prompt(
                List.of(
                    new SystemMessage(SYSTEM_PROMPT),
                    new UserMessage(userMessage)
                ),
                registerFunctions(customerId)
            );
            
            // Send the prompt to OpenAI and get the response
            String response = openAiChatClient.call(prompt).getResult().getOutput().getContent();
            return response;
            
        } catch (Exception e) {
            e.printStackTrace();
            return "Sorry, I couldn't process your request.";
        }
    }
    
    private List<OpenAiFunctionCallbackWrapper> registerFunctions(String customerId) {
        List<OpenAiFunctionCallbackWrapper> functions = new ArrayList<>();
        
        // Register get_balance function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("get_balance")
            .description("Fetches user balance")
            .parameter("customerId", String.class, "Customer ID")
            .function(params -> {
                try {
                    ResponseEntity<Map> response = restTemplate.getForEntity(
                        "http://localhost:5001/balance/" + customerId,
                        Map.class
                    );
                    return response.getBody();
                } catch (Exception e) {
                    return Map.of("error", "Could not fetch balance data.");
                }
            })
            .build());
            
        // Register get_spending function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("get_spending")
            .description("Fetches spending by category")
            .parameter("customerId", String.class, "Customer ID")
            .parameter("category", String.class, "Spending category")
            .function(params -> {
                try {
                    String category = (String) params.get("category");
                    ResponseEntity<List> response = restTemplate.exchange(
                        "http://localhost:5001/transactions/" + customerId,
                        org.springframework.http.HttpMethod.GET,
                        null,
                        List.class
                    );
                    
                    List<Map<String, Object>> transactions = response.getBody();
                    double total = transactions.stream()
                        .filter(t -> category.equals(t.get("category")))
                        .mapToDouble(t -> ((Number) t.get("amount")).doubleValue())
                        .sum();
                    
                    return Map.of("total", total);
                } catch (Exception e) {
                    return Map.of("error", "Could not fetch spending data.");
                }
            })
            .build());
            
        // Register list_transactions function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("list_transactions")
            .description("Retrieves transactions")
            .parameter("customerId", String.class, "Customer ID")
            .parameter("startDate", String.class, "Start date")
            .parameter("endDate", String.class, "End date")
            .function(params -> {
                try {
                    String startDate = (String) params.get("startDate");
                    String endDate = (String) params.get("endDate");
                    ResponseEntity<Map> response = restTemplate.getForEntity(
                        "http://localhost:5001/transactions/" + customerId + "?start=" + startDate + "&end=" + endDate,
                        Map.class
                    );
                    return response.getBody();
                } catch (Exception e) {
                    return Map.of("error", "Could not fetch transaction data.");
                }
            })
            .build());
            
        // Register find_nearest_atm function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("find_nearest_atm")
            .description("Finds nearby ATM")
            .function(params -> {
                try {
                    ResponseEntity<Map> response = restTemplate.getForEntity(
                        "http://localhost:5001/nearest-atm",
                        Map.class
                    );
                    return response.getBody();
                } catch (Exception e) {
                    return Map.of("error", "Could not find nearest ATM.");
                }
            })
            .build());
            
        // Register enroll_online_banking function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("enroll_online_banking")
            .description("Enrolls user for online banking")
            .parameter("customerId", String.class, "Customer ID")
            .function(params -> {
                try {
                    ResponseEntity<Map> response = restTemplate.postForEntity(
                        "http://localhost:5001/enroll/" + customerId,
                        null,
                        Map.class
                    );
                    return response.getBody();
                } catch (Exception e) {
                    return Map.of("error", "Could not enroll in online banking.");
                }
            })
            .build());
            
        // Register get_account_details function
        functions.add(OpenAiFunctionCallbackWrapper.builder()
            .name("get_account_details")
            .description("Retrieves account details")
            .parameter("customerId", String.class, "Customer ID")
            .function(params -> {
                try {
                    ResponseEntity<Map> response = restTemplate.getForEntity(
                        "http://localhost:5001/account/" + customerId,
                        Map.class
                    );
                    return response.getBody();
                } catch (Exception e) {
                    return Map.of("error", "Could not fetch account details.");
                }
            })
            .build());
            
        return functions;
    }
}

@RestController
class ChatController {
    
    private final BankingService bankingService;
    
    public ChatController(BankingService bankingService) {
        this.bankingService = bankingService;
    }
    
    @PostMapping("/chat")
    public Map<String, String> chat(@RequestBody ChatRequest request) {
        String customerId = request.getCustomerId();
        if (customerId == null || customerId.isEmpty()) {
            throw new IllegalArgumentException("Customer ID is required.");
        }
        
        String responseMessage = bankingService.generateResponse(request.getMessage(), customerId);
        Map<String, String> response = new HashMap<>();
        response.put("reply", responseMessage);
        return response;
    }
}

class ChatRequest {
    private String message;
    private String customerId;
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getCustomerId() {
        return customerId;
    }
    
    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }
}
