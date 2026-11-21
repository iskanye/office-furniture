import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public final class ReserveOperation extends AbstractOperation {
    public ReserveOperation(Warehouse warehouse) {
        super(warehouse);
    }

    @Override
    protected Map<String, Object> execute() {
        Warehouse w = warehouse();
        Request request = w.request();
        String error = request.validate(w.customers(), w.products());
        if (error != null) {
            return Operation.rejected(error);
        }
        List<RequestLine> lines = request.mergedLines();
        List<Map<String, Object>> shortages = w.checkAvailability(lines);
        if (!shortages.isEmpty()) {
            Map<String, Object> result = Operation.rejected("Недостаточно товара");
            result.put("shortages", shortages);
            return result;
        }
        String total = request.calculateTotal(lines, w.products()).toPlainString();
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
        return w.reserveAll(lines);
    }
}
