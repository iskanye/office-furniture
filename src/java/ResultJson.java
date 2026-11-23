package ru.mirea.furniture;

import java.util.LinkedHashMap;
import java.util.Map;

public final class ResultJson {
    private ResultJson() {}

    public static Map<String, Object> toJson(OperationResult result) {
        Map<String, Object> json = new LinkedHashMap<>();
        switch (result) {
            case OperationResult.Rejected rejected -> {
                json.put("status", "rejected");
                json.put("reason", rejected.reason());
                if (!rejected.shortages().isEmpty()) {
                    json.put(
                            "shortages",
                            rejected.shortages().stream()
                                    .map(s ->
                                            Map.<String, Object>of(
                                                    "product_id",
                                                    s.productId(),
                                                    "missing",
                                                    s.missing()))
                                    .toList());
                }
                if (rejected.total() != null) {
                    json.put("total", rejected.total());
                }
            }
            case OperationResult.AwaitingConfirmation awaiting -> {
                json.put("status", "awaiting_confirmation");
                json.put("total", awaiting.total());
            }
            case OperationResult.Reserved reserved -> {
                json.put("status", "reserved");
                json.put("request_id", reserved.requestId());
                json.put("total", reserved.total());
            }
            case OperationResult.Cancelled cancelled -> {
                json.put("status", "cancelled");
                json.put("request_id", cancelled.requestId());
                json.put("reason", cancelled.reason());
                json.put("released_reservations", cancelled.releasedReservations());
            }
        }
        return json;
    }
}
