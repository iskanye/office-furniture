import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public final class StateTest {
    private StateTest() {}

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        Map<String, Object> input =
                (Map<String, Object>) Json.parse(Files.readString(Path.of("example.json")));
        Warehouse w = Main.load(input);
        Operation reserve = new ReserveOperation(w);
        check("reserved".equals(reserve.apply().get("status")), "reservation result");
        check(w.reservations().size() == 3, "all lines reserved");
        check("rejected".equals(reserve.apply().get("status")), "repeat rejected");
        check(w.reservations().size() == 3, "repeat does not add reservations");
        Operation cancel = new CancelOperation(w, "R1", " Отказ ");
        check(
                Integer.valueOf(2).equals(cancel.apply().get("released_reservations")),
                "release count");
        check(
                w.request().cancelled() && "Отказ".equals(w.request().cancellationReason()),
                "cancellation saved");
        check(
                w.reservations().stream().filter(Reservation::active).count() == 1,
                "other request untouched");
        check(w.stocks().get("T1").quantity().intValueExact() == 10, "physical stock unchanged");
        check("rejected".equals(cancel.apply().get("status")), "repeat cancel rejected");
        input = (Map<String, Object>) Json.parse(Files.readString(Path.of("example.json")));
        ((Map<String, Object>) ((List<?>) input.get("stocks")).get(1))
                .put("quantity", java.math.BigDecimal.ZERO);
        Warehouse shortWarehouse = Main.load(input);
        check(
                "rejected".equals(new ReserveOperation(shortWarehouse).apply().get("status")),
                "shortage rejected");
        check(shortWarehouse.reservations().size() == 1, "no partial reservation");
        try {
            w.reservations().clear();
            throw new AssertionError("mutable collection");
        } catch (UnsupportedOperationException expected) {
        }
        check(
                Json.parse(Json.stringify(Map.of("text", "a\n\"б")))
                        .equals(Map.of("text", "a\n\"б")),
                "JSON round trip");
        for (String malformed : List.of("01", "[1,]", "{x:1}", "true false", "1.", "1e")) {
            try {
                Json.parse(malformed);
                throw new AssertionError("bad JSON accepted: " + malformed);
            } catch (IllegalArgumentException expected) {
            }
        }
        System.out.println("OK: state transitions, atomic rejection, encapsulation and JSON");
    }
}
