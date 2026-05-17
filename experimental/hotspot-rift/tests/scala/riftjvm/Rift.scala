package riftjvm

import jdk.internal.rift.RiftRegion

import scala.reflect.ClassTag

object Rift:
  final class Scope private[Rift] (val handle: Long):
    def current: Boolean =
      RiftRegion.current() == handle

    def stats: Array[Long] =
      RiftRegion.stats(handle)

    def verifyLive[A <: AnyRef](value: A): A =
      RiftRegion.verifyLive(value)
      value

  final class HeapRoot[A <: AnyRef] private[Rift] (private[Rift] val handle: Long):
    def rawHandle: Long = handle

  def register[A <: AnyRef](using tag: ClassTag[A]): Unit =
    RiftRegion.registerEligible(tag.runtimeClass)

  def epoch[A](capacity: Long)(body: Scope => A): A =
    val handle = RiftRegion.open(capacity)
    RiftRegion.enter(handle)
    try body(Scope(handle))
    finally RiftRegion.close(handle)

  def heapRoot[A <: AnyRef](value: A): HeapRoot[A] =
    HeapRoot[A](RiftRegion.createHeapRoot(value))

  def resolve[A <: AnyRef](root: HeapRoot[A]): A =
    RiftRegion.resolveHeapRoot(root.handle).asInstanceOf[A]

  def release(root: HeapRoot[?]): Unit =
    RiftRegion.releaseHeapRoot(root.handle)
