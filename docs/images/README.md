# Reproduce the documentation screenshots

The screenshots show the real application with a small **synthetic demonstration**.
The comments, code, interpretations, decisions, vectors and rule were prepared for
illustration. No model was invoked and no human research judgement was collected.
The application's normal fixture labels remain visible where it provides them.

## Prepare a fresh demonstration

Use Python 3.12 and run these commands from the repository root. Choose a **new**
local directory outside every Git worktree; the script refuses an existing path.
It creates four source records, four prepared interpretations, one failed draft, three synthetic
decisions, a fixture selection, one group, one candidate and a saved review draft.

1. Install the locked dependencies:

   ```text
   uv sync --locked
   ```

2. Create the demonstration runtime:

   ```text
   uv run --locked python docs/images/create_demo.py --data-root ../extras/screenshot-demo
   ```

3. Serve it on a separate port:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/screenshot-demo serve --port 8006
   ```

4. Open `http://127.0.0.1:8006` and use the paths printed by the script or saved in
   `<data-root>/screenshot-routes.json`. Do not start a model server or worker.
5. For the guidance screenshot, enter **Documentation fixture** as the name and
   **Clarify the ownership-transfer exception.** as the instruction. Check the
   rule and its discussion message. Leave the form unsubmitted.
6. Capture the views below, crop to the relevant content and inspect the result
   in its guide. Stop the temporary web server when finished.

The fixture has repeatable content, but generated IDs, timestamps and derived
digests vary. Use the newly printed routes rather than copying IDs from an image.
The deliberately invalid source URL is a label for locally supplied bytes; the
script pre-populates the source and does not download from it. The rule's declared
author is **Documentation fixture**; it is not an assertion of human authorship.

## Capture record

Captured on **20 September 2026**, using application code at `da3e48c`, with no
application-source changes during capture. The fixture is [create_demo.py](create_demo.py)
in this documentation revision. The browser was the Codex in-app browser on Windows,
using its existing dark appearance, a reported 1280 × 720 CSS viewport and native
1265 × 712 pixel captures. Browser scaling can differ on another machine.

Only pixel crops were applied: no scaling, redaction, compositing or content edits.
Raw captures and runtime files remain outside Git. [captures.json](captures.json)
and [the correction captures](captures-draft-repair.json) record pixel crop rectangles, scroll positions, image dimensions and SHA-256 hashes.
Use the visible landmarks below when different browser scaling makes those exact
coordinates unsuitable. A crop must keep the relevant labels and controls readable.

| Asset | Route key | Type / pixels | Content to retain |
| --- | --- | --- | --- |
| [Source browser](source-browser.png) | `observations` | Overview, 1232 × 675 | Dataset title, synthetic label, comment/code pair and Normalise action |
| [Interpretation result](annotation-result.png) | `annotation` | Overview, 1232 × 535 | Proposed issue and quoted evidence |
| [Assessment controls](annotation-assessment.png) | `annotation` | Panel, 960 × 221 | Human assessment heading, explanation, notes, editor and all buttons |
| [Failed draft](failed-draft-assessment.png) | `failed_annotation` | Overview, 1232 × 635 | Failure explanation, original draft editor and Edit/Reject controls |
| [Saved selection](frozen-selection.png) | `selection` | Overview, 1232 × 605 | Fixture label, totals, queue action and complete first input card |
| [Discovery group](discovery-group.png) | `discovery` | Overview, 1232 × 514 | Result heading, fixture label, totals and complete representative card |
| [Rule definition](rule-definition.png) | `rule` | Panel, 960 × 391 | Title, fixture label, pending state, scope and exclusions |
| [Saved review draft](saved-review-draft.png) | `workspace` | Overview, 1232 × 482 | Saved status, pending rule, intent and separate Save/Apply controls |
| [Guidance selection](guidance-selection.png) | `guidance` | Overview, 1232 × 452 | Heading, selected rule/message and explicit submission button |

There are two crop widths: 1232 pixels for views containing wide cards or paired
columns, and 960 pixels for focused panels. Heights follow the content. Reuse these
assets across documents instead of making separate copies for each guide.

The source-browser image appears in the README and dataset guide. The assessment
panel is shared by the annotation and study-preparation guides. The study has no
group-rating interface yet; the discovery image must not be described as one.

## Maintain the images

- Follow the [screenshot guidance](../development/documentation-style.md#screenshots-that-help-readers-act).
- Recapture affected views when controls, labels or behaviour change. Update the
  image, crop/hash record, alt text and caption together.
- Review the image at the document's displayed width, with the original available
  for closer inspection. Crop surrounding navigation before shrinking text.
- In PRs, use an immutable image URL from the reviewed commit and link these notes.
  Keep routine validation evidence separate from the illustration.

The correction capture record supersedes the earlier result and assessment entries
in `captures.json`; the other original captures remain current. The failed-draft
image shows an unreviewed synthetic job. Browser verification used a separate
synthetic job and saved one correction; neither is research data.
