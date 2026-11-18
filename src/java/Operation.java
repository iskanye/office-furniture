import java.util.*;
public interface Operation {
    Map<String, Object> apply();
    static Map<String, Object> rejected(String reason) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "rejected"); result.put("reason", reason); return result;
    }
}
