# Screenshots that help readers act

Use a screenshot to orient readers, locate a control or recognise a meaningful result. Keep steps, commands and essential explanations in text. A screenshot illustrates a visible state; it does not prove the underlying behaviour works.

## Select and capture

- Prefer a few useful views to an image for every click. A README often benefits from one overview; a PR may need one illustration or a before/after pair. These are choices, not quotas. Reuse assets where the same view serves several guides.
- Capture the actual application with shareable demonstration data in a separate environment. Label synthetic examples and manually prepared outputs. Do not manufacture real user decisions or run costly services merely to furnish an illustration; use permitted fixtures where practical.
- Choose an overview for orientation or a focused panel for a particular action. Crop case by case, retaining the heading, labels and enough context to understand the view. Reuse a small set of widths where practical; let height follow the content. Keep text legible at the document's normal display size.
- Preserve the interface faithfully. Do not redraw controls, alter displayed results or use generated illustrations as application screenshots. Exclude secrets, private data, personal browser chrome and irrelevant desktop content at capture time. If redaction is necessary, make it explicit and record it.
- Follow the project's asset location and format conventions. Use descriptive filenames and suitably sized images. Prefer repository-relative links in documents and immutable revision URLs in PR descriptions when the host supports them.
- Add useful alt text and a short caption describing the relevant state or action. They should not merely repeat the filename. Keep the instructions usable without seeing the image.

## Retain enough to reproduce

Keep concise capture notes with the maintained assets or their project-owned record:

| Record | Purpose |
| --- | --- |
| Application version/revision and capture date | Identify the interface shown |
| Fixture, setup and route | Recreate the visible state without private data |
| Browser, viewport and relevant appearance | Explain layout differences |
| Scroll position, crop and any redaction | Explain the exact framing and transformations |
| Reproducibility limits | Identify varying IDs, timestamps or unavailable dependencies |

A small deterministic fixture may make recapture easier. Keep sensitive or large runtime data outside source control according to project policy. Image hashes can help an existing evidence workflow; do not introduce one solely for a decorative image.

## Verify and maintain

Before publication, inspect the image at its intended display size and in the rendered document when that view is available. Check legibility, links, matching caption/state and whether necessary controls have been cropped out. If a view cannot be inspected, record the limit rather than claiming it passed or bypassing access controls.

Review affected images when UI labels, layout or workflows change. Recapture or remove misleading images; unrelated changes do not require recapture. Preserve historical evidence and imported originals rather than rewriting them as current guides.
