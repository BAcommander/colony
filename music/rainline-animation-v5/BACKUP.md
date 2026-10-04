# Rainline backup

User requested commit and push on 2026-10-05. This backup includes Rainline revision history, source code, configuration, masks, reports and the latest 20-second v5 preview. Its exact-path ordinary-Git rule preserves the 42 MB video. The 60-second three-repeat review and other draft videos remain local and can be reproduced. Backup is separate from artistic acceptance.

`backup-manifest.json` records preview and dependency hashes. The five dependency snapshots preserve the exact bytes used in validation; on a fresh Windows checkout, compare the recorded SHA-256 values before rendering. If a dependency's checkout line endings differ, restore its bytes from the corresponding snapshot to the recorded path. This does not change its Python behavior. Rainline Python/JSON files and snapshots use `-text` attributes to preserve their recorded bytes.

`remote-backup-verification.json`, when present locally, records verification after the push. Other sessions' working files were preserved; only Rainline portions of shared status files were staged.
