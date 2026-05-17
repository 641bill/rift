import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotConfigGateSmoke {
    public static void main(String[] args) {
        try {
            RiftRegion.open(1024);
            throw new AssertionError("unsupported VM configuration should fail");
        } catch (UnsupportedOperationException expected) {
            String message = expected.getMessage();
            if (message == null || !message.contains("Rift regions prototype currently requires")) {
                throw new AssertionError("unexpected gate message: " + message, expected);
            }
        }
        System.out.println("config-gate-ok");
    }
}
