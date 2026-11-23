import java.util.List;

public sealed interface OperationResult {
    record Rejected(String reason, List<Shortage> shortages, String total)
            implements OperationResult {
        public Rejected {
            shortages = List.copyOf(shortages);
        }

        public Rejected(String reason) {
            this(reason, List.of(), null);
        }
    }

    record AwaitingConfirmation(String total) implements OperationResult {}

    record Reserved(String requestId, String total) implements OperationResult {}

    record Cancelled(String requestId, String reason, int releasedReservations)
            implements OperationResult {}
}
