import java.util.ArrayList;

public final class RiftHotSpotBaselineSmoke {
  static final class Event {
    final int timestamp;
    final int key;
    final long left;
    final long right;
    Event next;

    Event(int timestamp, int key, long left, long right) {
      this.timestamp = timestamp;
      this.key = key;
      this.left = left;
      this.right = right;
    }
  }

  static final class Bucket {
    Event head;
    Event tail;
    int count;

    void append(Event event) {
      if (tail == null) {
        head = event;
      } else {
        tail.next = event;
      }
      tail = event;
      count++;
    }

    long closeAndDrop() {
      long checksum = count;
      Event cur = head;
      while (cur != null) {
        checksum += cur.timestamp * 17L + cur.key * 31L + cur.left - cur.right;
        cur = cur.next;
      }
      head = null;
      tail = null;
      count = 0;
      return checksum;
    }
  }

  public static void main(String[] args) {
    int records = args.length > 0 ? Integer.parseInt(args[0]) : 1_000_000;
    int epochSize = args.length > 1 ? Integer.parseInt(args[1]) : 10_000;
    int activeTimestamps = args.length > 2 ? Integer.parseInt(args[2]) : 16;

    Bucket[] buckets = new Bucket[activeTimestamps];
    for (int i = 0; i < buckets.length; i++) {
      buckets[i] = new Bucket();
    }

    long checksum = 0L;
    long output = 0L;
    long start = System.nanoTime();

    for (int i = 0; i < records; i++) {
      int timestamp = (i / epochSize) % activeTimestamps;
      int key = i & 1023;
      long left = ((long) i * 1664525L + 1013904223L) & 0xffffL;
      long right = ((long) i * 22695477L + 1L) & 0xffffL;
      Event event = new Event(timestamp, key, left, right);
      buckets[timestamp].append(event);
      output++;

      if ((i + 1) % epochSize == 0) {
        int closing = ((i + 1) / epochSize) % activeTimestamps;
        checksum ^= buckets[closing].closeAndDrop();
      }
    }

    for (Bucket bucket : buckets) {
      checksum ^= bucket.closeAndDrop();
    }

    double elapsedMs = (System.nanoTime() - start) / 1_000_000.0;
    System.out.println("mode\trecords\tepoch_size\tactive_timestamps\telapsed_ms\tchecksum\toutput");
    System.out.printf(
        "heap-gc\t%d\t%d\t%d\t%.3f\t%d\t%d%n",
        records, epochSize, activeTimestamps, elapsedMs, checksum, output);
  }
}
