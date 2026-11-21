import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Main {
    private Main() {}

    @SuppressWarnings("unchecked")
    private static Map<String, Object> object(Object value) {
        return (Map<String, Object>) value;
    }

    @SuppressWarnings("unchecked")
    private static List<Object> list(Map<String, Object> value, String key) {
        return (List<Object>) value.getOrDefault(key, List.of());
    }

    private static String text(Map<String, Object> value, String key) {
        Object item = value.get(key);
        return item instanceof String ? (String) item : null;
    }

    private static BigDecimal number(Map<String, Object> value, String key) {
        Object item = value.get(key);
        return item instanceof BigDecimal ? (BigDecimal) item : null;
    }

    public static Warehouse load(Map<String, Object> data) {
        Map<String, Customer> customers = new LinkedHashMap<>();
        for (Object item : list(data, "customers")) {
            Map<String, Object> v = object(item);
            customers.put(text(v, "id"), new Customer(text(v, "id"), text(v, "name")));
        }
        Map<String, Product> products = new LinkedHashMap<>();
        for (Object item : list(data, "products")) {
            Map<String, Object> v = object(item);
            products.put(
                    text(v, "id"),
                    new Product(text(v, "id"), text(v, "name"), new BigDecimal(text(v, "price"))));
        }
        Map<String, Stock> stocks = new LinkedHashMap<>();
        for (Object item : list(data, "stocks")) {
            Map<String, Object> v = object(item);
            stocks.put(
                    text(v, "product_id"), new Stock(text(v, "product_id"), number(v, "quantity")));
        }
        List<Reservation> reservations = new ArrayList<>();
        for (Object item : list(data, "reservations")) {
            Map<String, Object> v = object(item);
            reservations.add(
                    new Reservation(
                            text(v, "id"),
                            text(v, "request_id"),
                            text(v, "product_id"),
                            number(v, "quantity"),
                            Boolean.TRUE.equals(v.get("active"))));
        }
        Map<String, Object> r = object(data.get("request"));
        List<RequestLine> lines = new ArrayList<>();
        for (Object item : list(r, "lines")) {
            Map<String, Object> v = object(item);
            lines.add(new RequestLine(text(v, "product_id"), number(v, "quantity")));
        }
        Request request =
                new Request(
                        text(r, "id"),
                        text(r, "customer_id"),
                        Boolean.TRUE.equals(r.get("confirmed")),
                        text(r, "agreed_total"),
                        lines,
                        Boolean.TRUE.equals(r.get("cancelled")),
                        text(r, "cancellation_reason"));
        return new Warehouse(customers, products, stocks, reservations, request);
    }

    public static Map<String, Object> process(Map<String, Object> data) {
        Warehouse warehouse = load(data);
        Operation operation;
        if ("cancel".equals(data.get("operation"))) {
            Map<String, Object> cancellation = object(data.getOrDefault("cancellation", Map.of()));
            operation =
                    new CancelOperation(
                            warehouse,
                            text(cancellation, "request_id"),
                            text(cancellation, "reason"));
        } else {
            operation = new ReserveOperation(warehouse);
        }
        return operation.apply();
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.err.println("Использование: java -cp out Main example.json");
            System.exit(2);
        }
        Map<String, Object> data =
                object(Json.parse(Files.readString(Path.of(args[0]), StandardCharsets.UTF_8)));
        System.out.println(Json.stringify(process(data)));
    }
}
