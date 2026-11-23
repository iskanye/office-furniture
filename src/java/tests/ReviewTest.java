import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public final class ReviewTest {
    private ReviewTest() {}

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> input() throws Exception {
        return (Map<String, Object>) Json.parse(Files.readString(Path.of("example.json")));
    }

    public static void main(String[] args) throws Exception {
        Map<String, Object> data = input();
        data.put("operation", "reserv");
        check("rejected".equals(Main.process(data).get("status")), "unknown operation rejected");
        data.put("operation", "");
        check("rejected".equals(Main.process(data).get("status")), "empty operation rejected");
        data.put("operation", null);
        check("rejected".equals(Main.process(data).get("status")), "null operation rejected");
        data.remove("operation");
        check(
                "reserved".equals(Main.process(data).get("status")),
                "omitted action defaults to reserve");
        data = input();
        @SuppressWarnings("unchecked")
        Map<String, Object> request = (Map<String, Object>) data.get("request");
        request.put("confirmed", false);
        Warehouse warehouse = Main.load(data);
        check(
                warehouse.reserveAll() instanceof OperationResult.AwaitingConfirmation,
                "warehouse checks confirmation");
        check(
                warehouse.reservations().size() == 1,
                "unconfirmed request leaves reservations unchanged");
        data = input();
        @SuppressWarnings("unchecked")
        Map<String, Object> invalidRequest = (Map<String, Object>) data.get("request");
        invalidRequest.put("customer_id", "unknown");
        check(
                "Неизвестный покупатель"
                        .equals(
                                ((OperationResult.Rejected)
                                                new ReserveOperation(Main.load(data)).apply())
                                        .reason()),
                "base operation translates reservation validation error");
        check(
                "Неверный номер заявки"
                        .equals(
                                ((OperationResult.Rejected)
                                                new CancelOperation(
                                                                Main.load(input()),
                                                                "unknown",
                                                                "Отказ")
                                                        .apply())
                                        .reason()),
                "base operation translates cancellation validation error");
        data = input();
        data.remove("request");
        check(
                "request: ожидается объект".equals(Main.process(data).get("reason")),
                "missing request explained");
        data = input();
        data.put("request", false);
        check("rejected".equals(Main.process(data).get("status")), "wrong request type rejected");
        data = input();
        @SuppressWarnings("unchecked")
        Map<String, Object> stock =
                (Map<String, Object>) ((java.util.List<?>) data.get("stocks")).getFirst();
        stock.remove("quantity");
        check(
                "quantity: ожидается неотрицательное целое число"
                        .equals(Main.process(data).get("reason")),
                "missing stock quantity explained");
        stock.put("quantity", "10");
        check(
                "rejected".equals(Main.process(data).get("status")),
                "wrong stock quantity type rejected");
        data = input();
        data.put("stocks", null);
        check("rejected".equals(Main.process(data).get("status")), "null collection rejected");
        check("rejected".equals(Main.process(null).get("status")), "null input rejected");
        System.out.println("OK: review regression tests");
    }
}
