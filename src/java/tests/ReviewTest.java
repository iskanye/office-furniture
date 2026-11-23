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
                "awaiting_confirmation".equals(warehouse.reserveAll().get("status")),
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
                        .equals(new ReserveOperation(Main.load(data)).apply().get("reason")),
                "base operation translates reservation validation error");
        check(
                "Неверный номер заявки"
                        .equals(
                                new CancelOperation(Main.load(input()), "unknown", "Отказ")
                                        .apply()
                                        .get("reason")),
                "base operation translates cancellation validation error");
        System.out.println("OK: review regression tests");
    }
}
