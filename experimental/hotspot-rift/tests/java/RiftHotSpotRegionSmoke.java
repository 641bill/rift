import java.util.Arrays;
import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotRegionSmoke {
    private static final int OPEN = 1;
    private static final int ACTIVE = 2;
    private static final int CAPACITY = 3;
    private static final int USED = 4;
    private static final int HIGH_WATER = 5;
    private static final int ENTERS = 7;
    private static final int LEAVES = 8;
    private static final int CLOSES = 9;
    private static final int RESETS = 10;
    private static final int RAW_ALLOCS = 11;

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("disabled")) {
            expectUnsupportedWhenDisabled();
        } else {
            exerciseEnabledLifecycle();
        }
    }

    private static void expectUnsupportedWhenDisabled() {
        try {
            RiftRegion.open(1024);
            throw new AssertionError("RiftRegion.open should require -XX:+UseRiftRegions");
        } catch (UnsupportedOperationException expected) {
            System.out.println("disabled-ok");
        }
    }

    private static void exerciseEnabledLifecycle() {
        long h = RiftRegion.open(1024);
        check(h != 0, "non-zero handle");
        check(RiftRegion.current() == 0, "no current before enter");

        RiftRegion.enter(h);
        check(RiftRegion.current() == h, "current after enter");
        long p1 = RiftRegion.allocateRaw(h, 24);
        long p2 = RiftRegion.allocateRaw(h, 17);
        check(p1 != 0 && p2 != 0 && p2 > p1, "raw bump allocation");

        long[] active = RiftRegion.stats(h);
        check(active[OPEN] == 1, "open before close: " + Arrays.toString(active));
        check(active[ACTIVE] == 1, "active before leave: " + Arrays.toString(active));
        check(active[CAPACITY] == 1024, "capacity: " + Arrays.toString(active));
        check(active[USED] == 48, "aligned used bytes: " + Arrays.toString(active));
        check(active[HIGH_WATER] == 48, "high water: " + Arrays.toString(active));
        check(active[ENTERS] == 1, "enter count: " + Arrays.toString(active));
        check(active[RAW_ALLOCS] == 2, "raw alloc count: " + Arrays.toString(active));

        expectIllegalState(() -> RiftRegion.open(64), "nested open");
        RiftRegion.leave(h);
        check(RiftRegion.current() == 0, "no current after leave");
        expectIllegalState(() -> RiftRegion.allocateRaw(h, 8), "inactive allocation");

        RiftRegion.enter(h);
        RiftRegion.close(h);
        check(RiftRegion.current() == 0, "no current after close");

        long[] closed = RiftRegion.stats(h);
        check(closed[OPEN] == 0, "closed open flag: " + Arrays.toString(closed));
        check(closed[ACTIVE] == 0, "closed active flag: " + Arrays.toString(closed));
        check(closed[USED] == 0, "closed used bytes: " + Arrays.toString(closed));
        check(closed[HIGH_WATER] == 48, "closed high water: " + Arrays.toString(closed));
        check(closed[ENTERS] == 2, "closed enter count: " + Arrays.toString(closed));
        check(closed[LEAVES] == 2, "closed leave count: " + Arrays.toString(closed));
        check(closed[CLOSES] == 1, "close count: " + Arrays.toString(closed));
        check(closed[RESETS] == 1, "reset count: " + Arrays.toString(closed));
        expectIllegalState(() -> RiftRegion.enter(h), "closed enter");
        expectIllegalState(() -> RiftRegion.close(h), "double close");

        final long[] callbackHandle = new long[1];
        RiftRegion.epoch(128, () -> {
            callbackHandle[0] = RiftRegion.current();
            RiftRegion.allocateRaw(callbackHandle[0], 32);
        });
        long[] epochClosed = RiftRegion.stats(callbackHandle[0]);
        check(epochClosed[CLOSES] == 1, "epoch close count: " + Arrays.toString(epochClosed));
        check(epochClosed[RESETS] == 1, "epoch reset count: " + Arrays.toString(epochClosed));

        System.out.println("enabled-ok");
    }

    private static void expectIllegalState(Runnable body, String label) {
        try {
            body.run();
            throw new AssertionError(label + " should fail");
        } catch (IllegalStateException expected) {
            // expected
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
