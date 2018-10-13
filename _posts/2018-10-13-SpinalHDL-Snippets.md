---
layout: post
title:  "SpinalHDL Snippets"
date:   2018-10-13 22:00:00 -0700
categories: RTL
---

# Split Testbench into Functional Sections

* [Compile the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L30)

* [Create a test on the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L37)

* Kick off one particular test: ```sbt "test-only *.MyScalaUnitTest"```

