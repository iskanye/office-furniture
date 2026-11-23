import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public final class Warehouse {
    private final Map<String, Customer> customers;
    private final Map<String, Product> products;
    private final Map<String, Stock> stocks;
    private final List<Reservation> reservations;
    private final Request request;

    public Warehouse(
            Map<String, Customer> customers,
            Map<String, Product> products,
            Map<String, Stock> stocks,
            List<Reservation> reservations,
            Request request) {
        this.customers = Map.copyOf(customers);
        this.products = Map.copyOf(products);
        this.stocks = Map.copyOf(stocks);
        this.reservations = new ArrayList<>(reservations);
        this.request = request;
    }

    public Map<String, Customer> customers() {
        return customers;
    }

    public Map<String, Product> products() {
        return products;
    }

    public Map<String, Stock> stocks() {
        return stocks;
    }

    public List<Reservation> reservations() {
        return List.copyOf(reservations);
    }

    public Request request() {
        return request;
    }

    public List<Map<String, Object>> checkAvailability(List<RequestLine> lines) {
        List<Map<String, Object>> shortages = new ArrayList<>();
        for (RequestLine line : lines) {
            BigDecimal reserved = BigDecimal.ZERO;
            for (Reservation reservation : reservations) {
                if (reservation.active() && reservation.productId().equals(line.productId())) {
                    reserved = reserved.add(reservation.quantity());
                }
            }
            Stock stock = stocks.get(line.productId());
            BigDecimal available =
                    (stock == null ? BigDecimal.ZERO : stock.quantity()).subtract(reserved);
            if (line.quantity().compareTo(available) > 0) {
                Map<String, Object> shortage = new LinkedHashMap<>();
                shortage.put("product_id", line.productId());
                shortage.put("missing", line.quantity().subtract(available));
                shortages.add(shortage);
            }
        }
        return shortages;
    }

    public boolean hasReservation() {
        return reservations.stream()
                .anyMatch(r -> r.active() && Objects.equals(r.requestId(), request.id()));
    }

    public Map<String, Object> reserveAll() {
        String error = request.validate(customers, products);
        if (error != null) {
            throw new IllegalArgumentException(error);
        }
        List<RequestLine> lines = request.mergedLines();
        List<Map<String, Object>> shortages = checkAvailability(lines);
        if (!shortages.isEmpty()) {
            Map<String, Object> result = Operation.rejected("Недостаточно товара");
            result.put("shortages", shortages);
            return result;
        }
        String total = request.calculateTotal(lines, products).toPlainString();
        if (!request.confirmed()) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("status", "awaiting_confirmation");
            result.put("total", total);
            return result;
        }
        if (!Objects.equals(request.agreedTotal(), total)) {
            Map<String, Object> result = Operation.rejected("Согласованная цена изменилась");
            result.put("total", total);
            return result;
        }
        if (request.cancelled()) {
            return Operation.rejected("Заказ отменён");
        }
        if (hasReservation()) {
            return Operation.rejected("Заявка уже зарезервирована");
        }
        for (RequestLine line : lines) {
            reservations.add(
                    new Reservation(
                            request.id() + ":" + line.productId(),
                            request.id(),
                            line.productId(),
                            line.quantity(),
                            true));
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "reserved");
        result.put("request_id", request.id());
        result.put("total", total);
        return result;
    }

    public Map<String, Object> cancel(String requestId, String reason) {
        if (!Objects.equals(requestId, request.id())) {
            throw new IllegalArgumentException("Неверный номер заявки");
        }
        if (reason == null || reason.strip().isEmpty()) {
            throw new IllegalArgumentException("Укажите причину отмены");
        }
        if (request.cancelled()) {
            return Operation.rejected("Заказ уже отменён");
        }
        if (!hasReservation()) {
            return Operation.rejected("У заказа нет активного резерва");
        }
        int released = 0;
        for (Reservation r : reservations) {
            if (r.active() && Objects.equals(r.requestId(), request.id())) {
                r.release();
                released++;
            }
        }
        request.cancel(reason.strip());
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "cancelled");
        result.put("request_id", request.id());
        result.put("reason", request.cancellationReason());
        result.put("released_reservations", released);
        return result;
    }
}
