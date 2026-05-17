package riftjvm

object RiftJvmScalaSmoke:
  private final val ObjectAllocs = 12

  def main(args: Array[String]): Unit =
    Rift.register[ScalaPrimitiveRecord]
    Rift.register[ScalaPrimitiveRootRecord]
    expectIllegalArgument(Rift.register[ScalaReferenceRecord], "reference field eligibility")
    expectIllegalArgument(Rift.register[ScalaNonFinalRecord], "non-final eligibility")

    val checksum = Rift.epoch(4096) { scope =>
      val record = new ScalaPrimitiveRecord(7, 11L, 3.5d)
      scope.verifyLive(record)
      check(scope.current, "scope should be current")
      check(scope.stats(ObjectAllocs) == 1, "Scala primitive record should allocate in region")
      record.sum()
    }
    check(checksum == 21L, "Scala region constructor and field stores ran normally")

    val bridgeChecksum = Rift.epoch(4096) { scope =>
      var root: Rift.HeapRoot[ScalaMetadata] | Null = null
      try
        val localRoot = Rift.heapRoot(new ScalaMetadata(99))
        root = localRoot
        val record = new ScalaPrimitiveRootRecord(localRoot.rawHandle, 12)
        check(scope.stats(ObjectAllocs) == 1, "Scala bridge record should allocate in region")
        System.gc()
        val metadata = Rift.resolve(localRoot)
        check(metadata.x == 99, "Scala heap-root bridge should survive GC")
        record.tag() + metadata.x
      finally
        if root != null then Rift.release(root)
    }
    check(bridgeChecksum == 111, "Scala heap-root bridge checksum")

    println("scala-rift-ok")

  private def expectIllegalArgument(body: => Unit, label: String): Unit =
    try
      body
      throw AssertionError(s"$label should fail")
    catch
      case _: IllegalArgumentException => ()

  private def check(condition: Boolean, message: String): Unit =
    if !condition then throw AssertionError(message)

final class ScalaPrimitiveRecord(private val x: Int, private val y: Long, private val z: Double):
  def sum(): Long =
    x + y + z.toLong

final class ScalaPrimitiveRootRecord(private val root: Long, private val tag0: Int):
  def rootHandle(): Long = root
  def tag(): Int = tag0

final class ScalaReferenceRecord(private val value: Object)

class ScalaNonFinalRecord(private val x: Int)

final class ScalaMetadata(val x: Int)
