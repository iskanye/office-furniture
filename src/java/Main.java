package ru.mirea.furniture;

import java.io.IOException;
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
    private static Map<String, Object> object(Object value, String name) {
        if (!(value instanceof Map<?, ?> map)
                || map.keySet().stream().anyMatch(key -> !(key instanceof String))) {
            throw new IllegalArgumentException(name + ": ожидается объект");
        }
        return (Map<String, Object>) value;
    }

    @SuppressWarnings("unchecked")
    private static List<Object> list(Map<String, Object> value, String key) {
        Object items = value.getOrDefault(key, List.of());
        if (!(items instanceof List<?>)) {
            throw new IllegalArgumentException(key + ": ожидается массив");
        }
        return (List<Object>) items;
    }

    private static String text(Map<String, Object> value, String key) {
        Object item = value.get(key);
        return item instanceof String ? (String) item : null;
    }

    private static BigDecimal number(Map<String, Object> value, String key) {
        Object item = value.get(key);
        return item instanceof BigDecimal ? (BigDecimal) item : null;
    }

    private static String requiredText(Map<String, Object> value, String key) {
        String result = text(value, key);
        if (result == null || result.isBlank()) {
            throw new IllegalArgumentException(key + ": ожидается непустая строка");
        }
        return result;
    }

    private static BigDecimal requiredQuantity(Map<String, Object> value) {
        BigDecimal result = number(value, "quantity");
        if (result == null || result.scale() > 0 || result.signum() < 0) {
            throw new IllegalArgumentException("quantity: ожидается неотрицательное целое число");
        }
        return result;
    }

    private static BigDecimal price(Map<String, Object> value) {
        try {
            BigDecimal result = new BigDecimal(requiredText(value, "price"));
            if (result.signum() < 0) {
                throw new NumberFormatException();
            }
            return result;
        } catch (NumberFormatException error) {
            throw new IllegalArgumentException("price: ожидается строка с неотрицательной ценой");
        }
    }

    public static Warehouse load(Map<String, Object> data) {
        Map<String, Customer> customers = new LinkedHashMap<>();
        for (Object item : list(data, "customers")) {
            Map<String, Object> v = object(item, "Элемент массива");
            customers.put(requiredText(v, "id"), new Customer(text(v, "id"), text(v, "name")));
        }
        Map<String, Product> products = new LinkedHashMap<>();
        for (Object item : list(data, "products")) {
            Map<String, Object> v = object(item, "Элемент массива");
            products.put(
                    requiredText(v, "id"), new Product(text(v, "id"), text(v, "name"), price(v)));
        }
        Map<String, Stock> stocks = new LinkedHashMap<>();
        for (Object item : list(data, "stocks")) {
            Map<String, Object> v = object(item, "Элемент массива");
            stocks.put(
                    requiredText(v, "product_id"),
                    new Stock(text(v, "product_id"), requiredQuantity(v)));
        }
        List<Reservation> reservations = new ArrayList<>();
        for (Object item : list(data, "reservations")) {
            Map<String, Object> v = object(item, "Элемент массива");
            reservations.add(
                    new Reservation(
                            text(v, "id"),
                            text(v, "request_id"),
                            requiredText(v, "product_id"),
                            requiredQuantity(v),
                            Boolean.TRUE.equals(v.get("active"))));
        }
        Map<String, Object> r = object(data.get("request"), "request");
        List<RequestLine> lines = new ArrayList<>();
        for (Object item : list(r, "lines")) {
            Map<String, Object> v = object(item, "Элемент массива");
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
        try {
            return processValidated(object(data, "Входные данные"));
        } catch (IllegalArgumentException error) {
            return ResultJson.toJson(new OperationResult.Rejected(error.getMessage()));
        }
    }

    private static Map<String, Object> processValidated(Map<String, Object> data) {
        Object action = data.getOrDefault("operation", "reserve");
        if (!"reserve".equals(action) && !"cancel".equals(action)) {
            return ResultJson.toJson(
                    new OperationResult.Rejected("Неизвестная операция: " + action));
        }
        Warehouse warehouse = load(data);
        Operation operation;
        if ("cancel".equals(data.get("operation"))) {
            Map<String, Object> cancellation =
                    object(data.getOrDefault("cancellation", Map.of()), "cancellation");
            operation =
                    new CancelOperation(
                            warehouse,
                            text(cancellation, "request_id"),
                            text(cancellation, "reason"));
        } else {
            operation = new ReserveOperation(warehouse);
        }
        return ResultJson.toJson(operation.apply());
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Использование: java -cp out ru.mirea.furniture.Main example.json");
            System.exit(2);
        }
        Map<String, Object> result;
        try {
            Map<String, Object> data =
                    object(
                            Json.parse(Files.readString(Path.of(args[0]), StandardCharsets.UTF_8)),
                            "Входные данные");
            result = process(data);
        } catch (IOException error) {
            result =
                    ResultJson.toJson(
                            new OperationResult.Rejected("Не удалось прочитать входной файл"));
        } catch (IllegalArgumentException error) {
            result = ResultJson.toJson(new OperationResult.Rejected(error.getMessage()));
        }
        System.out.println(Json.stringify(result));
    }
}
