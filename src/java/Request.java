package ru.mirea.furniture;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Request {
    private final String id;
    private final String customerId;
    private final boolean confirmed;
    private final String agreedTotal;
    private final List<RequestLine> lines;
    private boolean cancelled;
    private String cancellationReason;

    public Request(
            String id,
            String customerId,
            boolean confirmed,
            String agreedTotal,
            List<RequestLine> lines,
            boolean cancelled,
            String cancellationReason) {
        this.id = id;
        this.customerId = customerId;
        this.confirmed = confirmed;
        this.agreedTotal = agreedTotal;
        this.lines = List.copyOf(lines);
        this.cancelled = cancelled;
        this.cancellationReason = cancellationReason;
    }

    public String id() {
        return id;
    }

    public String customerId() {
        return customerId;
    }

    public boolean confirmed() {
        return confirmed;
    }

    public String agreedTotal() {
        return agreedTotal;
    }

    public List<RequestLine> lines() {
        return lines;
    }

    public boolean cancelled() {
        return cancelled;
    }

    public String cancellationReason() {
        return cancellationReason;
    }

    public void cancel(String reason) {
        cancelled = true;
        cancellationReason = reason;
    }

    public String validate(Map<String, Customer> customers, Map<String, Product> products) {
        if (customerId == null || !customers.containsKey(customerId)) {
            return "Неизвестный покупатель";
        }
        if (lines.isEmpty()) {
            return "В заявке нет позиций";
        }
        for (RequestLine line : lines) {
            if (line.productId() == null || !products.containsKey(line.productId())) {
                return "Неизвестный артикул: "
                        + (line.productId() == null ? "None" : line.productId());
            }
            if (line.quantity() == null
                    || line.quantity().scale() > 0
                    || line.quantity().signum() <= 0) {
                return "Количество должно быть положительным целым числом";
            }
        }
        return null;
    }

    public List<RequestLine> mergedLines() {
        Map<String, BigDecimal> quantities = new LinkedHashMap<>();
        for (RequestLine line : lines) {
            quantities.merge(line.productId(), line.quantity(), BigDecimal::add);
        }
        List<RequestLine> merged = new ArrayList<>();
        quantities.forEach((product, count) -> merged.add(new RequestLine(product, count)));
        return List.copyOf(merged);
    }

    public BigDecimal calculateTotal(List<RequestLine> merged, Map<String, Product> products) {
        BigDecimal total = BigDecimal.ZERO;
        for (RequestLine line : merged) {
            total = total.add(products.get(line.productId()).price().multiply(line.quantity()));
        }
        return total.setScale(2, RoundingMode.HALF_EVEN);
    }
}
