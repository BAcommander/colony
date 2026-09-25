# Basalt v4 — redistribute motion by depth

User feedback: middle-right smoke is now too much; far distance and top of shot still appear still. Reduce middle-ground gust opacity from0.48 to0.18, height scale from1.6 to0.85, and existing near-haze opacity by35%. Keep travel so what remains still moves.

Add a separate terrain-masked far-haze layer in the distant valley left of the main mesa and across the foothills below it. Exclude the tall spire, distant outcrop and habitat rooflines. Use shallow warm-grey density flowing right, not a large opaque fog bank. This is independent of the middle-right dust.

Extend source-cloud-detail motion from the narrow band above the mesa into the upper sky. Protect the moon with an exclusion mask. Remove the moon from the texture-only source before advection so translated samples cannot create ghost moons. Preserve the original moon pixels and source outside the effect masks. Keep the sunset gradient, architecture and camera fixed.

Produce a20-second review loop at720p and4K. Inspect temporal samples, source masks and decoded seam. Preserve v3 and provide a v3/v4 comparison. Do not rebuild a20-minute file during this balance-review pass; deliver the short loop so the distribution can be judged first. Record user artistic approval separately from technical tests.
