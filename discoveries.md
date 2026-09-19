# Chronology and test dispositions

The initial clean baseline installation failed against host Temp ACLs. Changing Temp fixed the directory problem but left incomplete installed executable metadata; a locked offline reinstall restored the environment. `baseline-checks-reinstalled.log` passes 15 tests. Earlier failed logs are retained; they are not negative controls.

The selection milestone ebbc700 passed 26 tests; accounting milestone 4b5b919 passed 33. Journal/CLI milestone 75a4c95 retained the first integration result, including an outdated architecture edge assertion and an incorrectly constructed Yoyo migration fixture. These failed before the intended migration assertion. Formatting failures are also retained in the logs.

The architecture test now checks the actual SQLite owner (adapters.state); its snapshot/import obligation is retained. The migration fixture now uses the supported migration collection over a directory containing the original migration only. No test obligation was removed. The corrected suite passes 43 tests. During review of the expanded event subjects, deleting/renaming a dataset was found to need the old FK restriction; triggers and a negative control now retain that protection. Completed usage export now includes the actual inventory/policy/price snapshots as well as IDs, so a copied Parquet history remains interpretable.

The journal and CLI were developed together in the diary. They will be separated in semantic history: the journal checkpoint has complete persistence/transaction tests; export/CLI tests arrive with their implementation. The price-version test at the journal checkpoint establishes immutable price identity; its export assertion extends that same test in the next checkpoint. No later tests are run against earlier code as checkpoint evidence.

ADR-0005 is proposed despite implementation in the candidate: owner acceptance has not occurred. ADR-0001 remains accepted, and ADRs 0002–0004 remain implemented. No empirical model comparison was performed.
