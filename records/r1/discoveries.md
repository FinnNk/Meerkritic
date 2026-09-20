# Chronological discoveries

- Baseline is the exact open PR 17 head; the live checkout is separate and unchanged.
- Initial targeted commands omitted PYTHONPATH and could not import the application.
  The canonical command supplies it. Targeted retries used the same source path;
  all 8 workflow and 6 annotation-web tests passed. This was command setup, not an
  application failure; no dependency or test contract was weakened.
- Native screenshots at the original host width clipped the right edge. Full-page
  exports duplicated/clipped content and were rejected by visual inspection. At
  the 1000-pixel responsive width, native captures were complete; 960-pixel crops
  were inspected and replace the failed attempts. Raw failed captures remain here.
- First complete implementation verification found the existing failure-provenance
  test still expected normalisation-v2. The implemented prompt is intentionally v3
  because its meaning changed. Update this exact expected version to v3; preserve
  all failure-provenance assertions. Retain the original failed complete run.
