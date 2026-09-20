# Reconstruction correction

Final semantic inspection found a line-number-based header transplant in the
first encoding rebuild's P3 placed a second header over the selection link.
The final frozen tree was equal, and its HTTP smoke passed, but this intermediate
checkpoint's promise was incomplete. The original candidate and check records
remain retained. Reassembly now matches the header element rather than assuming
the same line number in different versions. This restores the already-frozen
content at its intended proposition; there is no new implementation change.
P3-P5 have new identities and require fresh checkpoint evidence.
