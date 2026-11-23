package ru.mirea.furniture;

import java.math.BigDecimal;
import java.util.ArrayList;
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

    public List<Shortage> checkAvailability(List<RequestLine> lines) {
        List<Shortage> shortages = new ArrayList<>();
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
                shortages.add(new Shortage(line.productId(), line.quantity().subtract(available)));
            }
        }
        return shortages;
    }

    public boolean hasReservation() {
        return reservations.stream()
                .anyMatch(r -> r.active() && Objects.equals(r.requestId(), request.id()));
    }

    public OperationResult reserveAll() {
        String error = request.validate(customers, products);
        if (error != null) {
            throw new IllegalArgumentException(error);
        }
        List<RequestLine> lines = request.mergedLines();
        List<Shortage> shortages = checkAvailability(lines);
        if (!shortages.isEmpty()) {
            return new OperationResult.Rejected("Недостаточно товара", shortages, null);
        }
        String total = request.calculateTotal(lines, products).toPlainString();
        if (!request.confirmed()) {
            return new OperationResult.AwaitingConfirmation(total);
        }
        if (!Objects.equals(request.agreedTotal(), total)) {
            return new OperationResult.Rejected("Согласованная цена изменилась", List.of(), total);
        }
        if (request.cancelled()) {
            return new OperationResult.Rejected("Заказ отменён");
        }
        if (hasReservation()) {
            return new OperationResult.Rejected("Заявка уже зарезервирована");
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
        return new OperationResult.Reserved(request.id(), total);
    }

    public OperationResult cancel(String requestId, String reason) {
        if (!Objects.equals(requestId, request.id())) {
            throw new IllegalArgumentException("Неверный номер заявки");
        }
        if (reason == null || reason.strip().isEmpty()) {
            throw new IllegalArgumentException("Укажите причину отмены");
        }
        if (request.cancelled()) {
            return new OperationResult.Rejected("Заказ уже отменён");
        }
        if (!hasReservation()) {
            return new OperationResult.Rejected("У заказа нет активного резерва");
        }
        int released = 0;
        for (Reservation r : reservations) {
            if (r.active() && Objects.equals(r.requestId(), request.id())) {
                r.release();
                released++;
            }
        }
        request.cancel(reason.strip());
        return new OperationResult.Cancelled(request.id(), request.cancellationReason(), released);
    }
}
