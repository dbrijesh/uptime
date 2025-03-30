import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import org.springframework.context.annotation.Bean;
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

@RestController
class ChatController {

    private final RestTemplate restTemplate;
    private static final String OPENAI_API_KEY = "your_openai_api_key"; // Replace with your actual API key
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

    public ChatController(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @PostMapping("/chat")
    public Map<String, String> chat(@RequestBody ChatRequest request) {
        String customerId = request.getCustomerId();
        if (customerId == null || customerId.isEmpty()) {
            throw new IllegalArgumentException("Customer ID is required.");
        }

        String responseMessage = generateResponse(request.getMessage(), customerId);
        Map<String, String> response = new HashMap<>();
        response.put("reply", responseMessage);
        return response;
    }

    private String generateResponse(String userMessage, String customerId) {
        try {
            // Prepare OpenAI API request
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(OPENAI_API_KEY);

            List<Map<String, String>> messages = new ArrayList<>();
            messages.add(Map.of("role", "system", "content", SYSTEM_PROMPT));
            messages.add(Map.of("role", "user", "content", userMessage));

            List<Map<String, Object>> functions = new ArrayList<>();
            functions.add(createFunctionDefinition("get_balance", "Fetches user balance", 
                    Map.of("customerId", "string")));
            functions.add(createFunctionDefinition("get_spending", "Fetches spending by category", 
                    Map.of("customerId", "string", "category", "string")));
            functions.add(createFunctionDefinition("list_transactions", "Retrieves transactions", 
                    Map.of("customerId", "string", "startDate", "string", "endDate", "string")));
            functions.add(createFunctionDefinition("find_nearest_atm", "Finds nearby ATM", 
                    Collections.emptyMap()));
            functions.add(createFunctionDefinition("enroll_online_banking", "Enrolls user for online banking", 
                    Map.of("customerId", "string")));
            functions.add(createFunctionDefinition("get_account_details", "Retrieves account details", 
                    Map.of("customerId", "string")));

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", "gpt-4-turbo");
            requestBody.put("messages", messages);
            requestBody.put("functions", functions);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            ResponseEntity<Map> responseEntity = restTemplate.exchange(
                    "https://api.openai.com/v1/chat/completions",
                    HttpMethod.POST,
                    entity,
                    Map.class
            );

            Map responseBody = responseEntity.getBody();
            List<Map<String, Object>> functionResponses = processFunctionCalls(responseBody, customerId);
            
            // Extract the initial response content
            String finalResponse = extractContentFromResponse(responseBody);
            
            // Append function response information
            if (functionResponses != null && !functionResponses.isEmpty()) {
                for (Map<String, Object> functionResponse : functionResponses) {
                    String functionName = (String) functionResponse.get("function");
                    Map<String, Object> data = (Map<String, Object>) functionResponse.get("data");
                    
                    switch (functionName) {
                        case "get_balance":
                            finalResponse += "\nYour current balance is $" + data.get("balance") + ".";
                            break;
                        case "get_spending":
                            finalResponse += "\nYou've spent $" + data.get("total") + " in that category.";
                            break;
                        case "list_transactions":
                            finalResponse += "\nHere are your recent transactions: " + data.toString() + ".";
                            break;
                        case "find_nearest_atm":
                            finalResponse += "\nThe nearest ATM is at " + data.get("location") + ".";
                            break;
                        case "enroll_online_banking":
                            finalResponse += "\nYou are now enrolled in online banking!";
                            break;
                        case "get_account_details":
                            finalResponse += "\nHere are your account details: " + data.toString() + ".";
                            break;
                    }
                }
            }
            
            return finalResponse;
        } catch (Exception e) {
            e.printStackTrace();
            return "Sorry, I couldn't process your request.";
        }
    }

    private Map<String, Object> createFunctionDefinition(String name, String description, Map<String, String> parameters) {
        Map<String, Object> function = new HashMap<>();
        function.put("name", name);
        function.put("description", description);
        function.put("parameters", Map.of("customerId", "string"));
        return function;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> processFunctionCalls(Map responseBody, String customerId) {
        try {
            List<Map> choices = (List<Map>) responseBody.get("choices");
            if (choices == null || choices.isEmpty()) {
                return null;
            }
            
            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            if (message == null) {
                return null;
            }
            
            Object functionCall = message.get("function_call");
            if (functionCall == null) {
                return null;
            }
            
            List<Map<String, Object>> functionCalls = new ArrayList<>();
            if (functionCall instanceof Map) {
                functionCalls.add((Map<String, Object>) functionCall);
            } else if (functionCall instanceof List) {
                functionCalls = (List<Map<String, Object>>) functionCall;
            }
            
            List<Map<String, Object>> responses = new ArrayList<>();
            for (Map<String, Object> func : functionCalls) {
                String name = (String) func.get("name");
                String arguments = (String) func.get("arguments");
                
                Map<String, Object> args = parseJsonArguments(arguments);
                args.put("customerId", customerId);
                
                Map<String, Object> data = fetchFunctionData(name, args);
                responses.add(Map.of("function", name, "data", data));
            }
            
            return responses;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
    
    private Map<String, Object> parseJsonArguments(String json) {
        // Simple implementation - in production use a proper JSON parser
        if (json == null || json.isEmpty()) {
            return new HashMap<>();
        }
        // This is a simplified version - in a real app, use Jackson or Gson
        return new HashMap<>();
    }
    
    private String extractContentFromResponse(Map responseBody) {
        try {
            List<Map> choices = (List<Map>) responseBody.get("choices");
            if (choices != null && !choices.isEmpty()) {
                Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
                if (message != null) {
                    return (String) message.get("content");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "I'm not sure how to answer that.";
    }

    private Map<String, Object> fetchFunctionData(String functionName, Map<String, Object> args) {
        try {
            String customerId = (String) args.get("customerId");
            
            switch (functionName) {
                case "get_balance":
                    ResponseEntity<Map> balanceResponse = restTemplate.getForEntity(
                            "http://localhost:5001/balance/" + customerId,
                            Map.class
                    );
                    return balanceResponse.getBody();
                    
                case "get_spending":
                    String category = (String) args.get("category");
                    ResponseEntity<List> transactionsResponse = restTemplate.exchange(
                            "http://localhost:5001/transactions/" + customerId,
                            HttpMethod.GET,
                            null,
                            List.class
                    );
                    
                    List<Map<String, Object>> transactions = transactionsResponse.getBody();
                    double total = transactions.stream()
                            .filter(t -> category.equals(t.get("category")))
                            .mapToDouble(t -> ((Number) t.get("amount")).doubleValue())
                            .sum();
                    
                    return Map.of("total", total);
                    
                case "list_transactions":
                    String startDate = (String) args.get("startDate");
                    String endDate = (String) args.get("endDate");
                    ResponseEntity<Map> listTransactionsResponse = restTemplate.getForEntity(
                            "http://localhost:5001/transactions/" + customerId + "?start=" + startDate + "&end=" + endDate,
                            Map.class
                    );
                    return listTransactionsResponse.getBody();
                    
                case "find_nearest_atm":
                    ResponseEntity<Map> atmResponse = restTemplate.getForEntity(
                            "http://localhost:5001/nearest-atm",
                            Map.class
                    );
                    return atmResponse.getBody();
                    
                case "enroll_online_banking":
                    ResponseEntity<Map> enrollResponse = restTemplate.postForEntity(
                            "http://localhost:5001/enroll/" + customerId,
                            null,
                            Map.class
                    );
                    return enrollResponse.getBody();
                    
                case "get_account_details":
                    ResponseEntity<Map> accountResponse = restTemplate.getForEntity(
                            "http://localhost:5001/account/" + customerId,
                            Map.class
                    );
                    return accountResponse.getBody();
                    
                default:
                    return Map.of("error", "Function not implemented");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Could not fetch data for " + functionName);
        }
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
