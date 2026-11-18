import java.math.BigDecimal;
import java.util.*;

/** Minimal JSON adapter; business logic does not depend on parsing. */
public final class Json {
    private final String source;
    private int offset;
    private Json(String source) { this.source = source; }
    public static Object parse(String text) {
        Json parser = new Json(text);
        Object value = parser.value(); parser.space();
        if (parser.offset != text.length()) throw parser.error("Лишние символы");
        return value;
    }
    private IllegalArgumentException error(String message) {
        return new IllegalArgumentException(message + " в позиции " + offset);
    }
    private void space() {
        while (offset < source.length() && " \r\n\t".indexOf(source.charAt(offset)) >= 0) offset++;
    }
    private boolean take(char ch) {
        space();
        if (offset < source.length() && source.charAt(offset) == ch) { offset++; return true; }
        return false;
    }
    private void expect(char ch) { if (!take(ch)) throw error("Ожидается " + ch); }
    private Object value() {
        space();
        if (offset >= source.length()) throw error("Ожидается значение");
        char ch = source.charAt(offset);
        if (ch == '"') return string();
        if (take('{')) {
            Map<String, Object> map = new LinkedHashMap<>();
            if (take('}')) return map;
            do { String key = string(); expect(':'); map.put(key, value()); } while (take(','));
            expect('}'); return map;
        }
        if (take('[')) {
            List<Object> list = new ArrayList<>();
            if (take(']')) return list;
            do { list.add(value()); } while (take(','));
            expect(']'); return list;
        }
        for (String literal : List.of("true", "false", "null")) {
            if (source.startsWith(literal, offset)) {
                offset += literal.length();
                return literal.equals("null") ? null : literal.equals("true");
            }
        }
        int start = offset;
        if (offset < source.length() && source.charAt(offset) == '-') offset++;
        if (offset >= source.length()) throw error("Ожидается число");
        if (source.charAt(offset) == '0') offset++;
        else {
            if (source.charAt(offset) < '1' || source.charAt(offset) > '9') throw error("Неверное число");
            digits();
        }
        boolean decimal = false;
        if (offset < source.length() && source.charAt(offset) == '.') {
            decimal = true; offset++; int before = offset; digits();
            if (before == offset) throw error("Ожидается дробная часть");
        }
        if (offset < source.length() && "eE".indexOf(source.charAt(offset)) >= 0) {
            decimal = true; offset++;
            if (offset < source.length() && "+-".indexOf(source.charAt(offset)) >= 0) offset++;
            int before = offset; digits();
            if (before == offset) throw error("Ожидается показатель степени");
        }
        BigDecimal number = new BigDecimal(source.substring(start, offset));
        // Preserve JSON integer versus float distinction used by the Python validator.
        return decimal && number.scale() <= 0 ? number.setScale(1) : number;
    }
    private void digits() {
        while (offset < source.length() && source.charAt(offset) >= '0' && source.charAt(offset) <= '9') offset++;
    }
    private String string() {
        expect('"'); StringBuilder result = new StringBuilder();
        while (offset < source.length()) {
            char ch = source.charAt(offset++);
            if (ch == '"') return result.toString();
            if (ch < 32) throw error("Управляющий символ в строке");
            if (ch != '\\') { result.append(ch); continue; }
            if (offset >= source.length()) throw error("Незавершённое экранирование");
            char escaped = source.charAt(offset++);
            switch (escaped) {
                case '"', '\\', '/' -> result.append(escaped);
                case 'b' -> result.append('\b');
                case 'f' -> result.append('\f');
                case 'n' -> result.append('\n');
                case 'r' -> result.append('\r');
                case 't' -> result.append('\t');
                case 'u' -> {
                    if (offset + 4 > source.length()) throw error("Неверный Unicode");
                    result.append((char) Integer.parseInt(source.substring(offset, offset + 4), 16)); offset += 4;
                }
                default -> throw error("Неверное экранирование");
            }
        }
        throw error("Незавершённая строка");
    }
    public static String stringify(Object value) {
        if (value == null) return "null";
        if (value instanceof String str) {
            StringBuilder out = new StringBuilder("\"");
            for (char ch : str.toCharArray()) {
                switch (ch) {
                    case '"' -> out.append("\\\"");
                    case '\\' -> out.append("\\\\");
                    case '\n' -> out.append("\\n");
                    case '\r' -> out.append("\\r");
                    case '\t' -> out.append("\\t");
                    default -> { if (ch < 32) out.append(String.format("\\u%04x", (int) ch)); else out.append(ch); }
                }
            }
            return out.append('"').toString();
        }
        if (value instanceof Map<?, ?> map) {
            StringJoiner out = new StringJoiner(", ", "{", "}");
            map.forEach((key, item) -> out.add(stringify(key.toString()) + ": " + stringify(item)));
            return out.toString();
        }
        if (value instanceof Iterable<?> list) {
            StringJoiner out = new StringJoiner(", ", "[", "]");
            list.forEach(item -> out.add(stringify(item))); return out.toString();
        }
        if (value instanceof BigDecimal number) return number.toPlainString();
        if (value instanceof Number || value instanceof Boolean) return value.toString();
        throw new IllegalArgumentException("Неподдерживаемое значение JSON");
    }
}
